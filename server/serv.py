import socket
from datetime import datetime
import requests
from threading import Thread
import config


def log(*args):
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(time, *args)


def call_webhook(cfg, host, port):
    r = requests.request(cfg.method, cfg.url, headers=cfg.headers, json=cfg.json(host, port))
    log('call webhook:', cfg.name, 'result:', r.status_code)
    return r.status_code == 200


class Server:
    def __init__(self):
        self.listen_addr = ('0.0.0.0', 4040)
        self.port = 0
        self.s = None
        self.flags = [False for _ in config.webhooks]

        log('listen on', self.listen_addr)

    def handle(self, data, addr):
        host, new_port = addr
        if data != b'ping':
            return

        log('recv ping, host:', host, 'port:', new_port)

        if self.port == new_port:
            return
        else:
            self.port = new_port
            self.flags = [True for _ in config.webhooks]

        for i, flag in enumerate(self.flags):
            if flag and call_webhook(config.webhooks[i], host, new_port):
                self.flags[i] = False

    def run(self):
        self.s = socket.socket(2, 2)
        self.s.bind(self.listen_addr)

        while True:
            data, addr = self.s.recvfrom(512)
            Thread(target=self.handle, args=(data, addr)).start()


def main():
    s = Server()
    s.run()


main()
