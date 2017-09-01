import socket
import json


def ask_nat_type(client, serv, serv2):
    client.sendto(b'', serv2)
    query_data_dict = {
        'method': 'askNATType'
    }
    query_data = json.dumps(query_data_dict).encode()
    client.sendto(query_data, serv)
    result_bytes, _ = client.recvfrom(512)
    result = result_bytes.decode()
    return result == 'true'


def get_client_id(client, serv):
    query_data_dict = {
        'method': 'getId'
    }
    query_data = json.dumps(query_data_dict).encode()
    client.sendto(query_data, serv)
    result_bytes, _ = client.recvfrom(512)
    client_id = int(result_bytes.decode())
    return client_id
    # return result == 'true'


def listen(client, serv):
    while True:
        data, addr = client.recvfrom(1024)
        print(addr, data)
        if addr == serv:
            req = json.loads(data.decode())
            if req.get('method') == 'connect':
                client.sendto(b'', (req.get('ip'), req.get('port')))
            else:
                pass
        else:
            client.sendto(data, addr)


def connect_remote(client, serv, remote_id):
    query_data_dict = {
        'method': 'connect',
        'id': remote_id
    }
    query_data = json.dumps(query_data_dict).encode()
    client.sendto(query_data, serv)
    result_bytes, _ = client.recvfrom(512)
    result = json.loads(result_bytes.decode())
    remote_addr = (result.get('ip'), result.get('port'))
    print(client.recvfrom(512))
    while True:
        client.sendto(input().encode(), remote_addr)
        print(client.recvfrom(512))


def connect_serv():
    client = socket.socket(2, 2)
    serv = ('127.0.0.1', 2333)
    serv2 = ('127.0.0.1', 2334)
    if not ask_nat_type(client, serv, serv2):
        print('Can not p2p.')
        return
    else:
        client_id = get_client_id(client, serv)
        print('我的ID:', client_id)
        mode = input('选择模式(0:监听模式；1:主动连接模式):')
        if mode == '0':
            listen(client, serv)
        elif mode == '1':
            remote_id = int(input('要连接的ID：'))
            connect_remote(client, serv, remote_id)
        else:
            return


connect_serv()
