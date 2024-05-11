"""
一个简易的局域网聊天房，目前有重名bug
"""
import argparse
import socket

from Client import Client


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--username", type=str, default=socket.gethostname())
    parser.add_argument("-g", "--group", type=str, default="224.6.6.6")
    args = parser.parse_args()

    client = Client(args.username, args.group)
    client.start()


if __name__ == '__main__':
    main()
