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
import soscoap.netsock as sos_sock

logging.basicConfig(filename='server.log', level=logging.DEBUG, 
                    format='%(asctime)s %(module)s %(message)s')
log = logging.getLogger(__name__)

class Server(object):
    def __init__(self):
        self.socket = sos_sock.AsyncSocket()

# Start the server
try:
    server = Server()
    asyncore.loop()
except KeyboardInterrupt:
    log.info('Server closed')


