# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Provides the MessageSocket class.
'''
import asyncore
import logging
import message
import socket
import soscoap
from   soscoap import event

log = logging.getLogger(__name__)

SOCKET_BUFSIZE = 1024
                
class MessageSocket(asyncore.dispatcher):
    '''Source for network CoAP messages. Implemented as a select/poll-based socket,
    based on the the built-in asyncore module. Listens on the CoAP port for the
    loopback interface.
    
    Events:
        Register a handler for an event via the 'registerFor<Event>' method.
        
        :Receive: Triggered with the received CoAP message
    
    Attributes:
        :_receiveHook: EventHook Triggered when message received
    '''
    def __init__(self):
        '''Binds the socket to the CoAP port; ready to read'''
        asyncore.dispatcher.__init__(self)
        
        self._receiveHook = event.EventHook()

        self.create_socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.bind(('::1', soscoap.COAP_PORT))
        log.info("MessageSocket ready")
        
    def registerForReceive(self, handler):
        self._receiveHook.register(handler)
        
    def handle_read(self):
        data, addr = self.socket.recvfrom(SOCKET_BUFSIZE)
        if log.isEnabledFor(logging.DEBUG):
            hexstr = ' '.join(['{:02x}'.format(ord(b)) for b in data])
            log.debug('Read from {0}; data (hex) {1}'.format(addr, hexstr))
            
        coapmsg = message.buildFrom(addr=addr, bytestr=data)
        self._receiveHook.trigger(coapmsg)
        
    def send(self, message):
        pass

    def writable(self):
        return False
