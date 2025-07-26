import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(('', 0))  # 绑定每个网卡
s.sendto(b'hello', ('255.255.255.255', 9999))
s.close()
