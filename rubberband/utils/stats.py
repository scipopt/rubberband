"""Organize information import status."""
from collections import defaultdict


class ImportStats(object):
    """Class to hold information about import status."""

    def __init__(self, collection, basename):
        """
        Initialize an ImportStats object.

        Parameters
        ----------
        collection
            name for the object
        """
        self.collection = collection
        self.basename = basename
        self.fail = 0
        self.url = None
        self.status = None
        self.messages = defaultdict(list)

    def logMessage(self, identifier, msg):
        """
        Store (or log) message under field identifier.

        Parameters
        ----------
        identifier
            Identifier to store message under.
        msg : str
            Message to store.
        """
        self.messages[identifier].append(msg)

    def getMessages(self):
        """Return all messages in form of a defaultdict."""
        return self.messages

    def setUrl(self, url):
        """
        Store the url.

        Parameters
        ----------
        url : str
            Url to store
        """
        self.url = url

    def getUrl(self):
        """Return the url."""
        return self.url
