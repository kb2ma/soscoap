# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the Mozilla Public License 2.0, as published at the link below.
# http://opensource.org/licenses/MPL-2.0
'''
Tests for the msgsock module. The main issues are send and receive handling.
'''
import asyncore
from   flexmock import flexmock
import logging
import pytest
import socket
import soscoap as coap
from   soscoap import msgsock
from   soscoap import message as msgModule

logging.basicConfig(filename='test.log', level=logging.DEBUG, 
                    format='%(asctime)s %(module)s %(message)s')
log = logging.getLogger(__name__)
    

def createStubSocket():
    '''Common initialization for a mock socket.socket'''
    ssocket = flexmock(
        setblocking = lambda flag: None,
        fileno      = lambda: 0,
        bind        = lambda addr: None,
        close       = lambda: None)
    flexmock(socket.socket).new_instances(ssocket)
    return ssocket
    
def test_create_socket():
    createStubSocket()

    sock = msgsock.MessageSocket()
    
    assert sock != None
    assert sock.addr[0] == '::1'
    assert sock.addr[1] == 5683
    
def receiveTestReader(msg):
    '''Callback to verify test_receive() socket Receive event.'''
    assert msg.messageType == coap.MessageType.CON
    assert msg.codeDetail  == coap.RequestCode.GET
    assert msg.absolutePath()  == '/ver'
    
def test_receive():
    (createStubSocket()
        .should_receive('recvfrom')
        .and_return( ('\x40\x01\x6C\x29\xB3\x76\x65\x72', ('::1', 42683, 0, 0)) ))
    
    sock = msgsock.MessageSocket()
    sock.registerForReceive(receiveTestReader)
    # Cannot use the lower level asyncore.read(). It wraps an empty except handler, 
    # and so we cannot fail the test.
    sock.handle_read_event()
    
def verifySend(bytestr, address):
    '''Callback to verify test_send() socket send contents.'''
    assert address == ('::1', 42683, 0, 0)
    assert len(bytestr) == 8
    assert [b for b in bytestr[:2]] == [0x60, 0x45]
    
def test_send():
    (createStubSocket()
        .should_receive('sendto')
        .replace_with( lambda bytestr,addr: verifySend(bytestr,addr) ))

    sock = msgsock.MessageSocket()
        
    msg             = msgModule.CoapMessage()
    msg.address     = ('::1', 42683, 0, 0)
    msg.messageType = coap.MessageType.ACK
    msg.tokenLength = 0
    msg.codeClass   = coap.CodeClass.Success
    msg.codeDetail  = coap.SuccessResponseCode.Content
    msg.messageId   = 0
    msg.token       = 0
    msg.payload     = '0.1'

    sock.send(msg)
    # Cannot use the lower level asyncore.write(). It wraps an empty except handler, 
    # and so we cannot fail the test.
    sock.handle_write_event()
