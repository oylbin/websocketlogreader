# -*- coding: utf-8 -*-
import argparse
import random
import os
import time

import cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

import threading
import datetime
import io
import json
import subprocess

# http://stackoverflow.com/questions/7647167/check-if-a-process-is-running-in-python-in-linux-unix
# http://stackoverflow.com/a/7647375
def is_process_running(process_id):
    process_id = int(process_id)
    # 特殊处理 process_id = 0的话始终返回true，用于长时间监控某个日志文件的情况
    if process_id == 0:
        return True
    try:
        os.kill(process_id, 0)
        return True
    except OSError:
        return False

class ThreadClass(threading.Thread):
    def __init__(self, ws, pid, filename):
        threading.Thread.__init__(self)
        self.ws = ws
        self.pid = pid
        self.filename = filename
        self.stop = False

    def run(self):
        if not os.path.exists(self.filename):
            self.ws.close(1001,"log file not exits[%s]"%self.filename)
            return
        #self.ws.send(self.filename+"\n")
        f = io.open(self.filename,'rt',1,'utf-8')
        while True:
            if self.ws == None or self.stop == True:
                break
            s = f.read()
            if len(s):
                self.ws.send(s)
            elif is_process_running(self.pid) == False:
                # 进程结束了，而且日志也读出不内容了
                break
            time.sleep(0.1)
        if self.ws:
            self.ws.close(1000,"\n\nprocess finished\n\n")

class ChatWebSocketHandler(WebSocket):
    t = None

    def received_message(self, m):
        #cherrypy.engine.publish('websocket-broadcast', m)
        #cherrypy.log("received_message: %s"%(str(m)))
        if self.t == None:
            try:
                d = json.loads(str(m))
                if d.has_key('ping'):
                    self.close(1000,"pong")
                    return
                if not d.has_key('pid'):
                    self.close(1001,"need pid param")
                    return
                if not d.has_key('filename'):
                    self.close(1001,"need filename param")
                    return
                pid = d['pid']
                filename = d['filename']

                self.t = ThreadClass(self,pid,filename)
                self.t.start()
            except ValueError,err:
                self.close(1001,"failed to json decode [%s]"%str(m))

    def closed(self, code, reason="A client left the room without a proper explanation."):
        if self.t:
            self.t.stop = True
            self.t.join()
        #cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))

class Root(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @cherrypy.expose
    def index(self):
        #return ""+cherrypy.server.base()
        import socket
        return socket.gethostbyname(socket.gethostname())

    @cherrypy.expose
    def js(self):
        return "hi"

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Echo CherryPy Server')
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('-p', '--port', default=9001, type=int)
    args = parser.parse_args()

    cherrypy.config.update({'server.socket_host': args.host,'server.socket_port': args.port,'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__))})

                            
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.quickstart(Root(args.host, args.port), '', config={
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': ChatWebSocketHandler
            }
        }
    )
