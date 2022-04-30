import socket
import struct
import logging

import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)


class Communicator:
    """Обмен данными с имитатором вертушки, 1 сокет"""

    # Структура пакета
    packet_struct = '13f'

    def __init__(self, host_ip: str = None, host_port: int = 6505, bind_port: int = 6502):
        self.host_addr = (host_ip, host_port)
        self.bind_addr = (self.get_ip(), bind_port)

        if host_ip is None:
            self.host_addr = (self.get_ip(), self.host_addr[1])
        self.data_NaN = [np.NaN for _ in range(13)] #вернём в случае пропуска

    @staticmethod
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('192.168.1.1', 1))  # doesn't even have to be reachable
        IP = s.getsockname()[0]
        s.close()
        return IP

    def connect(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(self.bind_addr)  # Привязка адреса и порта к сокету.
        print('[+] Ready to receive MPU data on %s:%d' % (self.bind_addr[0],
                                                         self.bind_addr[1]))
        self.server.connect(self.host_addr)
        print('[+] Connected to %s:%d' % (self.host_addr[0], self.host_addr[1]))
        self.server.settimeout(0.25)

    def control(self, u):
        msg = struct.pack('f', u)
        self.server.send(msg) # отправляем запрос

    def measure(self):
        try:
            msg, _ = self.server.recvfrom(256)
            data = struct.unpack(self.packet_struct, msg)
            return data
        except (socket.error, socket.timeout, struct.error) as e:
            logging.info('[+] No data available', e)
            return self.data_NaN

    def ctrl_and_meas(self, u):
        self.control(u)
        return self.measure()

    def close(self):
        self.server.close()
        print('[+] server closed...')

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
