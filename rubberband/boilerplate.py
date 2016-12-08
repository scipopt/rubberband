import os
import logging

from tornado.options import define, options
from tornado.web import Application
from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections

from rubberband.routes import routes
from rubberband.handlers.fe import FourOhFourView

define("port", default=8888, help="Port to run tornado on.")
define("num_processes", default=1, help="Number of processes to run app in.")
define("prod_url", default="https://rubberband.example.com",
       help="The external url for this app.")
define("cookie_secret", default="RANDOMCOOKIESECRET", help="The cookie secret.")
define("api_token", default="SECUREAPITOKEN",
       help="The token that /api/ endpoints authorize against.")

define("gitlab_private_token", default="",
       help="Private token for gitlab user that Rubberband will make requests as.")
define("gitlab_url", default="", help="The gitlab url.")
define("gitlab_project_ids", default={},
       help="key-value pairs of gitlab project names and their IDs.")

define("elasticsearch_url", default="http://127.0.0.1:9200",
       help="The Elasticsearch url.")
define("elasticsearch_use_ssl", default=False, help="Use ssl? No for dev.")
define("elasticsearch_verify_certs", default=False, help="Verify certs? No for dev.")
define("elasticsearch_ca_certs", default=None, help="Path to CA certs.")

define("smtp_host", default="", help="The FQDN of the SMTP host.")
define("smtp_port", default="", help="The listening port of SMTP host.")
define("smtp_from_address", default="",
       help="The default `from` email address for emails that this app sends.")
define("smtp_username", default="", help="The username for SMTP authentication.")
define("smtp_password", default="", help="The password for SMTP authentication.")


def make_app(project_root):
    # Load options from environment
    loggr = logging.getLogger()
    loggr.setLevel(level=20)
    config = "/etc/rubberband/app.cfg"
    if os.path.isfile(config):
        logging.info("Loading additional configuration from /etc/rubberband/app.cfg")
        options.parse_config_file(config)
    else:
        logging.info("Using default config.")

    settings = {
        "debug": True if options.num_processes == 1 else False,
        "static_path": os.path.join(project_root, "static"),
        "template_path": os.path.join(project_root, "templates"),
        "cookie_secret": options.cookie_secret,
        "default_handler_class": FourOhFourView,
        "logger": loggr,
    }

    # Set up application
    app = Application(routes, **settings)

    logging.info("Setting up Elasticsearch connection.")
    conn = Elasticsearch([options.elasticsearch_url], use_ssl=options.elasticsearch_use_ssl,
                         verify_certs=options.elasticsearch_verify_certs,
                         ca_certs=options.elasticsearch_ca_certs)
    connections.add_connection("default", conn)

    if app.settings["debug"]:
        app.base_url = "http://127.0.0.1:{}".format(options.port)
    else:
        app.base_url = options.prod_url

    return app
