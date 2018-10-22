"""Methods to use for the communication with gitlab."""
from tornado.options import options
from gitlab import Gitlab


def get_commit_data(project_id, git_hash):
    """
    Get commit information from the git hash.

    Parameters
    ----------
    project_id : int
        Id of project in gitlab.
    git_hash : str
        Githash of commit to look up.

    Returns
    -------
    commit object
        requested commit
    """
    if git_hash.endswith("-dirty"):
        git_hash = git_hash.rstrip("-dirty")

    client = Gitlab(options.gitlab_url, options.gitlab_private_token)
    commit = client.projects.get(project_id).commits.get(git_hash)

    return commit


def get_username(query_string):
    """
    Get the gitlab/internal username from a search term (full name, email, etc).

    Parameters
    ----------
    query_string : str
        String to search for.

    Returns
    -------
    str
        username
    """
    client = Gitlab(options.gitlab_url, options.gitlab_private_token)
    authors = client.users.list(search=query_string)

    if len(authors) < 1:
        return query_string
    elif len(authors) > 1:
        return authors[0].username

    return authors[0].username
