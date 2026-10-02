"""Contains AnalyzeExternalView: hand a run/comparison off to LogAnalyzer."""

import asyncio
import json
import logging
import os
import re
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

from elasticsearch.dsl import Search
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.options import options
from tornado.web import HTTPError

from rubberband.constants import EXPORT_FILE_TYPES, RESULT_INDEX
from rubberband.models import TestSet

from .base import BaseHandler
from .result import load_testsets_files

logger = logging.getLogger(__name__)


def _result_coverage(ts_ids):
    """Count parsed results per testset in Elasticsearch (one cheap agg query).

    Returns a ``{testset_id: count}`` dict. An empty dict means ES is
    unreachable or nothing matched, which callers treat as "no results".
    """
    try:
        search = Search(index=RESULT_INDEX).query("terms", testset_id=ts_ids)
        search.aggs.bucket("per_ts", "terms", field="testset_id", size=len(ts_ids))
        resp = search.execute()
        return {b.key: b.doc_count for b in resp.aggregations.per_ts.buckets}
    except Exception:  # noqa: BLE001 - coverage is advisory
        return {}


def _es_run_groups(ts_ids):
    """Group testsets into runs by their filename's setting.

    Mirrors LogAnalyzer's rubberband convention
    ``check.<testset>.<binary_timestamp>.<queue>.<setting>-s<seed>.out``: testsets
    that share a setting (differ only by seed) belong to the same run. Returns
    ``{run_name: {"settings": ..., "testset_ids": [...]}}``.
    """
    def _load(ts_id):
        try:
            return TestSet.get(id=ts_id)
        except Exception:  # noqa: BLE001 - skip unreadable testsets
            return None

    if len(ts_ids) == 1:
        testsets = [_load(ts_ids[0])]
    else:
        with ThreadPoolExecutor(max_workers=min(len(ts_ids), 8)) as executor:
            testsets = list(executor.map(_load, ts_ids))

    groups = {}
    for ts in testsets:
        if ts is None:
            continue
        stem = os.path.splitext(ts.filename or "")[0]
        stem = re.sub(r"-s\d+$", "", stem)  # strip the -s<seed> suffix
        parts = stem.split(".")
        if len(parts) >= 5 and parts[0] == "check":
            # drop the timestamp from the binary part, like LogAnalyzer does
            binary = parts[2].rsplit("_", 1)[0] if "_" in parts[2] else parts[2]
            name = ".".join([parts[0], parts[1], binary, parts[3], parts[-1]])
        else:
            name = stem
        settings = parts[-1] if parts else ""
        groups.setdefault(
            name, {"settings": settings, "testset_ids": []}
        )["testset_ids"].append(ts.meta.id)
    return groups


def _encode_multipart(fields, files):
    """
    Encode form fields and files as multipart/form-data.

    Parameters
    ----------
    fields : dict
        name -> string value
    files : list of tuple
        (field_name, filename, content_type, bytes)

    Returns
    -------
    (bytes, str)
        the encoded body and the matching Content-Type header value
    """
    boundary = uuid.uuid4().hex
    marker = ("--" + boundary).encode()
    lines = []
    for name, value in fields.items():
        lines += [
            marker,
            f'Content-Disposition: form-data; name="{name}"'.encode(),
            b"",
            value.encode(),
        ]
    for name, filename, content_type, data in files:
        lines += [
            marker,
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode(),
            f"Content-Type: {content_type}".encode(),
            b"",
            data,
        ]
    lines += [("--" + boundary + "--").encode(), b""]
    body = b"\r\n".join(lines)
    return body, f"multipart/form-data; boundary={boundary}"


