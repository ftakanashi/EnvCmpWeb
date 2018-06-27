#!/usr/bin/env python
# -*- coding:utf-8 -*-

import paramiko
import socket
import time
def main():
    tran = paramiko.Transport(sock=('192.168.178.59',22))
    tran.connect(username='root',password='wyz56193028')
    channel = tran.open_session()
    channel.get_pty()
    channel.invoke_shell()

    # cmd = 'tar -cvzf /tmp/hipstest.tar.gz /hsdata/hips\n'
    cmd = 'ls\n'
    channel.send(cmd)
    channel.settimeout(1)
    while 1:
        time.sleep(1)
        try:
            print channel.recv(65535).decode('utf-8').strip('\n')
        except socket.timeout,e:
            channel.close()
            break

if __name__ == '__main__':
    main()