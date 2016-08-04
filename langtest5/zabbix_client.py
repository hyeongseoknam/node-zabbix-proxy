from twisted.internet import protocol, reactor, endpoints, defer, task
from twisted.internet.endpoints import TCP4ClientEndpoint
from StringIO import StringIO
import struct
import simplejson
from zabbix_protocols import ZabbixClientSimulator
import zabbix_proxy

clients = []
i = 0
nclients_this_time = 168
def timer():
    global clients
    global i
    global nclients_this_time
    print 'def timer called', len(clients)
    # for client in clients:
    total_clients = len(clients)

    for n in range(nclients_this_time):
        if i < total_clients:
            client = clients[i]
            client.do()
            i += 1
        else:
            i=0



def run_forever():
    try:
        reactor.run()
    except KeyboardInterrupt:
        print "Interrupted by keyboard. Exiting."
        reactor.stop()

def create_clients():
    global clients
    hostname_prefix="20160727_host_"
    #zabbix_server_ip = '192.168.1.214'
    zabbix_server_ip = '192.168.1.175'
    zabbix_server_port = 10051
    for i in range(2000):
        hostname = hostname_prefix +str(i)
        clients.append(ZabbixClientSimulator(hostname, zabbix_server_ip, zabbix_server_port))
    l = task.LoopingCall(timer)
    l.start(5.0)  # call every 60 second

def startUpload():
    zabbix_proxy.zabbix_address='192.168.1.214'
    zabbix_proxy.start()

if __name__ == '__main__':
    startUpload()
    create_clients()
    run_forever()
