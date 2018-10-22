"""Functions to deal with hases."""
import hashlib


def read_in_chunks(file_object, chunk_size=1024):
    """
    Lazy function (generator) to read a file piece by piece.

    Default chunk size: 1k.
    borrowed from http://stackoverflow.com/a/519653

    Parameters
    ----------
    file_object : file object
        File to read in chunks.

    Keyword arguments:
    chunk_size : int
        size of chunks to read (default 1024)

    Yields
    ------
    datachunks
        requested data
    """
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def generate_sha256_hash(filepath):
    """
    Take a filepath and return a hex digest of a sha2 hash.

    Parameters
    ----------
    filepath : str
        Path to file.

    Returns
    -------
    str
        requested hash
    """
    sha_result = hashlib.sha256()

    try:
        file_object = open(filepath, "rb")
    except IOError:
        return None

    for chunk in read_in_chunks(file_object):
        sha_result.update(chunk)

    file_object.close()

    return sha_result.hexdigest()
