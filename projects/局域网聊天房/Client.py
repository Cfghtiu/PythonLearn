import socket
import time
from typing import Union
from threading import Thread
from enum import Enum

from Window import Window

Addr = tuple[str, int]


class Package(Enum):
    JOIN = b'j'
    CHAT = b'c'
    RENAME = b'r'
    QUIT = b'q'
    HELLO = b'h'


class Client:
    def __init__(self, username: str, group: str):
        self.username = username
        self.group = group
        self.window = Window(self)
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 端口复用
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                             socket.inet_aton(group) + socket.inet_aton('0.0.0.0'))  # 加入组播
        self.sock.bind(("", 9990))
        self.thread = Thread(target=self.recv_loop, daemon=True)
        self.users = set()

    def recv_loop(self):
        while self.running:
            try:
                pkg, name, data, addr = self.recv()
                self.handle_data(pkg, name, data, addr)
            except IOError:
                self.quit()

    def recv(self) -> tuple[Package, str, list[bytes], Addr]:
        data, addr = self.sock.recvfrom(1024)
        pkg = Package(int.to_bytes(data[0], 1, 'big'))
        data = data[1:]
        name, *data = data.split(b":")
        return pkg, name.decode("utf8"), data, addr

    def _send(self, pkg: Package, data: Union[bytes, str] = b'', addr: Addr = None):
        if isinstance(data, str):
            data = data.encode("utf8")
        data = self.username.encode("utf8") + b":" + data
        self.sock.sendto(pkg.value + data, addr or (self.group, 9990))

    def handle_data(self, pkg: Package, name: str, data: list[bytes], addr: Addr):
        if pkg == Package.CHAT:
            self.window.print(f"<{name}> {data[0].decode('utf8')}")
        elif pkg == Package.RENAME:
            new = data[0].decode("utf8")
            self.window.tip(f"{name}{addr}改名为{new}")
            self.users.discard(name)
            self.users.add(new)
            self.users.add(self.username)
        elif pkg == Package.JOIN:
            self.window.tip(f"{name}{addr}加入聊天室")
            self.users.add(name)
            self._send(Package.HELLO)  # 欢迎
        elif pkg == Package.QUIT:
            self.window.tip(f"{name}{addr}退出聊天室")
            self.users.discard(name)
            self.users.add(self.username)
        elif pkg == Package.HELLO:
            self.users.add(name)

    def chat(self, text: str):
        self._send(Package.CHAT, text)

    def rename(self, username: str):
        self._send(Package.RENAME, username)
        self.username = username
        self.window.set_name_entry(username)

    def quit(self):
        self.running = False
        self._send(Package.QUIT)
        self.sock.close()

    def start(self):
        self._send(Package.JOIN)
        self.thread.start()

        def print_names():
            time.sleep(1.2)
            self.window.print("当前房间用户:" + ", ".join(self.users))

        Thread(target=print_names, daemon=True).start()

        self.window.mainloop()