class AnalyzeExternalView(BaseHandler):
    """Bundle one or more TestSets and hand them to a LogAnalyzer instance."""

    async def _handoff_from_es(self, ts_ids):
        """Ask LogAnalyzer to import the testsets' already-parsed ES results.

        Returns True when the ES path was used (the caller should return), False
        when it should fall back to the raw-log upload.
        """
        base = options.loganalyzer_url.rstrip("/")
        public_base = (
            options.loganalyzer_public_url or options.loganalyzer_url
        ).rstrip("/")
        groups = await asyncio.to_thread(_es_run_groups, ts_ids)
        if not groups:
            return False
        runs = [
            {"name": name, "settings": g["settings"], "testset_ids": g["testset_ids"]}
            for name, g in groups.items()
        ]
        body = json.dumps(
            {
                "es_url": options.elasticsearch_url,
                "description": "Imported from Rubberband",
                "runs": runs,
            }
        ).encode()
        request = HTTPRequest(
            url=f"{base}/api/import-from-es",
            method="POST",
            body=body,
            headers={"Content-Type": "application/json"},
            request_timeout=120,
        )
        try:
            response = await AsyncHTTPClient().fetch(request)
            payload = json.loads(response.body)
        except Exception as e:  # noqa: BLE001 - fall back to the raw upload
            logger.warning("import-from-es failed (%r); falling back to raw upload", e)
            return False

        created = payload.get("runs") or []
        if not created or payload.get("skipped"):
            # no/partial parsed results - let the raw-log upload handle it
            return False
        run_ids = [r["run_id"] for r in created if r.get("run_id")]
        if not run_ids:
            return False
        logger.info("LogAnalyzer ES handoff: runs %s", run_ids)
        if len(run_ids) == 2:
            self.redirect(public_base + "/compare?runs=" + ",".join(run_ids))
        elif len(run_ids) == 1:
            self.redirect(f"{public_base}/instances/{run_ids[0]}")
        else:
            self.redirect(public_base + "/")
        return True

    async def get(self, testsets):
        """
        Zip the raw logs of the given testsets, upload them to LogAnalyzer and
        redirect the user to the resulting LogAnalyzer run page.

        Parameters
        ----------
        testsets : str
            comma-separated TestSet ids
        """
        # internal URL for the server-to-server upload; public URL for the
        # browser redirect (behind a reverse proxy these differ)
        base = options.loganalyzer_url.rstrip("/")
        public_base = (
            options.loganalyzer_public_url or options.loganalyzer_url
        ).rstrip("/")
        if not base:
            raise HTTPError(404, reason="LogAnalyzer integration is not configured.")

        ts_ids = [t for t in testsets.split(",") if t]
        if not ts_ids:
            raise HTTPError(400, reason="No testsets given.")

        # Fast path: if every testset has parsed results, hand those to LogAnalyzer directly.
        coverage = await asyncio.to_thread(_result_coverage, ts_ids)
        if (
            coverage
            and all(coverage.get(t, 0) > 0 for t in ts_ids)
            and await self._handoff_from_es(ts_ids)
        ):
            return

        # Only the raw logs are needed here, so use the loader that skips the result scan.
        ts_list = await asyncio.to_thread(load_testsets_files, ts_ids)

        # Build the raw-log archive the download button produces (LogAnalyzer re-parses it); ZIP_STORED since it's loopback.
        with BytesIO() as byteio:
            with zipfile.ZipFile(byteio, "w", zipfile.ZIP_STORED) as archive:
                for ts in ts_list:
                    for ftype in EXPORT_FILE_TYPES:
                        try:
                            archive.writestr(
                                f"{ts.meta.id}/{os.path.splitext(ts.filename)[0]}{ftype}",
                                ts.files[ftype.lstrip(".")].text,
                            )
                        except (AttributeError, KeyError):
                            # no file of this type for this testset
                            pass
            zip_bytes = byteio.getvalue()

        logger.info(
            "LogAnalyzer handoff: base=%s zip_bytes=%d for %s",
            base,
            len(zip_bytes),
            ",".join(ts_ids),
        )

        label = (", ".join(ts.filename for ts in ts_list))[:120] or "Rubberband run"
        body, content_type = _encode_multipart(
            fields={"name": label, "description": "Imported from Rubberband"},
            files=[("files", "rubberband.zip", "application/zip", zip_bytes)],
        )

        request = HTTPRequest(
            url=f"{base}/api/upload",
            method="POST",
            body=body,
            headers={"Content-Type": content_type},
            request_timeout=180,
        )
        try:
            response = await AsyncHTTPClient().fetch(request)
        except Exception as e:  # noqa: BLE001 - surface any transport/HTTP error
            logger.error("LogAnalyzer upload failed: %r", e)
            if getattr(e, "response", None) is not None:
                logger.error(
                    "LogAnalyzer upload response body: %s", e.response.body[:1000]
                )
            raise HTTPError(502, reason="Could not reach LogAnalyzer: " + e)

        try:
            payload = json.loads(response.body)
        except ValueError:
            raise HTTPError(502, reason="Unexpected response from LogAnalyzer.")

        # One run -> its instances page; two runs -> /compare; more -> the dashboard.
        if payload.get("run_id"):
            self.redirect("{}/instances/{}".format(public_base, payload["run_id"]))
        elif payload.get("runs"):
            run_ids = [r["run_id"] for r in payload["runs"] if r.get("run_id")]
            if len(run_ids) == 2:
                self.redirect(public_base + "/compare?runs=" + ",".join(run_ids))
            else:
                self.redirect(public_base + "/")
        else:
            raise HTTPError(502, reason="Unexpected response from LogAnalyzer.")
