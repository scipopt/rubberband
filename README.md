[![Build Status](https://travis-ci.org/xmunoz/rubberband.svg?branch=master)](https://travis-ci.org/xmunoz/rubberband)

# Rubberband

A flexible LP solver log file web view and analysis tool, backed by Elasticsearch.

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

This is a detailed description of how to set up Rubberband. If you're running Ubuntu or any of its Linux variants, simply clone this repository and run `bin/start_project.sh` for a faster setup. Otherwise, read the instructions below.

### Installing Elasticsearch

Java 8 is [required](https://www.elastic.co/guide/en/elasticsearch/reference/2.4/setup.html#jvm-version) to run Elasticsearch. For Ubuntu, you can install Java 8 this way.
```
sudo apt-get install python-software-properties
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer
```

To confirm that Java is properly installed, check the version.
```
$ java -version
java version "1.8.0_101"
Java(TM) SE Runtime Environment (build 1.8.0_101-b13)
Java HotSpot(TM) 64-Bit Server VM (build 25.101-b13, mixed mode)
```

Now you're ready to install Elasticsearch. NOTE: Elasticsearch is rapidly developing software. Only 2.x versions of Elasticsearch are supported by Rubberband. Sadly, Elasticsearch is neither backwards- nor forwards-compatible. Here are the most current instructions for installing Elasticsearch with `apt` on Ubuntu.

```
wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb http://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list
sudo apt-get update && sudo apt-get install elasticsearch
```

General instructions for installing Elasticsearch can be found in the [offical Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/2.4/_installation.html).

More information about running Elasticsearch as a service can be found [here](https://www.elastic.co/guide/en/elasticsearch/reference/2.4/setup-repositories.html), though this shouldn't be required for a development setup.

### Setting up Rubberband

Rubberband is built on [tornado](http://www.tornadoweb.org/en/stable/) and [ipet-reader](https://github.com/xmunoz/ipet-reader), a python3 compatible fork of [ipet](https://git.zib.de/integer/ipet). To get Rubberband running locally, make sure you first have Elasticsearch installed and running.

```
sudo service elasticsearch start
```

Now clone this repository and set up a virtual environment.

```
virtualenv -p python3 --no-site-packages venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

Copy the configuration file in [config/app.cfg](config/app.cfg) into `/etc/rubberband/`, and edit the required variables. Rubberband has some sane defaults already configured, so this step isn't strickly required. However, if you want to connect Rubberband to a Gitlab instance, or to an SMTP server to send email, you will need to edit `app.cfg`.

### Populating Elasticsearch

To populate the database or run unit tests, first install Rubberband inside the virtualenv.

```
pip install -e .
```

Now take a look at the control script in `bin/rubberband-ctl`. Running the control script with no options will show the help. For first-time, create the index, and populate that index with data. This can be accomplished with the following two commands.

```
bin/rubberband-ctl create_index
bin/rubberband-ctl populate_index
```

The second command will need a few minutes to finish. If the commands complete sucessfully, stdout should look something like this:

```
WARNING:elasticsearch:HEAD /solver-results [status:404 request:0.005s]
INFO:elasticsearch:PUT http://127.0.01:9200/solver-results [status:200 request:0.107s]
INFO:elasticsearch:HEAD http://127.0.01:9200/solver-results [status:200 request:0.002s]
INFO:elasticsearch:PUT http://127.0.01:9200/solver-results/_mapping/file [status:200 request:0.041s]
INFO:elasticsearch:HEAD http://127.0.01:9200/solver-results [status:200 request:0.002s]
INFO:elasticsearch:PUT http://127.0.01:9200/solver-results/_mapping/testset [status:200 request:0.019s]
INFO:root:Loading additional configuration from /etc/rubberband/app.cfg
INFO:root:Setting up Elasticsearch connection.
INFO:rubberband.utils.importer:debug opened a connection to elasticsearch with the ResultClient
INFO:rubberband.utils.importer:Found 4 files. Beginning to parse.
INFO:urllib3.connectionpool:Starting new HTTP connection (1): 127.0.01
INFO:elasticsearch:GET http://127.0.01:9200/solver-results/testset/_search [status:200 request:0.057s]
INFO:rubberband.utils.importer:Adding SoluFile.
...
```

### Start the server

Cross your fingers and run the following command.

```
python server.py
```

If everything went well, you should be able to open [http://127.0.0.1:8888/](http://127.0.0.1:8888/) in your browser and see something that looks like this.

![rubberband screenshot](https://raw.githubusercontent.com/xmunoz/rubberband/master/rubberband-screenshot.png)


## Testing

Run the test suite.

```
py.test -v tests/
```

Tests will fail if Elasticsearch is not running, or if the index is empty.

## Deployment

Rubberband currently requires a connection to an [Elasticsearch 2.x](https://www.elastic.co/guide/en/elasticsearch/reference/2.4/index.html) instance and (optionally) a [Gitlab](https://about.gitlab.com/) instance to run. To configure a Gitlab connection, edit the configuration variables in `/etc/rubberband/app.cfg` beginning with `gitlab_`. The Gitlab connection is used to look up information from the code base that your test set log is linked to. Examples of this type of information are git commit date and last committer. The visualize tab is disabled if no Gitlab connection information is provided.

### Authentication

There is no authentication built into Rubberband, though rubberband will authorize requests to the frontend using the `X-Forwarded-Email` header. Request made to the API require this header, as well as an `X-Api-Token` header. This is to say that authentication and setting the appropriate headers is the responsibility of the user/deployer. [oauth2_proxy](https://github.com/bitly/oauth2_proxy) is a convenient proxy that, when properly hooked up to an OAuth provider, will set this header for you.

### Web Server

Rubberband is meant to be deployed behind a production webserver, such as a [nginx](https://www.nginx.com/) or [apache](https://httpd.apache.org/). See [config/rubberband-oauth](config/rubberband-oauth) for a sample nginx configuration. This example shows an HTTPS deployment configured with [Let's Encrypt](and://letsencrypt.org/).

### Process Management

[Supervisor](http://supervisord.org/) is a process monitor and manager, and great way to make sure Rubberband keeps running reliably in production.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
