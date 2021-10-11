import socket
from datetime import datetime
import requests
from threading import Thread
from dataclasses import dataclass
import config


def log(*args):
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(time, *args)


def call_webhook(cfg, service_name, host, port):
    r = requests.request(cfg.method, cfg.url, headers=cfg.headers, json=cfg.json(service_name, host, port))
    log('call webhook:', cfg.name, 'result:', r.status_code)
    return str(r.status_code).startswith('2')


@dataclass
class Service:
    webhooks: [config.WebhookConfig]
    name: str
    port: int = 0

    def set_flags(self, flag):
        for w in self.webhooks:
            w.flag = flag

    def check_flags(self, host, port):
        for w in self.webhooks:
            if w.flag and call_webhook(w, self.name, host, port):
                w.flag = False


class Server:
    def __init__(self):
        self.listen_addr = ('0.0.0.0', config.listen_port)
        self.s = None

        self.services = {}
        for service_name, webhooks in config.webhooks_config.items():
            service = Service(webhooks=webhooks, name=service_name)
            self.services[service_name] = service
        log(self.services)

    def handle(self, raw, addr):
        data = raw.decode()
        if not data.startswith('ping'):
            return

        host, port = addr
        _, service_name = data.split(' ')
        log('recv ping, service:', service_name, 'host:', host, 'port:', port)

        service = self.services[service_name]
        old_port = service.port
        if old_port != port:
            service.set_flags(True)
            service.port = port

        for service in self.services.values():
            service.check_flags(host, port)

    def run(self):
        self.s = socket.socket(2, 2)
        self.s.bind(self.listen_addr)
        log('listen on', self.listen_addr)

        while True:
            data, addr = self.s.recvfrom(512)
            Thread(target=self.handle, args=(data, addr)).start()


def main():
    s = Server()
    s.run()


main()
