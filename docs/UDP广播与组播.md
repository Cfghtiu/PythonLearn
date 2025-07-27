# UDP广播与组播
假如你的程序需要在局域网内发现其他节点，那么可以使用UDP广播或者组播    
广播会发送给子网内所有设备，可能造成不必要的网络流量  
而组播更高效，但需要路由器支持

## 注意
1. 有的路由器不支持组播，所以个人建议用广播
2. 广播和组播都可能会被防火墙阻止，需要进行设置
3. 有的选项的等级是socket.IPPROTO_IP，有的是socket.SOL_SOCKET

## 广播
### UDP广播的本质
就是向255.255.255.255(或子网广播地址如192.168.1.255)发送数据，这时，一个网段的所有节点都能收到

### 创建/发送广播
```python
import socket
# UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 设置socket选项(socket.SOL_SOCKET)，允许广播(socket.SO_BROADCAST, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# 允许端口复用，可选，一般都会开启，否则如果本地开启两个相同软件会提示端口被占用
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 发送
sock.sendto(b"hello", ("255.255.255.255", 12345))
# 接收就是正常接收，绑定端口为12345
```
**注意**: 自己绑定的12345端口也会接受到自己发送的广播，建议通过自定义协议头来区分

## 组播
### 加入组播的核心
通过设置`socket.IP_ADD_MEMBERSHIP`选项加入组播  
选项要求的值的类型在C语言结构为
```c
struct ip_mreq {
    struct in_addr imr_multiaddr;  // 组播IP (4字节)
    struct in_addr imr_interface;  // 本地接口IP (4字节)
};
```
组播IP的范围在224.0.0.0到239.255.255.255之间，可自由选择  
那么创建这个结构的字节代码就是
```python
import socket
group = socket.inet_aton("224.1.1.1")  # socket.inet_aton返回长度4，打包后的bytes
print(group)  # b'\xe0\x01\x01\x01'
interface = socket.inet_aton("0.0.0.0")  # 0.0.0.0代表监听所有网卡收到的数据
print(interface)  # b'\x00\x00\x00\x00'
mreq = group +  interface  # 拼接后就符合ip_mreq的结构
```
### 创建
```python
import socket
# UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 允许端口复用，可选，一般都会开启，否则如果本地开启两个相同软件会提示端口被占用
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 禁用回环，可选，默认开启时本机会收到自己发的组播
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)
# 决定数据包传递距离，每经过1个路由器就减1，为0就抛弃，默认1
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
# 需要选绑定地址
sock.bind(("0.0.0.0", 12345))
# 加入组播
mreq = socket.inet_aton("224.1.1.1") + socket.inet_aton("0.0.0.0")
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
# 接下来正常发送和接收
```

### 另一个创建mreq的方法
```python
import socket
import struct
group = socket.inet_aton("224.1.1.1")
mreq = struct.pack("4sl", group, socket.INADDR_ANY)
```
这时mreq和上面的mreq的值一样，
懂struct模块的人会知道4sl会将group打包成4字节的字符串，
而由于group的值本身就是4字节的，所以不会变，为b'\xe0\x01\x01\x01'，
而socket.INADDR_ANY会被打包为4字节无符号整数，
由于socket.INADDR_ANY的值是0，所以就会打包成b'\x00\x00\x00\x00'，
最后返回拼接的结果，跟上面一样

两种方法不同在于能方法2直接用`socket.INADDR_ANY`，也就是0……