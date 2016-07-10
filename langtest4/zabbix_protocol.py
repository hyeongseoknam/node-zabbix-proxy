from twisted.internet.protocol import Factory, Protocol
import simplejson
from StringIO import StringIO
import struct

class ZabbixProtocol(Protocol):
    def __init__(self, proxy_protocol):
        self.__proxy_protocol = proxy_protocol
        self.buffer = StringIO()
        self.__payload_length = None

    def connectionMade(self):
        print 'ZabbixProtocol.connectionMade step -1'
        jsondoc = simplejson.dumps(self.__proxy_protocol.getDoc())
        outbuf = StringIO()
        outbuf.write('ZBXD\1')
        outbuf.write(struct.pack('Q',len(jsondoc)))
        outbuf.write(jsondoc)
        print 'sending', jsondoc
        self.transport.write(outbuf.getvalue())

    def dataReceived(self, data):
        print 'ZabbixProtocol def dataReceived(self, data):'
        self.buffer.seek(0, 2)
        self.buffer.write(data)
        self.__parseHeader()

    def __parseHeader(self):
        self.buffer.seek(0, 0)
        if not self.__payload_length and self.buffer.len >= 13:
            header = self.buffer.read(5)
            if 'ZBXD' == header[0:4] and '\1' == header[4]:
                self.__payload_length = struct.unpack('Q', self.buffer.read(8))[0]
        if self.__payload_length and self.buffer.len - 13 == self.__payload_length:
            self.buffer.seek(13, 0)
            jsonDoc = self.buffer.read()
            print 'ZabbixProtocol def __parseHeader(self):'
            outbuf = StringIO()
            outbuf.write('ZBXD\1')
            outbuf.write(struct.pack('Q', len(jsonDoc)))
            outbuf.write(jsonDoc)
            print 'relaying',jsonDoc
            self.__proxy_protocol.transport.write(outbuf.getvalue())
            self.__proxy_protocol.transport.loseConnection()
            print 'send complete'

    def connectionLost(self, reason):
        print 'ZabbixProtocol.connectionLost step -1'
        print reason.getErrorMessage()


class ZabbixFactory(Factory):
    def __init__(self, proxy_protocol):
        self.__proxy_protocol = proxy_protocol

    def buildProtocol(self, addr):
        return ZabbixProtocol(self.__proxy_protocol)