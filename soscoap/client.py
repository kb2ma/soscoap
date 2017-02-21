# Copyright (c) 2017, Ken Bannister
# All rights reserved. 
#
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Provides an SOS CoapClient, the main SOS interface for a client-based CoAP 
application.
'''
import asyncore
import logging
import random
import socket
from   soscoap import CodeClass
from   soscoap import MediaType
from   soscoap import MessageType
from   soscoap import OptionType
from   soscoap import RequestCode
from   soscoap import ServerResponseCode
from   soscoap import SuccessResponseCode
import soscoap
from   soscoap.event import EventHook
from   soscoap.message import CoapMessage
from   soscoap.message import CoapOption
from   soscoap.resource import SosResourceTransfer
from   soscoap.msgsock import MessageSocket

log = logging.getLogger(__name__)

class CoapClient(object):
    '''Client for CoAP requests. Like a CoAP server, binds to a socket, usually
    on the standard CoAP port. However, only accepts incoming responses when
    there is an outstanding request.
    
    Events:
        Register a handler for an event via the 'registerFor<Event>' method.
        
        :ResourceGet:  Client has received a response for a resource GET request.

    Usage:
        #. cc = CoapClient() -- Create instance, using the standard CoAP port.
        #. cc.start() -- Start networking.
        *. ... -- Send messages (TBD)
        *. cc.close() -- Cleanup

     Attributes:
        :_msgSocket: MessageSocket to send/receive messages
        :_responseHook:  EventHook triggered when resource response received
        :_nextMessageId: Next sequential value for a new Message ID

    .. automethod:: soscoap.server.CoapClient.__init__
   '''
    def __init__(self, msgSocket=None, sourcePort=soscoap.COAP_PORT, dest=None):
        '''Client initialization, espeically for networking.
        
        :param msgSocket: MessageSocket Pass in only for unit testing
        :param sourcePort: int Port for source socket
        :param dest: tuple 2-tuple (string,int) for destination host address
                     and port
        '''
        destTuple = None
        if dest:
            info = socket.getaddrinfo(dest[0], dest[1], socket.AF_INET6,
                                                        socket.SOCK_DGRAM)
            log.debug('getaddrinfo: {0}'.format(info))
            # Assume we want the first 5-tuple entry returned
            destTuple = info[0][4]

        if msgSocket:
            self._msgSocket = msgSocket
        else:
            self._msgSocket = MessageSocket(localPort=sourcePort, remote=destTuple)

        self._msgSocket.registerForReceive(self._handleMessage)

        self._responseHook = EventHook()
        
        # A random start is recommended in Sec. 4.4.
        self._nextMessageId = random.randint(0, 0xFFFF)

    def close(self):
        '''Releases system resources'''
        self._msgSocket.close()
                
    def registerForResponse(self, handler):
        self._responseHook.register(handler)

    def send(self, message):
        '''Send a message'''
        self._msgSocket.send(message)
        
    def _handleMessage(self, message):
        try:
            log.debug('Handling resource response...')
            self._responseHook.trigger(message)

        except:
            log.exception('Error handling response')

    def _popMessageId(self):
        '''Returns the next sequential message ID, and increments'''
        nextid = self._nextMessageId
        self._nextMessageId = (self._nextMessageId+1 if self._nextMessageId < 0xFFFF 
                                                     else 1)
        return nextid
        
    def start(self):
        '''Start networking, with a one second timeout so client doesn't wait
        to send.'''
        log.info('Starting asyncore loop')
        asyncore.loop(1)
