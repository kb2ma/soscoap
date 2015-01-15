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
import sys

logging.basicConfig(filename='test.log', level=logging.DEBUG, 
                    format='%(asctime)s %(module)s %(message)s')
log = logging.getLogger(__name__)

formattedPath = '\n\t'.join(str(p) for p in sys.path)
log.info('Running test with sys.path:\n\t{0}'.format(formattedPath))

#
# GET resources and test
#

def getTestResource(resource):
    '''Callback for server ResourceGet event.'''
    assert resource.path == '/ver'
    resource.value = '0.1'

class MessageMatcher(object):
    '''For test_getResource()'''
    def __eq__(self, target):
        return (isinstance(target, msgModule.CoapMessage) 
                and target.messageType == coap.MessageType.ACK 
                and target.payload == '0.1')

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
    

def getErrorResource(resource):
    '''Callback for server ResourceGet event, for test_getError(). Generates error.'''
    assert resource.path == '/ver'
    raise KeyError

class ErrorMessageMatcher(object):
    '''Expecting error response for test_getError()'''
    def __eq__(self, target):
        return (isinstance(target, msgModule.CoapMessage)
                and target.messageType == coap.MessageType.ACK
                and target.codeClass   == coap.CodeClass.ServerError
                and target.codeDetail  == coap.ServerResponseCode.InternalServerError)

def test_getError():
    '''Tests generation of an error reply for an incoming CON GET request.'''
    mockMsgSocket = flexmock(
        registerForReceive = lambda handler: None,
        create_socket      = lambda family,type: None,
        bind               = lambda addr: None)

    mockMsgSocket.should_receive('send').with_args(ErrorMessageMatcher()).times(1)

    # Run
    # Must import server module here -- after definition of mock MessageSocket
    from soscoap import server as srvModule
    server = srvModule.CoapServer(mockMsgSocket)

    server.registerForResourceGet(getErrorResource)
    
    msg = msgModule.buildFrom(b'\x40\x01\x6C\x29\xB3\x76\x65\x72', 
                              address=('::1', 42683, 0, 0))
    server._handleMessage(msg)

#
# PUT resources and test
#

def putTestResource(resource):
    '''Callback for server ResourcePut event.'''
    assert resource.path == '/ping'

class PutMessageMatcher(object):
    '''For test_resource()'''
    def __eq__(self, target):
        return (isinstance(target, msgModule.CoapMessage) 
                and target.messageType == coap.MessageType.NON)

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

#
# POST resources and test
#

def postTestResource(resource):
    '''Callback for server ResourcePost event.'''
    assert resource.path == '/ping'

class PostMessageMatcher(object):
    '''For test_resource()'''
    def __eq__(self, target):
        return (isinstance(target, msgModule.CoapMessage) 
                and target.messageType == coap.MessageType.NON)

def test_postResource():
    '''Tests handling an incoming NON POST request.'''
    mockMsgSocket = flexmock(
        registerForReceive = lambda handler: None,
        create_socket      = lambda family,type: None,
        bind               = lambda addr: None)

    mockMsgSocket.should_receive('send').with_args(PostMessageMatcher()).times(1)
    
    # Run
    # Must import server module here -- after definition of mock MessageSocket
    from soscoap import server as srvModule
    server = srvModule.CoapServer(mockMsgSocket)
    server.registerForResourcePost(postTestResource)
    
    msg = msgModule.buildFrom(b'\x50\x02\xd0\x07\xb4\x70\x69\x6e\x67\xff\x32\x30\x31\x34\x2c\x31\x32\x35', 
                              address=('::1', 42683, 0, 0))
    server._handleMessage(msg)
