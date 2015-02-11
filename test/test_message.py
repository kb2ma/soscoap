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
from   soscoap import message as msgModule

logging.basicConfig(filename='test.log', level=logging.DEBUG, 
                    format='%(asctime)s %(module)s %(message)s')
log = logging.getLogger(__name__)

def test_FixedBytes():
    with pytest.raises(RuntimeError) as errobj:
        msgModule.buildFrom(bytestr=b'\x00\x00\x00')
        assert errobj == 'fixedBytes attribute too short'
        
# CON GET /ver
verGetMsg  = b'\x40\x01\x6C\x29\xB3\x76\x65\x72'
# CON GET /ver, with token 0x66 (ascii 'f')
tokenMsg   = b'\x41\x01\x6C\x29\x66\xB3\x76\x65\x72'
# NON PUT /ping with 2014,125
pingPutMsg = b'\x50\x03\x03\x17\xb4\x70\x69\x6e\x67\xff\x32\x30\x31\x34\x2c\x31\x32\x35'
# NON PUT /ping with 2014,125 with Content-Format text/plain
textContentPutMsg = b'\x50\x03\x03\x17\xb4\x70\x69\x6e\x67\x10\xff\x32\x30\x31\x34\x2c\x31\x32\x35'
# NON PUT /ping with 0x33 with Content-Format octet stream
binaryContentPutMsg = b'\x50\x03\x03\x17\xb4\x70\x69\x6e\x67\x11\x2a\xff\x33'
# NON POST /rss with Content-Format JSON
jsonContentPostMsg = b'\x51\x02\xe9\xe8\x7b\xb3\x72\x73\x73\x11\x32\xff\x7b\x22\x76\x22\x3a\x2d\x36\x39\x7d'

def test_option():
    '''Creates and queries a CoapOption'''
    msg = msgModule.CoapMessage()
    assert len(msg.options) == 0
    
    option = msgModule.CoapOption(coap.OptionType.ContentFormat, 0)
    assert option.type.number == 12
    assert option.value       == 0
    assert option.length      == 1
    
def test_simpleGet():
    '''Read GET request from bytes, and reserialize'''
    msg = msgModule.buildFrom(verGetMsg)
    
    assert msg.version     == 1
    assert msg.messageType == coap.MessageType.CON
    assert msg.tokenLength == 0
    assert msg.codeClass   == coap.CodeClass.Request
    assert msg.codeDetail  == coap.RequestCode.GET
    assert msg.messageId   == 27689  # 0x6C29
    assert msg.token       == None
    
    assert len(msg.options)     == 1
    assert msg.options[0].value == 'ver'
    
    assert msg.absolutePath()  == '/ver'
    
    assert msgModule.serialize(msg) == verGetMsg
    
def test_token():
    '''Read token in GET request from bytes, and reserialize'''
    msg = msgModule.buildFrom(tokenMsg)
    
    assert msg.token == b'\x66'
    assert msgModule.serialize(msg) == tokenMsg
    
def test_simplePut():
    '''Read PUT request from bytes, and reserialize'''
    msg = msgModule.buildFrom(pingPutMsg)
    
    assert msg.version     == 1
    assert msg.messageType == coap.MessageType.NON
    assert msg.tokenLength == 0
    assert msg.codeClass   == coap.CodeClass.Request
    assert msg.codeDetail  == coap.RequestCode.PUT
    assert msg.messageId   == 791  # 0x0317
    assert msg.token       == None
    
    assert len(msg.options)     == 1
    assert msg.options[0].value == 'ping'
    
    assert msg.payload == b'2014,125'
    
    assert msgModule.serialize(msg) == pingPutMsg
    
def test_contentFormat():
    '''Read content format in PUT request from bytes, and reserialize'''
    msg = msgModule.buildFrom(textContentPutMsg)
    
    assert len(msg.options)      == 2
    assert msg.options[0].type   == coap.OptionType.UriPath
    assert msg.options[1].type   == coap.OptionType.ContentFormat
    assert msg.options[1].value  == coap.MediaType.TextPlain

    assert msgModule.serialize(msg) == textContentPutMsg
    
def test_binaryContentFormat():
    '''Read binary content format in PUT request from bytes, and reserialize'''
    msg = msgModule.buildFrom(binaryContentPutMsg)
    
    assert len(msg.options)      == 2
    assert msg.options[0].type   == coap.OptionType.UriPath
    assert msg.options[1].type   == coap.OptionType.ContentFormat
    assert msg.options[1].value  == coap.MediaType.OctetStream
    
    assert msg.payload == b'\x33'

    assert msgModule.serialize(msg) == binaryContentPutMsg
        
def test_jsonContentFormat():
    '''Read JSON content format in POST request from bytes, and reserialize'''
    msg = msgModule.buildFrom(jsonContentPostMsg)
    
    assert len(msg.options)      == 2
    assert msg.options[0].type   == coap.OptionType.UriPath
    assert msg.options[1].type   == coap.OptionType.ContentFormat
    assert msg.options[1].value  == coap.MediaType.Json
    
    payload = msg.jsonPayload()
    assert 'v' in payload
    assert payload['v'] == -69

    assert msgModule.serialize(msg) == jsonContentPostMsg

def test_PayloadFormat():
    '''Reads payload based on Content-Format option'''
    msg = msgModule.buildFrom(textContentPutMsg)
    
    assert len(msg.options)      == 2

    optList = msg.findOption(coap.OptionType.ContentFormat)
    assert len(optList) == 1
    assert optList[0].type == coap.OptionType.ContentFormat

    assert msg.typedPayload() == '2014,125'