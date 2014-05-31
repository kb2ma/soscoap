#!/usr/bin/python
# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the Mozilla Public License 2.0, as published at the link below.
# http://opensource.org/licenses/MPL-2.0
'''
Defines and runs an example server for the SOS CoAP library.

Start the server on POSIX with:
   >PYTHONPATH=.. ./server.py
'''
import logging
import asyncore
from   soscoap import msgsock
from   soscoap import MessageType
from   soscoap import RequestCode

logging.basicConfig(filename='server.log', level=logging.DEBUG, 
                    format='%(asctime)s %(module)s %(message)s')
log = logging.getLogger(__name__)

class Server(object):
    def __init__(self):
        self.socket = msgsock.MessageSocket()
        self.socket.registerForReceive(self._handleMessage)
        
        self._resourceGetHook = EventHook()
                
    def registerForResourceGet(self, handler):
        self._resourceGetHook.register(handler)
        
    def _handleMessage(self, message):
        if message.messageType == MessageType.CON:
            if message.codeDetail == RequestCode.GET:
                log.debug('Handling resource GET request...')
                # Get path and trigger resource event
                #resource = Resource(message.absolutePath, message)
                #self._resourceGetHook.notify(resource)
                pass
    
    def send(self, resource):
        pass

# Start the server
try:
    server = Server()
    print 'Sock it to me!'
    asyncore.loop()
except KeyboardInterrupt:
    log.info('Server closed')


