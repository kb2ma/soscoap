# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the Mozilla Public License 2.0, as published at the link below.
# http://opensource.org/licenses/MPL-2.0
'''
Tests for the server module. The main issue is resource handling.
'''
from   __future__ import print_function
from   flexmock import flexmock
import logging
import pytest
import soscoap as coap
from   soscoap import message as msgModule

logging.basicConfig(filename='test.log', level=logging.DEBUG, 
                    format='%(asctime)s %(module)s %(message)s')
log = logging.getLogger(__name__)

# GET resources and testt

def getTestResource(resource):
    '''Callback for server ResourceGet event.'''
    assert resource.path == '/ver'
    resource.value = '0.1'

class MessageMatcher(object):
    '''For test_resource()'''
    def __eq__(self, target):
        return isinstance(target, msgModule.CoapMessage) \
                and target.messageType == coap.MessageType.ACK \
                and target.payload == '0.1'

def test_getResource():
    '''Tests use of a resource to handle an incoming CON GET request.'''
    mockMsgSocket = flexmock(
        registerForReceive = lambda handler: None,
        create_socket      = lambda family,type: None,
        bind               = lambda addr: None)

    mockMsgSocket.should_receive('send').with_args(MessageMatcher()).times(1)

    # Run
    # Must import server module here -- after definition of mock MessageSocket
    from soscoap import server as srvModule
    server = srvModule.CoapServer(mockMsgSocket)

    server.registerForResourceGet(getTestResource)
    
    msg = msgModule.buildFrom(b'\x40\x01\x6C\x29\xB3\x76\x65\x72', 
                              address=('::1', 42683, 0, 0))
    server._handleMessage(msg)

# PUT resources and test

def putTestResource(resource):
    '''Callback for server ResourcePut event.'''
    assert resource.path == '/ping'

class PutMessageMatcher(object):
    '''For test_resource()'''
    def __eq__(self, target):
        return isinstance(target, msgModule.CoapMessage) \
                and target.messageType == coap.MessageType.NON

def test_putResource():
    '''Tests handling an incoming NON PUT request.'''
    mockMsgSocket = flexmock(
        registerForReceive = lambda handler: None,
        create_socket      = lambda family,type: None,
        bind               = lambda addr: None)

    mockMsgSocket.should_receive('send').with_args(PutMessageMatcher()).times(1)
    
    # Run
    # Must import server module here -- after definition of mock MessageSocket
    from soscoap import server as srvModule
    server = srvModule.CoapServer(mockMsgSocket)
    server.registerForResourcePut(putTestResource)
    
    msg = msgModule.buildFrom(b'\x50\x03\x03\x17\xb4\x70\x69\x6e\x67\xff\x32\x30\x31\x34\x2c\x31\x32\x35', 
                              address=('::1', 42683, 0, 0))
    server._handleMessage(msg)
