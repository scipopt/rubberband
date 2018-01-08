"""Methods to use for the communication with gitlab."""
import gzip
from tornado.options import options
from base64 import b64encode
from gitlab import Gitlab
import requests
import logging


def get_commit_data(project_id, git_hash):
    """
    Get commit information from the git hash.

    Parameters:
    project_id : int -- Id of project in gitlab.
    git_hash : str -- Githash of commit to look up.

    Return : commit object
    """
    if git_hash.endswith("-dirty"):
        git_hash = git_hash.rstrip("-dirty")

    client = Gitlab(options.gitlab_url, options.gitlab_private_token)
    commit = client.projects.get(project_id).commits.get(git_hash)

    return commit


def get_username(query_string):
    """
    Get the gitlab/internal username from a search term (full name, email, etc).

    Parameters:
    query_string : str -- String to search for.

    Return : str
    """
    client = Gitlab(options.gitlab_url, options.gitlab_private_token)
    authors = client.users.search(query_string)

    if len(authors) < 1:
        return query_string
    elif len(authors) > 1:
        return authors[0].username

    return authors[0].username
