from twisted.internet import protocol, reactor, endpoints, defer, task
from twisted.internet.endpoints import TCP4ClientEndpoint
from StringIO import StringIO
import struct
import simplejson
from zabbix_protocols import ZabbixClientSimulator

clients = []

def timer():
    global clients
    print 'def timer called', len(clients)
    for client in clients:
        client.do()

def run_forever():
    try:
        reactor.run()
    except KeyboardInterrupt:
        print "Interrupted by keyboard. Exiting."
        reactor.stop()

def create_clients():
    global clients
    hostname_prefix="hsnam_host_"
    zabbix_server_ip = 'localhost'
    zabbix_server_port = 10052
    for i in range(100):
        hostname = hostname_prefix +str(i)
        clients.append(ZabbixClientSimulator(hostname, zabbix_server_ip, zabbix_server_port))
    l = task.LoopingCall(timer)
    l.start(60.0)  # call every 60 second

if __name__ == '__main__':
    create_clients()

    run_forever()