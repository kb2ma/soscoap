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

    Usage:
        #. cc = CoapClient() -- Create instance, using the standard CoAP port.
        #. cc.start() -- Start networking.
        *. ... -- Send messages (TBD)
        *. cc.close() -- Cleanup

     Attributes:
        :_msgSocket: MessageSocket to send/receive messages
        :_nextMessageId:    Next sequential value for a new Message ID

    .. automethod:: soscoap.server.CoapClient.__init__
   '''
    def __init__(self, msgSocket=None, port=soscoap.COAP_PORT):
        '''Pass in msgSocket only for unit testing.
        Pass in port for non-standard CoAP port.
        '''
        self._msgSocket = msgSocket if msgSocket else MessageSocket(port)
        self._msgSocket.registerForReceive(self._handleMessage)
        
        # A random start is recommended in Sec. 4.4.
        self._nextMessageId = random.randint(0, 0xFFFF)

    def close(self):
        '''Releases system resources'''
        self._msgSocket.close()
        
    def _handleMessage(self, message):
        '''Accepts/reads response, and ignores a request'''
        try:
            log.debug('Handling message for code class: {0}'.format(message.codeClass))
        except:
            log.exception('Error handling message')
        
    def _popMessageId(self):
        '''Returns the next sequential message ID, and increments'''
        nextid = self._nextMessageId
        self._nextMessageId = (self._nextMessageId+1 if self._nextMessageId < 0xFFFF 
                                                     else 1)
        return nextid
        
    def start(self):
        '''Start networking.'''
        log.info('Starting asyncore loop')
        asyncore.loop()
