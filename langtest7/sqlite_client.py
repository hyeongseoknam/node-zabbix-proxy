from twisted.internet import protocol, reactor, endpoints, defer, task
from twisted.enterprise import adbapi

class SQLiteClient(object):
    def __init__(self, host):
        self.__host = host
        self.__d = None


    def do(self):
        if not self.__d:
            self.__d = defer.Deferred()
            reactor.callLater(0, self.__d.callback, self)
            self.__d.addErrback(self.__handleError)

        self.__d.addCallback(self.parse)

    def parse(self):
        dbpool = adbapi.ConnectionPool("MySQLdb", db="test", user=user, password=password)


    def handleError(self):
        pass