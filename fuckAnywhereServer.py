import socket
import threading
import time
import json


def return_nat_type(s, client, client_pool):
    last_time = client_pool.get(client)
    if last_time and (time.time() - last_time < 3):
        s.sendto(b'true', client)
    else:
        s.sendto(b'false', client)


def return_id(s, client, client_id):
    s.sendto(str(client_id).encode(), client)


def _gen_id():
    # pass
    id = 1
    while True:
        yield id
        id += 1


def get_client_id(client, id_pool, gen_id):
    if id_pool.get(client):
        client_id = id_pool.get(client)
    else:
        client_id = next(gen_id)
        id_pool[client] = client_id
        id_pool[client_id] = client
    return client_id


def send_connect_command(s, client_a, client_b):
    ip, port = client_a
    data_dict = {
        'method': 'connect',
        'ip': ip,
        'port': port
    }
    command = json.dumps(data_dict).encode()
    s.sendto(command, client_b)

    ip, port = client_b
    data_dict = {
        'ip': ip,
        'port': port
    }
    result = json.dumps(data_dict).encode()
    s.sendto(result, client_a)


def get_handle(s, client_pool):

    gen_id = _gen_id()
    id_pool = {}

    def handle(data, client):
        client_id = get_client_id(client, id_pool, gen_id)

        req = json.loads(data.decode())
        print(client, req)

        if req.get('method') == 'askNATType':
            return_nat_type(s, client, client_pool)

        elif req.get('method') == 'getId':
            return_id(s, client, client_id)

        elif req.get('method') == 'connect':
            # print(id_pool)
            client_b = id_pool.get(req.get('id'))
            # print(req, req.get('id'), id_pool.get(1))
            send_connect_command(s, client, client_b)

        else:
            pass

    return handle


def start_serv2(client_pool):
    s2 = socket.socket(2, 2)
    s2.bind(('0.0.0.0', 2334))
    while True:
        data, client = s2.recvfrom(512)
        # print(data, client)
        client_pool[client] = int(time.time())


def start_serv():
    s = socket.socket(2, 2)
    s.bind(('0.0.0.0', 2333))

    client_pool = {}
    s2 = threading.Thread(target=start_serv2, args=(client_pool,))
    s2.start()

    handle = get_handle(s, client_pool)
    while True:
        data, client = s.recvfrom(512)
        handle(data, client)


start_serv()
# return_id = return_id_gen()
# print(next(return_id))
