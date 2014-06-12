# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the Mozilla Public License 2.0, as published at the link below.
# http://opensource.org/licenses/MPL-2.0
'''
Tests for the server module. The main issue is resource handling.
'''
from   flexmock import flexmock
import logging
import pytest
import soscoap as coap
from   soscoap import message

logging.basicConfig(filename='test.log', level=logging.DEBUG, 
                    format='%(asctime)s %(module)s %(message)s')
log = logging.getLogger(__name__)

#def test_start():

def getTestResource(resource):
    '''Callback for server ResourceGet event.'''
    assert resource.path == '/ver'
    resource.value = '0.1'

class MessageMatcher(object):
    '''For test_resource()'''
    def __eq__(self, target):
        return isinstance(target, message.CoapMessage) \
                and target.messageType == coap.MessageType.ACK \
                and target.payload == '0.1'

def test_resource():
    '''Tests use of a resource to handle an incoming CON GET request.'''
    ssocket = flexmock(
        registerForReceive = lambda handler: None,
        create_socket      = lambda family,type: None,
        bind               = lambda addr: None)
    flexmock(coap.msgsock).should_receive('MessageSocket').and_return(ssocket)

    ssocket.should_receive('send').with_args(MessageMatcher())

    # Run
    # Must import server module here -- after definition of mock MessageSocket
    from soscoap import server as srvModule
    server = srvModule.CoapServer()
    server.registerForResourceGet(getTestResource)
    
    msg = message.buildFrom('\x40\x01\x6C\x29\xB3\x76\x65\x72', 
                            address=('::1', 42683, 0, 0))
    server._handleMessage(msg)
