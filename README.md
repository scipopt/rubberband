# Rubberband

A flexible LP solver log file web view and analysis tool, backed by Elasticsearch.

- [Development](#Development)
  - [Installing Elasticsearch](#Installing-Elasticsearch)
  - [Setting up Rubberband](#Setting-up-Rubberband)
  - [Populating Elasticsearch](#Populating-Elasticsearch)
- [Testing](#Testing)
- [Deployment](#Deployment)
  - [Authentication](#Authentication)
  - [Web Server](#Web-Server)
  - [Process Management](#Process-Management)
- [Contributing](#Contributing)

## Development

This is a detailed description of how to set up Rubberband. If you're running Ubuntu or any of its Linux variants, simply clone this repository and run `bin/start_project.sh` for a faster setup. Otherwise, read the instructions below.

### Installing Elasticsearch

Java 8 is [required](https://www.elastic.co/guide/en/elasticsearch/reference/2.4/setup.html#jvm-version) to run Elasticsearch.
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

Now you're ready to install Elasticsearch. NOTE: Elasticsearch is rapidly developing software. Only 2.x versions of Elasticsearch are supported by Rubberband. Sadly, Elasticsearch is neither backwards- nor forwards-compatible.

```
wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb http://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list
sudo apt-get update && sudo apt-get install elasticsearch
```

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

Copy the configuration file in [config/app.cfg](config/app.cfg) into `/etc/rubberband/`, and edit the required variables.

### Populating Elasticsearch

Take a look at the control script in `bin/rubberband-ctl`. Running just that with no options will show the help. The main things you need to do for the first setup are create the index, and populate that index with data. This can be accomplished with the following two commands.

```
bin/rubberband-ctl create_index
bin/rubberband-ctl seed_database
```

## Testing

Install Rubberband in the virtual environment and run the test suite.

```
source venv/bin/activate
pip install -e .
py.test -v tests/
```

Tests will fail if elasticsearch is not running, or if the index is empty.

## Deployment

Rubberband currently requires a connection to an [Elasticsearch 2.x](https://www.elastic.co/guide/en/elasticsearch/reference/2.4/index.html) instance and (optionally) a [Gitlab](https://about.gitlab.com/) instance to run. To configure a Gitlab connection, edit the configuration variables in `/etc/rubberband/app.cfg` beginning with `gitlab_`. The Gitlab connection is used to look up information from the code base that your test set log is linked to. Examples of this type of information are git commit date and last committer.

### Authentication

There is no authentication built into Rubberband, though rubberband will authorize requests to the frontend using the `X-Forwarded-Email` header. Request made to the API require this header, as well as an `X-Api-Token` header. This is to say that authentication and setting the appropriate headers is the responsibility of the user/deployer. [oauth2_proxy](https://github.com/bitly/oauth2_proxy) is a convenient proxy that, when properly hooked up to an OAuth provider, will set this header for you.

### Web Server

Rubberband is meant to be deployed behind a production webserver, such as a [nginx](https://www.nginx.com/) or [apache](https://httpd.apache.org/).

### Process Management

[Supervisor](http://supervisord.org/) is a process monitor and manager, and great way to make sure Rubberband keeps running reliably in production.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
