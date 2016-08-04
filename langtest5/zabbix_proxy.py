import threading
import socket
import sys
from StringIO import StringIO
import struct
import simplejson

zabbix_address = ''
zabbix_port = 10051
item_doc= dict()

class _ZabbixProxy(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        server_address = ('0.0.0.0', 10051)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)
        try:
            while True:
                connection, client_address = sock.accept()
                try:
                    doc = self.parse(connection)
                    self.update(doc)
                    zconn = socket.create_connection((zabbix_address, zabbix_port))
                    buf = StringIO()
                    buf.write('ZBXD\1')
                    buf.write(struct.pack('Q', len(doc)))
                    buf.write(doc)
                    zconn.sendall(buf.getvalue())
                    doc = self.parse(zconn)
                    buf = StringIO()
                    buf.write('ZBXD\1')
                    buf.write(struct.pack('Q', len(doc)))
                    buf.write(doc)
                    connection.sendall(buf.getvalue())
                    connection.close()
                finally:
                    connection.close()
        finally:
            sock.close()

    def parse(self,conn):
        self.read(conn, 5)
        payload_length = struct.unpack('Q', self.read(conn, 8))[0]
        return self.read(conn, payload_length)

    def read(self, conn, length):
        buf = StringIO()
        nbyteleft = length
        while nbyteleft:
            nbytethistime = conn.recv(nbyteleft)
            if nbytethistime:
                buf.write(nbytethistime )
                nbyteleft -= len(nbytethistime )
            else:
                raise Exception('read error')
        return buf.getvalue()

    def update(self, jsondoc):
        global item_doc
        doc = simplejson.loads(jsondoc)
        if 'data' in doc:
            for item in doc['data']:
                key = item['key']
                item_doc[key] = item

def start():
    _ZabbixProxy().start()
