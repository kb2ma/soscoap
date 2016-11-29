# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Provides an SOS CoapServer, the main SOS interface for a server-based CoAP 
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

class CoapServer(object):
    '''Server for CoAP requests. Requires another entity to define its use by
    registering event handlers.
    
    Events:
        Register a handler for an event via the 'registerFor<Event>' method.
        
        :ResourceGet:  Server requests the value for the provided resource, to 
                       service a client GET request.
        :ResourcePut:  Server forwards the value for the provided resource, to 
                       service a client PUT request.
        :ResourcePost: Server forwards the value for the provided resource, to 
                       service a client POST request.
        
    Usage:
        #. cs = CoapServer() -- Create instance
        #. Register event handlers as needed; for example, cs.registerForResourceGet(). 
        #. cs.start() -- Start to listen for requests

     Attributes:
        :_msgSocket: MessageSocket to send/receive messages
        :_resourceGetHook:  EventHook triggered when GET resource requested
        :_resourcePutHook:  EventHook triggered when PUT resource requested
        :_resourcePostHook: EventHook triggered when POST resource requested
        :_nextMessageId:    Next sequential value for a new Message ID
   '''
    def __init__(self, msgSocket=None):
        '''Pass in msgSocket only for unit testing'''
        self._msgSocket = msgSocket if msgSocket else MessageSocket()
        self._msgSocket.registerForReceive(self._handleMessage)
        
        self._resourceGetHook  = EventHook()
        self._resourcePutHook  = EventHook()
        self._resourcePostHook = EventHook()
        
        # A random start is recommended in Sec. 4.4.
        self._nextMessageId = random.randint(0, 0xFFFF)
                
    def registerForResourceGet(self, handler):
        self._resourceGetHook.register(handler)
        
    def registerForResourcePost(self, handler):
        self._resourcePostHook.register(handler)
        
    def registerForResourcePut(self, handler):
        self._resourcePutHook.register(handler)
        
    def _handleMessage(self, message):
        resource = None
        try:
            resource = SosResourceTransfer(message.absolutePath(), 
                                           sourceAddress=message.address)

            if message.codeDetail == RequestCode.GET:
                log.debug('Handling resource GET request...')
                # Retrieve requested resource via event, and send reply
                self._resourceGetHook.trigger(resource)
                self._sendGetReply(message, resource)

            elif message.codeDetail == RequestCode.PUT:
                log.debug('Handling resource PUT request...')
                resource.value = message.typedPayload()
                self._resourcePutHook.trigger(resource)
                self._sendPutReply(message, resource)

            elif message.codeDetail == RequestCode.POST:
                log.debug('Handling resource POST request...')
                resource.value = message.typedPayload()
                self._resourcePostHook.trigger(resource)
                self._sendPostReply(message, resource)
        except:
            log.exception('Error handling message; will send error reply')
            self._sendErrorReply(message, resource)
            
    def _createReplyTemplate(self, request, resource):
        '''Creates a reply message with common code for any reply
        
        :returns: CoapMessage Created reply
        '''
        msg             = CoapMessage()
        msg.address     = request.address
        msg.tokenLength = request.tokenLength
        msg.token       = request.token
        msg.codeClass   = resource.resultClass
        msg.codeDetail  = resource.resultCode
                                    
        if request.messageType == MessageType.CON:
            msg.messageType = MessageType.ACK
            msg.messageId   = request.messageId
        elif request.messageType == MessageType.NON:
            msg.messageType = MessageType.NON
            msg.messageId   = self._popMessageId()
        else:
            log.error('Sending Reset due to unexpected messageType: {0}', msg.messageType)
            msg.messageType = MessageType.RST
            msg.messageId   = request.messageId
            
        return msg
    
    def _sendGetReply(self, request, resource):
        '''Sends a reply to a GET request with the content for the provided resource.
        
        :param request: CoapMessage
        '''
        if not resource.resultClass:
            resource.resultClass = CodeClass.Success
            resource.resultCode  = SuccessResponseCode.Content

        msg         = self._createReplyTemplate(request, resource)
        msg.payload = bytearray(resource.value, soscoap.BYTESTR_ENCODING) \
                                    if resource.type == 'string' \
                                    else resource.value
                                    
        # Only add option for a string, and assume text-plain format.
        if resource.type == 'string':
            msg.addOption( CoapOption(OptionType.ContentFormat, MediaType.TextPlain) )
            
        self._msgSocket.send(msg)
    
    def _sendPostReply(self, request, resource):
        '''Sends a reply to a POST request confirming the changes.
        
        :param request: CoapMessage
        '''
        if not resource.resultClass:
            resource.resultClass = CodeClass.Success
            resource.resultCode  = SuccessResponseCode.Changed

        msg = self._createReplyTemplate(request, resource)
        
        self._msgSocket.send(msg)
    
    def _sendPutReply(self, request, resource):
        '''Sends a reply to a PUT request confirming the changes.
        
        :param request: CoapMessage
        '''
        if not resource.resultClass:
            resource.resultClass = CodeClass.Success
            resource.resultCode  = SuccessResponseCode.Changed

        msg = self._createReplyTemplate(request, resource)
        
        self._msgSocket.send(msg)
    
    def _sendErrorReply(self, request, resource):
        '''Sends a reply when an error has occurred in processing.
        
        :param request: CoapMessage
        :param resource: SosResourceTransfer
        '''
        msg             = self._createReplyTemplate(request, resource)
        msg.codeClass   = CodeClass.ServerError
        msg.codeDetail  = ServerResponseCode.InternalServerError
        
        self._msgSocket.send(msg)
        
    def _popMessageId(self):
        '''Returns the next sequential message ID, and increments'''
        nextid = self._nextMessageId
        self._nextMessageId = (self._nextMessageId+1 if self._nextMessageId < 0xFFFF 
                                                     else 1)
        return nextid
        
    def start(self):
        log.info('Starting asyncore loop')
        asyncore.loop()

