from twisted.internet import protocol, reactor, endpoints, defer
from StringIO import StringIO
import struct
from Queue import Queue
q = Queue()
import simplejson

class ZabbixSender(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.__payload_length = None

    def connectionMade(self):
        self.buffer = StringIO()

    def connectionLost(self, reason):
        self.buffer = None

    def dataReceived(self, data):
        self.buffer.seek(0,2)
        self.buffer.write(data)
        self.parse()

    def parse(self):
        d = defer.Deferred()
        d.addCallback(self.__parseHeader)
        d.addErrback(self.__parseError)

    def __parseHeader(self):
        self.buffer.seek(0,0)
        if not self.__payload_length and self.buffer.length() >= 13:
            if 'ZBXD'== buffer.read(4) and '\0' == buffer.read(1):
                self.__payload_length = struct.unpack('Q', buffer.read(8))[0]
        if self.__payload_length and self.buffer.length() == self.__payload_length:
            self.jsonDoc= buffer.read()

            d= defer.deferred()
            d.addCallback(self.__addToBuffer)
            d.addErrback(self.__responseError)
            d.addCallback(self.__responseSuccess)
            d.addErrback(self.__parseError)

    def __addToBuffer(self):
        doc = simplejson.loads(self.jsonDoc)
        self.items_count = len(doc['data'])





        q.put_nowait(doc)

    def __responseSuccess(self):
        resp = {
            "response": "success",
            "info": "Processed " + self.items_count+ " Failed 0 Total " + self.items_count + " Seconds spent 0.002070"
        }
        self.transport.write(simplejson.dumps(resp))
        self.transport.stop()

    def __responseError(self):
        resp = {
            "response": "failure",
            "info": "Processed 0 Failed 0 Total 0 Seconds spent 0.002070"
        }
        self.transport.write(simplejson.dumps(resp))
        self.transport.stop()

    def __parseError(self,e):
        print e

        self.transport.stop()

class ZabbixSenderFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return ZabbixSender(self)

endpoints.serverFromString(reactor, "tcp:1234").listen(ZabbixSenderFactory())
reactor.run()