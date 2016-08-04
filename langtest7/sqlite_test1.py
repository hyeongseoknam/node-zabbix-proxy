from twisted.enterprise import adbapi
from twisted.internet import protocol, reactor, endpoints, defer, task
from sqlite_client import SQLiteClient

clients = {}
def addClients(hosts):
    global clients
    for host in hosts:
        if host not in clients:
            host[host.GUID] = SQLiteClient(host)
        host[host.GUID].do()




def ontime():
    filename = "test.sqlite"
    dbpool = adbapi.ConnectionPool("sqlite3", filename, check_same_thread=False)
    d = dbpool.runQuery("select * from Host")
    d.addCallback(addClients)

def run_forever():
    try:
        reactor.run()
    except KeyboardInterrupt:
        print "Interrupted by keyboard. Exiting."
        reactor.stop()

def start_timer():
    l = task.LoopingCall(ontime)
    l.start(60.0)  # call every 60 second

access_list = [1,'MySQLdb', 'zabbix', 'zabbix', '1qaz@WSX', '192.168.25.11', 3306]

def init():
    import dbhelper
    dbhelper.initialize(access_list)


if __name__ == '__main__':
    init()
    start_timer()

    run_forever()

