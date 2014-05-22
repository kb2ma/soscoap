#!/usr/bin/python
# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the Mozilla Public License 2.0, as published at the link below.
# http://opensource.org/licenses/MPL-2.0
'''
Defines SosServer, an example server for the SOS CoAP library.

Start the server with:
   >python SosServer.py
'''
import asyncore
import logging
import socket

logging.basicConfig(filename='server.log', level=logging.DEBUG, 
                    format='%(asctime)s %(module)s %(message)s')
log = logging.getLogger(__name__)

COAP_PORT      = 5683
SOCKET_BUFSIZE = 1024

class SosServer(asyncore.dispatcher):
    def __init__(self):
        '''Bind the socket to the CoAP port; ready to read'''
        log.info("Server starting")
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.bind(('::1', COAP_PORT))
        log.info("Server ready")

    def handle_read(self):
        data, addr = self.recvfrom(SOCKET_BUFSIZE)
        
        debugTmpl  = 'Read from {0}; data {1}' 
        log.debug(debugTmpl.format(addr, ' '.join([hex(ord(b)) for b in data])))

    def writable(self):
        return False

# Start the server
SosServer()
try:
    asyncore.loop()
except KeyboardInterrupt:
    log.info('Server closed')


