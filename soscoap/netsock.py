# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Provides an asynchronous, select/poll based socket for CoAP message I/O.
'''
import asyncore
import logging
import socket
import soscoap

log = logging.getLogger(__name__)

SOCKET_BUFSIZE = 1024

class AsyncSocket(asyncore.dispatcher):
    def __init__(self):
        '''Bind the socket to the CoAP port; ready to read'''
        asyncore.dispatcher.__init__(self)

        self.create_socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.bind(('::1', soscoap.COAP_PORT))
        log.info("AsyncSocket ready")

    def handle_read(self):
        data, addr = self.socket.recvfrom(SOCKET_BUFSIZE)
        if log.isEnabledFor(logging.DEBUG):
            hexstr = ' '.join(['{:02x}'.format(ord(b)) for b in data])
            log.debug('Read from {0}; data (hex) {1}'.format(addr, hexstr))
        #msg = sos.message.buildFrom(data=data, addr=addr)

    def writable(self):
        return False
