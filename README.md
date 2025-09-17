# Rubberband

A flexible web view and analysis platform for solver log files of mathematical optimization software, backed by Elasticsearch.

- [Development](#development)
  - [Install Elasticsearch](#install-elasticsearch)
  - [Set up Rubberband](#set-up-rubberband)
  - [Populate Elasticsearch](#populate-elasticsearch)
  - [Start the server](#start-the-server)
- [Testing](#testing)
- [Deployment](#deployment)
  - [Authentication](#authentication)
  - [Web Server](#web-server)
  - [Process Management](#process-management)
- [Contributing](#contributing)

## Development

This is a detailed description of how to set up Rubberband.

### Install system requirements

```
sudo apt install git curl libffi-dev libssl-dev libsqlite3-dev libbz2-dev libncurses-dev libreadline-dev liblzma-dev zlib1g-dev tk-dev libxml2-dev libxslt1-dev
```

### Installing Elasticsearch

Download the .deb package and install it manually. Elasticsearch [comes bundled](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/installing-elasticsearch#jvm-version) with the version of Java that it needs to run.

```
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-9.1.3-amd64.deb
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-9.1.3-amd64.deb.sha512
shasum -a 512 -c elasticsearch-9.1.3-amd64.deb.sha512
sudo dpkg -i elasticsearch-9.1.3-amd64.deb
```

This version of Elasticsearch comes with various security configurations enabled. For local development, you can turn all of these off. To do that, open up `/etc/elasticsearch/elasticsearch.yml` and change the following configuration options to `false`:
 - `xpack.security.enabled`
 - `xpack.security.enrollment.enabled`
 - `xpack.security.http.ssl.enabled`
 - `xpack.security.transport.ssl.enabled`

### Setting up Rubberband

Rubberband is built on [tornado](http://www.tornadoweb.org/en/stable/) and [IPET](https://github.com/stephenjmaher/ipet/tree/remove-gui), an interactive performance evaluation tool that comes with a parsing library for benchmark files. To get Rubberband running locally, make sure you first have Elasticsearch installed and running.

```
sudo service elasticsearch start
```

Now install [pyenv](https://github.com/pyenv/pyenv).

```
curl -fsSL https://pyenv.run | bash
```

Then clone this repository, install the correct python version and set up a virtual environment.

```
pyenv install
pyenv virtualenv venv
pyenv activate venv
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

The first install command will clone and install IPET from github, you don't need to do this manually.

For a deployed version of Rubberband copy the configuration file in [config/app.cfg](config/app.cfg) into `/etc/rubberband/`, and edit the required variables. Rubberband has some sane defaults already configured, so this step isn't strictly required. However, if you want to connect Rubberband to a Gitlab instance, or to an SMTP server to send email, you will need to edit `app.cfg`.
NOTE: If you install Rubberband as a developer version, you don't need to do this.

### Populating Elasticsearch

To populate the database or run unit tests, first install Rubberband inside the virtualenv.

```
python -m pip install .
```

Now take a look at the control script in `bin/rubberband-ctl`. Running the control script with no options will show the help. For first-time, create the indices, and populate the indices with data. This can be accomplished with the following two commands.

```
bin/rubberband-ctl create-indices
bin/rubberband-ctl populate-indices
```

The second command will need a few minutes to finish. If the commands complete sucessfully, stdout should look something like this:

```
...
16-09-2025 12:19:29 - 488 INFO  elastic_transport.transport POST http://127.0.0.1:9200/testset/_doc [status:201 duration:0.030s]
16-09-2025 12:19:29 - 500 INFO  elastic_transport.transport POST http://127.0.0.1:9200/settings/_doc [status:201 duration:0.005s]
16-09-2025 12:19:29 - 512 INFO  elastic_transport.transport POST http://127.0.0.1:9200/settings/_doc [status:201 duration:0.007s]
16-09-2025 12:19:29 - 521 INFO  elastic_transport.transport POST http://127.0.0.1:9200/testset/_update/4o1SU5kBKuV0IQ9c9FAz?if_primary_term=1&if_seq_no=15&refresh=false [status:200 duration:0.009s]
16-09-2025 12:19:29 - 529 INFO  elastic_transport.transport POST http://127.0.0.1:9200/result/_doc [status:201 duration:0.004s]
16-09-2025 12:19:29 - 537 INFO  elastic_transport.transport POST http://127.0.0.1:9200/result/_doc [status:201 duration:0.004s]
16-09-2025 12:19:29 - 548 INFO  elastic_transport.transport POST http://127.0.0.1:9200/result/_doc [status:201 duration:0.008s]
16-09-2025 12:19:29 - 556 INFO  elastic_transport.transport POST http://127.0.0.1:9200/result/_doc [status:201 duration:0.004s]
16-09-2025 12:19:29 - 563 INFO  elastic_transport.transport POST http://127.0.0.1:9200/result/_doc [status:201 duration:0.004s]
16-09-2025 12:19:29 - 571 INFO  elastic_transport.transport POST http://127.0.0.1:9200/result/_doc [status:201 duration:0.004s]
16-09-2025 12:19:29 - 580 INFO  elastic_transport.transport POST http://127.0.0.1:9200/result/_doc [status:201 duration:0.006s]
16-09-2025 12:19:29 - 584 INFO  elastic_transport.transport POST http://127.0.0.1:9200/testset/_update/4o1SU5kBKuV0IQ9c9FAz?if_primary_term=1&if_seq_no=16&refresh=false [status:200 duration:0.003s]
16-09-2025 12:19:29 - 584 INFO  rubberband.utils.importer Data for file /home/user/workspace/r/tests/data/check.IP_1s_1m.scip-3.2.1.linux.x86_64.gnu.dbg.cpx.opt-low.default.out was successfully imported and archived
16-09-2025 12:19:29 - 587 INFO  rubberband.utils.importer Backing up /home/user/workspace/r/tests/data/check.IP_1s_1m.scip-3.2.1.linux.x86_64.gnu.dbg.cpx.opt-low.default.out in Elasticsearch
16-09-2025 12:19:29 - 594 INFO  elastic_transport.transport POST http://127.0.0.1:9200/file/_doc [status:201 duration:0.006s]
16-09-2025 12:19:29 - 595 INFO  rubberband.utils.importer Backing up /home/user/workspace/r/tests/data/check.IP_1s_1m.scip-3.2.1.linux.x86_64.gnu.dbg.cpx.opt-low.default.set in Elasticsearch
16-09-2025 12:19:29 - 602 INFO  elastic_transport.transport POST http://127.0.0.1:9200/file/_doc [status:201 duration:0.005s]
16-09-2025 12:19:29 - 602 INFO  rubberband.utils.importer Backing up /home/user/workspace/r/tests/data/check.IP_1s_1m.scip-3.2.1.linux.x86_64.gnu.dbg.cpx.opt-low.default.meta in Elasticsearch
16-09-2025 12:19:29 - 608 INFO  elastic_transport.transport POST http://127.0.0.1:9200/file/_doc [status:201 duration:0.003s]
16-09-2025 12:19:29 - 609 INFO  rubberband.utils.importer Backing up /home/user/workspace/r/tests/data/check.IP_1s_1m.scip-3.2.1.linux.x86_64.gnu.dbg.cpx.opt-low.default.err in Elasticsearch
16-09-2025 12:19:29 - 614 INFO  elastic_transport.transport POST http://127.0.0.1:9200/file/_doc [status:201 duration:0.005s]
16-09-2025 12:19:29 - 615 INFO  rubberband.utils.importer /home/user/workspace/r/tests/data/check.IP_1s_1m.scip-3.2.1.linux.x86_64.gnu.dbg.cpx.opt-low.default.out file bundle backed up in Elasticsearch.
16-09-2025 12:19:29 - 615 INFO  rubberband.utils.importer Finished!
```

### Start the server

Cross your fingers and run the following command from your virtual environment.

```
python server.py
```

If everything went well, you should be able to open [http://127.0.0.1:8888/](http://127.0.0.1:8888/) in your browser and see something that looks like this.

![rubberband screenshot](https://raw.githubusercontent.com/xmunoz/rubberband/master/rubberband-screenshot.png)

## CI

Continuous integration is configured with [Github Actions](https://github.com/features/actions), and is run on every pull request. For more information about the CI workflow, please see [here](./.github/workflows/ci.yaml).

## Documentation

To build the documentation run the following commands from inside the virtualenvironment:

```
cd doc
make doc
```

Now you can view the documentation by opening `doc/build/html/index.html` in your favorite webbrowser.

## Testing

First, install Rubberband locally:

```
python -m pip install .
```

Then, run the test suite.

```
pytest
```

Tests will fail if Elasticsearch is not running, or if the indices are empty or if you didn't configure authentication correctly.

## Deployment

Rubberband currently requires a connection to an [Elasticsearch 9.x](https://www.elastic.co/docs/solutions/search/get-started) instance and (optionally) a [Gitlab](https://about.gitlab.com/) instance to run. To configure a Gitlab connection, edit the configuration variables in `/etc/rubberband/app.cfg` beginning with `gitlab_`. The Gitlab connection is used to look up information from the code base that your test set log is linked to. Examples of this type of information are git commit date and last committer. The visualize tab is disabled if no Gitlab connection information is provided.

### Authentication

There is no authentication built into Rubberband, though rubberband will authorize requests to the frontend using the `X-Forwarded-Email` header. Request made to the API require this header, as well as an `X-Api-Token` header. This is to say that authentication and setting the appropriate headers is the responsibility of the user/deployer. [oauth2_proxy](https://github.com/bitly/oauth2_proxy) is a convenient proxy that, when properly hooked up to an OAuth provider, will set this header for you.

### Web Server

Rubberband is meant to be deployed behind a production webserver, such as a [nginx](https://www.nginx.com/) or [apache](https://httpd.apache.org/). See [config/rubberband-oauth](config/rubberband-oauth) for a sample nginx configuration. This example shows an HTTPS deployment configured with [Let's Encrypt](and://letsencrypt.org/).

### Process Management

[Supervisor](http://supervisord.org/) is a process monitor and manager, and great way to make sure Rubberband keeps running reliably in production.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
