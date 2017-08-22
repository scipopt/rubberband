from collections import defaultdict


class ImportStats(object):
    def __init__(self, collection):
        self.collection = collection
        self.fail = 0
        self.url = None
        self.status = None
        self.messages = defaultdict(list)

    def logMessage(self, identifier, msg):
        self.messages[identifier].append(msg)

    def getMessages(self):
        return self.messages

    def setUrl(self, url):
        self.url = url

    def getUrl(self):
        return self.url
