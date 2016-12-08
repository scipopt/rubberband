from rubberband.constants import FILES_DIR


def write_file(filename, contents):
    '''
    Save a file on the filesystem.
    '''
    path = FILES_DIR + filename
    with open(path, "wb") as f:
        f.write(contents)

    return path
