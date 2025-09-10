"""Methods to help with file io."""

from rubberband.constants import FILES_DIR


def write_file(filename, contents):
    """
    Save a file on the filesystem.

    Parameters
    ----------
    filename : string
        Filename of file to write to.
    contents : string
        Contents to write into file.
    """
    path = FILES_DIR + filename
    with open(path, "wb") as f:
        f.write(contents)

    return path
