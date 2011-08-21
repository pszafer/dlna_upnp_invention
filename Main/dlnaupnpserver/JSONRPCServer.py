'''
Created on 18-08-2011

@copyright: 2011,
@author: Pawel Szafer
@license:  Licensed under the BSD license
 http://www.opensource.org/licenses/bsd-license.php
 
@contact: pszafer@gmail.com
@version: 0.8.5

'''
import json
import socket
import struct
import threading
import time

class JsonSocket(object):
    
    def __init__(self, address = 'localhost', port = 7777):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connectionSocket = self.socket
        self._timeout = None
        self._address = address
        self._port = port
    
    def sendObject(self, obj):
        msg = json.dumps(obj)
        if self.socket:
            frmt = "=%ds" % len(msg)
            packedMsg = struct.pack(frmt, msg)
            packedHdr = struct.pack('=I', len(packedMsg))
            self._send(packedHdr)
            self._send(packedMsg)
        
    def _send(self, message):
        sent = 0
        while sent < len(message):
            sent += self.connectionSocket._send(message[sent:])
    
    def _read(self, size):
        data = ''
        while len(data) < size:
            cache = self.connectionSocket.recv(size - len(data))
            data += cache
            if cache == '':
                raise RuntimeError("Socket error")
        return data
    
    def msgLen(self):
        a = self._read(4)
        s = struct.unpack('=I', a)
        return s[0]
    
    def readObject(self):
        size = self.msgLen()
        data = self._read(size)
        frmt = "=%ds" % size
        msg = struct.unpack(frmt, data)
        return json.loads(msg[0])
    
    def close(self):
        self.socket.close()
        if self.socket != self.connectionSocket:
            self.connectionSocket.close()
            
    def getTimeout(self):
        return self._timeout
    
    def _setTimeout(self, timeout):
        self._timeout = timeout
        self.socket.settimeout(timeout)
        self.connectionSocket.settimeout(timeout)
        
    def getAddress(self):
        return self._address
    
    def setAddress(self, address):
        pass
    
    def getPort(self):
        return self._port

    def setPort(self, port):
        pass
    
    timeout = property(getTimeout, _setTimeout, doc='blrbrltb')
    _address = property(getAddress, setAddress, doc='a')
    _port = property(getPort, setPort, doc='b')
    
class JsonServer(JsonSocket):
    '''
    classdocs
    '''

    def __init__(self, ip_address='localhost', port=7777):
        '''
        Constructor
        '''
        super(JsonServer, self).__init__(ip_address, port)
        self.bind()
        
    def bind(self):
        self.socket.bind({
                          self._address,
                          self._port
                          })
        
    def listen(self):
        self.socket.listen()
        
    def accept(self):
        return self.socket.accept()
    
    def acceptConnection(self):
        self.listen()
        self.connectionSocket, addr = self.accept()
        self.connectionSocket.settimeout(self.timeout)
        
class ThreadedJsonServer(threading.Thread, JsonServer):
    '''
    
    '''
    
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        JsonServer.__init__(self)
        self.is_alive = False
        
    def processMessage(self, obj):
        pass
    
    def run(self):
        while self.is_alive:
            try:
                self.acceptConnection()
            except socket.timeout, e:
                continue
            except Exception, e:
                continue
            while self.is_alive:
                try:
                    obj = self.readObject()
                    self.processMessage()
                except socket.timeout, e:
                    continue
                except Exception, e:
                    self.connectionSocket.close()
                
    def start(self):
        self.is_alive = True
        super(ThreadedJsonServer, self).start()
        
    def stop(self):
        self.is_alive = False
        
class JsonClient(JsonSocket):
    def __init__(self, address='localhost', port=7777):
        super(JsonClient, self).__init__(address, port)

    def connect(self):
        for i in range(10):
            try:
                self.socket.connect( (self._address, self._port) )
            except socket.error, e:
                time.sleep(3)
                continue
            return True
        return False
    