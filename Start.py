#!/usr/bin/env python
#coding=utf8
#@author:weiyz

import os
import sys
import threading
import time
import warnings
import webbrowser
from Main import app

class ServerThread(threading.Thread):

    def __init__(self,port):
        threading.Thread.__init__(self)
        self.port = port

    def run(self):
        app.run(debug=True,host='127.0.0.1',port=self.port,threaded=True,use_reloader=False)

if __name__ == '__main__':
    os.system('cd %s' % os.getcwd())
    try:
        port = int(sys.argv[1])
    except Exception,e:
        warnings.warn('Invalid port number. Will use default value as 5050.')
        port = 5050
    server_thread = ServerThread(port)
    server_thread.start()
    time.sleep(1)
    webbrowser.open('http://localhost:5050/')
