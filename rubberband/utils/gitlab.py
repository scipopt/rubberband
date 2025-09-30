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


def get_user_access_level(user_mail):
    """
    From email, find if user is either in the authenticated group or in the authenticated project.

    Parameters
    ----------
    user_email : str
        Email to search for.

    Returns
    -------
    int
        integer corresponding to gitlab access level (0: no, < 15: read, > 15: write, > 45: delete)
    """
    client = Gitlab(options.gitlab_url, options.gitlab_private_token)
    group_users = client.groups.get(options.gitlab_group_name).members.list(
        query=user_mail
    )
    principal_gitlab_project = next(iter(options.gitlab_project_ids.values()))
    project_users = client.projects.get(principal_gitlab_project).members.list(
        query=user_mail
    )
    min_access = 20
    # so something is wrong, return 0
    if (len(group_users) > 1 or len(project_users) > 1) or (
        len(group_users) == 0 and len(project_users) == 0
    ):
        return min_access
    if len(group_users + project_users) == 2:
        group_id = group_users[0].id
        project_id = project_users[0].id
        if not group_id == project_id:
            return min_access
        access_level = group_users[0].access_level
        project_access_level = project_users[0].access_level
        access_level = max(access_level, project_access_level)
    else:
        if len(group_users) == 1:
            access_level = group_users[0].access_level
        else:
            access_level = project_users[0].access_level
    return max(min_access, access_level)


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
    # here gitlab needs the "search" keyword, "query" will not work
    authors = client.users.list(search=query_string)

    if len(authors) < 1:
        return query_string
    elif len(authors) > 1:
        return authors[0].username

    return authors[0].username
