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
import message as msgModule
import socket
import soscoap
from   soscoap import event
import sys

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
        :_outgoing: List (queue) of messages ready to send
        :_receiveHook: EventHook Triggered when message received
    '''
    def __init__(self):
        '''Binds the socket to the CoAP port; ready to read'''
        asyncore.dispatcher.__init__(self)
        
        self._receiveHook = event.EventHook()
        self._outgoing    = []

        self.create_socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.bind(('::1', soscoap.COAP_PORT))
        log.info('MessageSocket ready')
        
    def registerForReceive(self, handler):
        self._receiveHook.register(handler)
        
    def handle_read(self):
        data, addr = self.socket.recvfrom(SOCKET_BUFSIZE)
        if log.isEnabledFor(logging.DEBUG):
            hexstr = ' '.join(['{:02x}'.format(ord(b)) for b in data])
            log.debug('Read from {0}; data (hex) {1}'.format(addr, hexstr))
          
        # Top-level error handling when receive message
        try:
            coapmsg = msgModule.buildFrom(address=addr, bytestr=data)
            self._receiveHook.trigger(coapmsg)
        except:
            log.exception('Can\'t handle socket read')
        
    def send(self, message):
        '''Puts the provided message on the outgoing queue for the next write
        opportunity.
        '''
        self._outgoing.append(message)
        log.debug('Added message to outgoing queue')
        
    def handle_write(self):
        if self._outgoing:
            # Top-level error handling when send message
            try:
                message = self._outgoing.pop(0)
                log.info('Sending message')
                self.socket.sendto(msgModule.serialize(message), message.address)
            except:
                log.exception('Can\'t handle socket send')

    def writable(self):
        return self._outgoing
