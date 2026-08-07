"""Contains AnalyzeExternalView: hand a run/comparison off to LogAnalyzer."""

import json
import logging
import os
import uuid
import zipfile
from io import BytesIO

from tornado.web import HTTPError
from tornado.options import options
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from .base import BaseHandler
from .result import load_testsets
from rubberband.constants import EXPORT_FILE_TYPES

logger = logging.getLogger(__name__)


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
            'Content-Disposition: form-data; name="{}"'.format(name).encode(),
            b"",
            value.encode(),
        ]
    for name, filename, content_type, data in files:
        lines += [
            marker,
            'Content-Disposition: form-data; name="{}"; filename="{}"'.format(
                name, filename
            ).encode(),
            "Content-Type: {}".format(content_type).encode(),
            b"",
            data,
        ]
    lines += [("--" + boundary + "--").encode(), b""]
    body = b"\r\n".join(lines)
    return body, "multipart/form-data; boundary={}".format(boundary)


class AnalyzeExternalView(BaseHandler):
    """Bundle one or more TestSets and hand them to a LogAnalyzer instance."""

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
        public_base = (options.loganalyzer_public_url or options.loganalyzer_url).rstrip("/")
        if not base:
            raise HTTPError(404, reason="LogAnalyzer integration is not configured.")

        ts_ids = [t for t in testsets.split(",") if t]
        if not ts_ids:
            raise HTTPError(400, reason="No testsets given.")
        ts_list = load_testsets(ts_ids)

        # Build the same raw-log archive the download button produces. LogAnalyzer
        # detects the Rubberband filename convention and re-parses with its own
        # parser, so we hand over the raw logs, not Rubberband's parsed data.
        with BytesIO() as byteio:
            with zipfile.ZipFile(byteio, "w", zipfile.ZIP_DEFLATED) as archive:
                for ts in ts_list:
                    for ftype in EXPORT_FILE_TYPES:
                        try:
                            archive.writestr(
                                "{}/{}{}".format(
                                    ts.meta.id,
                                    os.path.splitext(ts.filename)[0],
                                    ftype,
                                ),
                                ts.raw(ftype),
                            )
                        except TypeError:
                            # ts.raw() returned None for a missing file type
                            pass
            zip_bytes = byteio.getvalue()

        logger.info(
            "Analyze handoff: base=%s zip_bytes=%d for %s",
            base, len(zip_bytes), ",".join(ts_ids),
        )

        label = (", ".join(ts.filename for ts in ts_list))[:120] or "Rubberband run"
        body, content_type = _encode_multipart(
            fields={"name": label, "description": "Imported from Rubberband"},
            files=[("files", "rubberband.zip", "application/zip", zip_bytes)],
        )

        request = HTTPRequest(
            url="{}/api/upload".format(base),
            method="POST",
            body=body,
            headers={"Content-Type": content_type},
            request_timeout=180,
        )
        try:
            response = await AsyncHTTPClient().fetch(request)
        except Exception as e:  # noqa: BLE001 - surface any transport/HTTP error
            logger.error("Analyze upload failed: %r", e)
            if getattr(e, "response", None) is not None:
                logger.error(
                    "Analyze upload response body: %s", e.response.body[:1000]
                )
            raise HTTPError(502, reason="Could not reach LogAnalyzer: {}".format(e))

        try:
            payload = json.loads(response.body)
        except ValueError:
            raise HTTPError(502, reason="Unexpected response from LogAnalyzer.")

        # A single run lands directly on its instances page. When LogAnalyzer
        # splits a Rubberband comparison into several runs (it groups by setting),
        # it returns {"multiple_runs": true, "runs": [...]} with no top-level
        # run_id. For a two-run comparison we hand the run ids straight to
        # LogAnalyzer's /compare route, which skips the dashboard, creates (or
        # reuses a cached) comparison and lands the user on the comparison page.
        # LogAnalyzer currently only renders two-run comparisons, so anything
        # larger falls back to the dashboard where the fresh runs appear.
        if payload.get("run_id"):
            self.redirect("{}/instances/{}".format(public_base, payload["run_id"]))
        elif payload.get("runs"):
            run_ids = [r["run_id"] for r in payload["runs"] if r.get("run_id")]
            if len(run_ids) == 2:
                self.redirect(
                    "{}/compare?runs={}".format(public_base, ",".join(run_ids))
                )
            else:
                self.redirect("{}/".format(public_base))
        else:
            raise HTTPError(502, reason="Unexpected response from LogAnalyzer.")
