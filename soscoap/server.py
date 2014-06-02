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
import logging
import asyncore
from   event import EventHook
from   message import CoapMessage
from   soscoap import CodeClass
from   soscoap import MessageType
from   soscoap import RequestCode
from   soscoap import SuccessResponseCode
from   resource import SosResource
from   msgsock import MessageSocket

log = logging.getLogger(__name__)

class CoapServer(object):
    '''Server for CoAP requests. Requires a managing entity to define the resource 
    interface. This interface is defined as needed via events.
    
    Events:
        Register a handler for an event via the 'registerFor<Event>' method.
        
        :ResourceGet: Server requires the value for the provided resource to service
                      a GET request.
        
    Usage:
        #. cs = CoapServer() -- Create instance
        #. cs.registerForResourceGet() -- Register event handler
        #. cs.start() -- Starts to listen for requests
    '''
    def __init__(self):
        self.socket = MessageSocket()
        self.socket.registerForReceive(self._handleMessage)
        
        self._resourceGetHook = EventHook()
                
    def registerForResourceGet(self, handler):
        self._resourceGetHook.register(handler)
        
    def _handleMessage(self, message):
        if message.messageType == MessageType.CON:
            if message.codeDetail == RequestCode.GET:
                log.debug('Handling resource GET request...')
                # Get path and trigger resource event
                resource = SosResource(message.absolutePath, message=message)
                self._resourceGetHook.trigger(resource)
                self._sendReply(resource)
    
    def _sendReply(self, resource):
        request = resource.message
        
        msg             = CoapMessage()
        msg.messageType = MessageType.ACK
        msg.tokenLength = request.tokenLength
        msg.codeClass   = CodeClass.Success
        msg.codeDetail  = SuccessResponseCode.Content
        msg.messageId   = request.messageId
        msg.token       = request.token
        
        self.socket.send(msg)
        
    def start(self):
        log.info('Starting asyncore loop')
        asyncore.loop()

