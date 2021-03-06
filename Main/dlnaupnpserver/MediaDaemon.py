'''
Created on 28-08-2011

@author: xps
'''

import sys

from Daemon import Daemon
from MediaServer import MediaServer, Runserver, RunRPCServer
import os
from threading import Lock
from Database2 import DBCursor
from backendobject import BackendObject
import signal

pid_path = '/tmp/daemon.pid'
log_path = '/tmp/daemon.log'

def set_exit_handler(func):
    if os.name == "nt":
        try:
            import win32api
            win32api.SetConsoleCtrlHandler(func, True)
        except ImportError:
            version = ".".join(map(str, sys.version_info[:2]))
            raise Exception("pywin32 not installed for Python " + version)
    else:
        signal.signal(signal.SIGUSR1, func)

class MyDaemon(Daemon):
    def __init__(self, **kwargs):
        self.serverProcess = None
        Daemon.__init__(self, **kwargs)
    
    def run(self):
        path_to_db = "media.db"
        dbpath = os.path.abspath(path_to_db)
        lock = Lock()
        dbCursor = DBCursor(db_path=dbpath)
        backendObject = BackendObject(dbCursor, "test")
        mediaServer = MediaServer(backendObject=backendObject, lock=lock)
        self.serverProcess = Runserver(mediaServer)
        self.serverProcess.start()
        lock.acquire()
        try:
            r = RunRPCServer(backendObject)
            r.run()
        finally:
            lock.release()
if __name__ == "__main__":
    
    
    daemon = MyDaemon(pidfile = pid_path, stdout = log_path, stderr = log_path)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
            #daemon.run()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            daemon.stop()
            sys.exit(2)
        sys.exit(0)
    else:
        daemon.stop()
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)