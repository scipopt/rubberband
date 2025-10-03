# starting from this file

import os
import tornado.ioloop
import tornado.httpserver
from datetime import date
import logging

from rubberband.boilerplate import make_app, options
from rubberband.constants import FILES_DIR
from rubberband.models import TestSet, Settings, File, Result

KB = 1024
MB = 1024 * KB
GB = 1024 * MB

ONE_DAY = 86400000  # in milliseconds


def delete_expired_documents():
    s = TestSet.search()
    s = s.filter("range", expirationdate={"lte": date.today()})
    response = s.execute()
    logging.info(f"Found {response.hits.total.value} expired testsets to delete.")
    for hit in response.hits:
        testset_id = hit.meta.id
        logging.info(f"Deleting testset {testset_id} associated data.")

        # Delete file documents
        file_search = File.search()
        file_search = file_search.filter("term", testset_id=testset_id)
        file_search_result = file_search.execute()
        files_to_delete = [f.filename for f in file_search_result.hits]
        file_search.delete()

        # Delete settings documents
        settings = Settings.get(hit.settings_id)
        settings.delete()
        default_settings = Settings.get(hit.default_settings_id)
        default_settings.delete()

        # Delete result documents
        for rid in hit.result_ids:
            result = Result.get(rid)
            result.delete()

        # Delete files from filesystem
        for f in files_to_delete:
            full_file_path = os.path.join(FILES_DIR, f)
            if os.path.exists(full_file_path):
                os.remove(full_file_path)
            else:
                logging.info(f"Unable to locate {full_file_path} for deletion.")

    # Delete all of the testset documents
    s.delete()

    logging.info("Finished deleting expired testsets.")


def main():
    project_root = os.path.join(os.path.dirname(__file__), "rubberband")
    app = make_app(project_root)

    # cron job to delete expired documents every day
    periodic_callback = tornado.ioloop.PeriodicCallback(
        delete_expired_documents, ONE_DAY
    )
    periodic_callback.start()

    # create an HTTPServer
    server = tornado.httpserver.HTTPServer(
        app, max_body_size=2 * GB, max_buffer_size=2 * GB
    )
    # bind it to a port specified in 'options'
    server.bind(options.port)
    # start server and ioloop as main event loop
    server.start(options.num_processes)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
