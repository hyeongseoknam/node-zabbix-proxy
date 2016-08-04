from datetime import datetime, timedelta
from twisted.internet import protocol, reactor, endpoints, defer, task
from twisted.internet.endpoints import TCP4ClientEndpoint
import struct
from StringIO import StringIO
import simplejson
import random
import time
import zabbix_proxy

class ZabbixClientSimulator(protocol.Factory):
    def __init__(self, hostname, zabbix_server_ip, zabbix_server_port):
        self.__active_checks= {}
        self.__last_active_check = None
        self.__sendbuf = []
        self.__zabbix_server_ip = zabbix_server_ip
        self.__zabbix_server_port = zabbix_server_port
        self.__hostname = hostname

    def do(self):
        # print 'def do(self): step -1'
        now = datetime.now()
        # if self.__last_active_check:
        #     print 'elapsed:',now - self.__last_active_check
        if not self.__active_checks or not now - self.__last_active_check > timedelta(minutes=1):
            # print 'def do(self): step -2'
            self.__sendActiveChecks()
            self.__sendData()
            self.__last_active_check = now
            print 'def do(self): step -3'

    def __sendData(self):
        # print 'def __sendData(self): step -1'
        self.__sendbuf.append(ZabbixHelper().getAgentData(self.__hostname))
        point = TCP4ClientEndpoint(reactor, self.__zabbix_server_ip, self.__zabbix_server_port)
        d = point.connect(self)
        d.addErrback(self.__zabbixServerConnectionFail)
        # print 'def __sendData(self): step -2'

    def __sendActiveChecks(self):
        # print 'def __sendActiveChecks(self):: step -1'
        self.__sendbuf.append(ZabbixHelper().getActiveChecks(self.__hostname))
        point = TCP4ClientEndpoint(reactor, self.__zabbix_server_ip, self.__zabbix_server_port)
        d = point.connect(self)
        d.addErrback(self.__zabbixServerConnectionFail)
        # print 'def __sendActiveChecks(self):: step -2'

    def __zabbixServerConnectionFail(self, e):
        print "__zabbixServerConnectionFail",e

    def buildProtocol(self, addr):
        return ZabbixSender(self)

    def updateZabbixClient(self, items):
        for item in items:
            key = item['key']
            delay = int(item['delay'])
            if key not in self.__active_checks:
                self.__active_checks[key] = {'key': key, 'delay': delay, 'lastupdated': None}
            else:
                d = self.__active_checks[key]
                d['delay'] = delay

    def getSenderBuffer(self):
        return self.__sendbuf.pop()

class ZabbixSender(protocol.Protocol):
    def __init__(self, factory):
        self.__factory= factory
        self.__payload_length = 0

    def connectionMade(self):
        # print "def connectionMade(self): step -1"
        self.__buffer= StringIO()
        self.transport.write(self.__factory.getSenderBuffer())
        # print "def connectionMade(self): step -2"

    def connectionLost(self, reason):
        # print "def connectionLost(self, reason):"

        reason.printTraceback()
        reason.printDetailedTraceback()
        print reason.getErrorMessage()

    def dataReceived(self, data):
        # print 'def dataReceived(self, data): step -1'
        if self.__parseHeader(data):
            # print 'parse complete:'
            # if 'data' in self.__doc:
            #     self.__factory.updateZabbixClient(self.__doc['data'])
            self.transport.loseConnection()
        # print 'def dataReceived(self, data): step -2'

    def __parseHeader(self, data):
        self.__buffer.seek(0,2)
        self.__buffer.write(data)
        self.__buffer.seek(0, 0)
        if not self.__payload_length and self.__buffer.len >= 13:
            header = self.__buffer.read(5)
            if 'ZBXD' == header[0:4] and '\1' == header[4]:
                self.__payload_length = struct.unpack('Q', self.__buffer.read(8))[0]
        if self.__payload_length and self.__buffer.len - 13 == self.__payload_length:
            self.__buffer.seek(13, 0)
            jsonDoc = self.__buffer.read()
            self.__doc = simplejson.loads(jsonDoc)
            return True
        else:
            return False

    def __parseError(self, e):
        print "def __parseError(self,e):"
        print e

        self.transport.stop()



class ZabbixHelper(object):
    def getActiveChecks(self, hostname):
        doc = dict(request="active checks",
            host= hostname,
            host_metadata = 'auto_register')

        return self.getSenderBuffer(simplejson.dumps(doc))


    def getSenderBuffer(self, jsonbody):
        buf = StringIO()
        buf.write('ZBXD\1')
        buf.write(struct.pack('Q', len(jsonbody)))
        buf.write(jsonbody)
        # print buf.getvalue()

        return buf.getvalue()

    def getAgentData(self,host= None, active_checks= {}):
        item_values = []
        items = zabbix_proxy.item_doc.values()
        # print 'def getAgentData(self,host= None, active_checks= {}):',items
        agent_data=dict(request= "agent data",
            data= item_values)
        now = int(time.mktime(datetime.now().timetuple()))
        ns = 0

        for item in items:
            value = item['value']
            key = item['key']
            item_values.append(dict(host = host, key= key, value=value, clock= now, ns=ns))

        return self.getSenderBuffer(simplejson.dumps(agent_data))