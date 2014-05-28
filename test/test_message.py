# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the Mozilla Public License 2.0, as published at the link below.
# http://opensource.org/licenses/MPL-2.0
'''
Tests for the message module.
'''
import logging
import pytest
import soscoap as coap
from   soscoap import message

logging.basicConfig(filename='test.log', level=logging.DEBUG, 
                    format='%(asctime)s %(module)s %(message)s')
log = logging.getLogger(__name__)

def test_FixedBytes():
    with pytest.raises(RuntimeError) as errobj:
        message.buildFrom(bytestr='\x00\x00\x00')
        assert errobj == 'fixedBytes attribute too short'
        
# GET /ver
verGetMsg = '\x40\x01\x6C\x29\xB3\x76\x65\x72'

def test_simpleGet():
    msg = message.buildFrom(bytestr=verGetMsg)
    
    assert msg.version     == 1
    assert msg.messageType == coap.MessageType.CON
    assert msg.tokenLength == 0
    assert msg.codeClass   == coap.CodeClass.Request
    assert msg.codeDetail  == coap.RequestCode.GET
    assert msg.messageId   == 27689  # 0x6C29
    assert msg.token       == None
    
    assert msg.absolutePath()  == '/ver'
