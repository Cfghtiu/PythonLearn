import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 9999))
print('Bind UDP on 9999...')
data, addr = s.recvfrom(1024)
print(data.decode())
