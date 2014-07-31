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
from   soscoap import CodeClass
from   soscoap import MessageType
from   soscoap import RequestCode
from   soscoap import SuccessResponseCode
import soscoap
from   soscoap.event import EventHook
from   soscoap.message import CoapMessage
from   soscoap.resource import SosResource
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
   '''
    def __init__(self, msgSocket=None):
        '''Pass in msgSocket only for unit testing'''
        self._msgSocket = msgSocket if msgSocket else MessageSocket()
        self._msgSocket.registerForReceive(self._handleMessage)
        
        self._resourceGetHook  = EventHook()
        self._resourcePutHook  = EventHook()
        self._resourcePostHook = EventHook()
                
    def registerForResourceGet(self, handler):
        self._resourceGetHook.register(handler)
        
    def registerForResourcePost(self, handler):
        self._resourcePostHook.register(handler)
        
    def registerForResourcePut(self, handler):
        self._resourcePutHook.register(handler)
        
    def _handleMessage(self, message):
        resource = SosResource(message.absolutePath())

        if message.codeDetail == RequestCode.GET:
            log.debug('Handling resource GET request...')
            # Get path and trigger resource event
            self._resourceGetHook.trigger(resource)
            self._sendGetReply(message, resource)

        elif message.codeDetail == RequestCode.PUT:
            log.debug('Handling resource PUT request...')
            resource.value = message.typedPayload()
            self._resourcePutHook.trigger(resource)
            # TODO: Must distinguish Created case from Changed case.
            self._sendPutReply(message, resource, SuccessResponseCode.Changed)

        elif message.codeDetail == RequestCode.POST:
            log.debug('Handling resource POST request...')
            resource.value = message.typedPayload()
            self._resourcePostHook.trigger(resource)
            # TODO: Must distinguish Created case from Changed case.
            self._sendPostReply(message, resource, SuccessResponseCode.Changed)
            
    def _createReplyTemplate(self, request, resource):
        '''Creates a reply message with common code for any reply
        
        :returns: CoapMessage Created reply
        '''
        msg             = CoapMessage()
        msg.address     = request.address
        msg.tokenLength = request.tokenLength
        msg.messageId   = request.messageId
        msg.token       = request.token
                                    
        if request.messageType == MessageType.CON:
            msg.messageType = MessageType.ACK
        elif request.messageType == MessageType.NON:
            msg.messageType = MessageType.NON
        else:
            # Is this even possible?
            raise NotImplementedError('No reply if not a CON or NON request')
            
        return msg
    
    def _sendGetReply(self, request, resource):
        '''Sends a reply to a GET request with the content for the provided resource.
        
        :param request: CoapMessage
        '''
        msg             = self._createReplyTemplate(request, resource)
        msg.codeClass   = CodeClass.Success
        msg.codeDetail  = SuccessResponseCode.Content
        msg.payload     = bytearray(resource.value, soscoap.BYTESTR_ENCODING) \
                                    if resource.type == 'string' \
                                    else resource.value
        self._msgSocket.send(msg)
    
    def _sendPostReply(self, request, resource, resourceAction):
        '''Sends a reply to a POST request confirming the changes.
        
        :param request: CoapMessage
        :param resourceAction: soscoap.SuccessResponseCode -- Created or Changed
        '''
        msg             = self._createReplyTemplate(request, resource)
        msg.codeClass   = CodeClass.Success
        msg.codeDetail  = resourceAction
        
        self._msgSocket.send(msg)
    
    def _sendPutReply(self, request, resource, resourceAction):
        '''Sends a reply to a PUT request confirming the changes.
        
        :param request: CoapMessage
        :param resourceAction: soscoap.SuccessResponseCode -- Created or Changed
        '''
        msg             = self._createReplyTemplate(request, resource)
        msg.codeClass   = CodeClass.Success
        msg.codeDetail  = resourceAction
        
        self._msgSocket.send(msg)
        
    def start(self):
        log.info('Starting asyncore loop')
        asyncore.loop()

