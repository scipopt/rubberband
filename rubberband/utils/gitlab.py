import gzip
from tornado.options import options
from base64 import b64encode
from gitlab import Gitlab
import requests
import logging


def remove_file(project_id, path, message, ref="master"):
    '''
    Remove a file from gitlab.
    '''
    client = Gitlab(options.gitlab_url, options.gitlab_private_token)
    f = client.projects.get(project_id).files.get(file_path=path, ref=ref)
    f.delete(commit_message=message, branch_name=ref)


def fetch_file(project_id, path, gzipped=True, ref="master"):
    '''
    Fetch a file's contents from gitlab.
    '''
    client = Gitlab(options.gitlab_url, options.gitlab_private_token)
    response = client.projects.get(project_id).files.get(file_path=path, ref=ref)
    content = response.decode()

    if gzipped:
        return gzip.decompress(content)

    return content


def create_file(project_id, path, message, content, gzipped=True, ref="master"):
    '''
    Create a file in gitlab.
    '''
    if gzipped:
        content = gzip.compress(content)
        path = path + ".gz"

    # need to base64 encode the contents because gzip contains non-utf-8 chars
    content = b64encode(content)

    payload = {
        "file_path": path,
        "branch_name": ref,
        "content": content,
        "commit_message": message,
        "encoding": "base64"
    }

    # this doesn't work because of some weird json encoding error
    # client = Gitlab(options.gitlab_url, options.gitlab_private_token)
    # client.projects.get(project_id).files.create(payload)

    url = "{}/api/v3/projects/{}/repository/files".format(options.gitlab_url, project_id)
    r = requests.post(url, data=payload, headers={"private-token": options.gitlab_private_token})
    logging.info(r.text)
    r.raise_for_status()


def get_commit_data(project_id, git_hash):
    '''
    Get commit information from the git hash.
    '''
    if git_hash.endswith("-dirty"):
        git_hash = git_hash.rstrip("-dirty")

    client = Gitlab(options.gitlab_url, options.gitlab_private_token)
    commit = client.projects.get(project_id).commits.get(git_hash)

    return commit


def get_username(query_string):
    '''
    Get the gitlab/interal zib username from a search term (full name, email, etc)
    '''
    client = Gitlab(options.gitlab_url, options.gitlab_private_token)
    authors = client.users.search(query_string)

    if len(authors) < 1:
        return query_string
    elif len(authors) > 1:  # ref: bzfgamra
        return authors[-1].username

    return authors[0].username
