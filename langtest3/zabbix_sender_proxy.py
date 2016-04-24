from twisted.internet import protocol, reactor, endpoints, defer, task
from StringIO import StringIO
import struct
from Queue import Queue
q = Queue()
import simplejson
import zabbix_request_handlers as zrh

class ZabbixSender(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.__payload_length = None

    def connectionMade(self):
        print "def connectionMade(self):"
        self.buffer = StringIO()

    def connectionLost(self, reason):
        print "def connectionLost(self, reason):",reason.__class__,dir(reason)

        reason.printTraceback()
        reason.printDetailedTraceback()
        print reason.getErrorMessage()

        self.buffer = None

    def unwrap_failures(self, err):
        """
        Takes nested failures and flattens the nodes into a list.
        The branches are discarded.
        """
        errs = []
        check_unwrap = [err]
        while len(check_unwrap) > 0:
            err = check_unwrap.pop()
            if hasattr(err.value, 'reasons'):
                errs.extend(err.value.reasons)
                check_unwrap.extend(err.value.reasons)
            else:
                errs.append(err)
        return errs

    def dataReceived(self, data):
        self.buffer.seek(0,2)
        self.buffer.write(data)
        self.__parseHeader()

    def getDoc(self):
        return self.__doc

    def parse(self, inst):
        request = self.__doc['request']
        zrh.getHandler(request)(self)


    def __parseHeader(self):
        self.buffer.seek(0,0)
        if not self.__payload_length and self.buffer.len >= 13:
            header= self.buffer.read(5)
            if 'ZBXD'== header[0:4] and '\1' == header[4]:
                self.__payload_length = struct.unpack('Q', self.buffer.read(8))[0]
        if self.__payload_length and self.buffer.len -13 == self.__payload_length :
            self.buffer.seek(13,0)
            jsonDoc= self.buffer.read()
            self.__doc = simplejson.loads(jsonDoc)
            d = defer.Deferred()
            reactor.callLater(0, d.callback, self)
            d.addCallback(self.parse)
            d.addCallback(self.__responseSuccess)
            d.addErrback(self.__responseError)


    def __responseSuccess(self, jsonresp):
        """resp = {
            "response": "success",
            "info": "Processed %(items_count)d Failed 0 Total %(items_count)d Seconds spent 0.002070" %dict(items_count=self.__items_count)
        }
        jsonresp = simplejson.dumps(resp)"""
        self.transport.write('ZBXD\1')
        self.transport.write(struct.pack('Q',len(jsonresp)))
        self.transport.write(jsonresp)
        self.transport.loseConnection()

    def __responseError(self, e):
        print e
        resp = {
            "response": "failure",
            "info": "Processed 0 Failed 0 Total 0 Seconds spent 0.002070"
        }
        self.transport.write(simplejson.dumps(resp))
        self.transport.loseConnection()

    def __parseError(self,e):
        print "def __parseError(self,e):"
        print e

        self.transport.stop()

class ZabbixSenderFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return ZabbixSender(self)


import history_syncer
history_syncer.start(q)

endpoints.serverFromString(reactor, "tcp:10051").listen(ZabbixSenderFactory())

try:
    reactor.run()
except KeyboardInterrupt:
    print "Interrupted by keyboard. Exiting."
    reactor.stop()