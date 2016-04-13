import socket
import struct
import json
import sys

zserver='localhost'
zport=10051

def send( mydata):
    '''
    This is the method that actually sends the data to the zabbix server.
    '''
    mydata = json.dumps(mydata)
    data_length = len(mydata)
    data_header = str(struct.pack('q', data_length))
    data_to_send = 'ZBXD\1' + str(data_header) + str(mydata)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((zserver, zport))
        sock.send(data_to_send)
    except Exception, err:
        err_message = u'Error talking to server: %s\n' %str(err)
        sys.stderr.write(err_message)
        return err_message

    resp= sock.recv(5)
    data_length = sock.recv(8)
    data_length= struct.unpack('<Q',data_length )[0]
    resp= sock.recv(data_length)
    sock.close()

    return resp
    #return sock.recv(10)


active_checks={'request': 'active checks',
    'host':'hello world host'
}
agent_data={'request':'agent data',
    'data':[{
            'host':'aaa',
            'key':'mykey',
            'value':'12345',
            'clock':1360150944,
            'ns': 396084028
        }
]
}
#active_checks_resp = send(active_checks)
#print 'active_checks:',active_checks_resp
agent_data_resp = send(agent_data)
print 'agent_data: ',agent_data_resp
