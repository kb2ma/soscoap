# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Provides a CoapMessage class, and functions to build an instance from a raw byte 
array.
'''
import logging
import soscoap as coap

log = logging.getLogger(__name__)

class CoapMessage(object):
    '''
    Modifiable representation of a CoAP message.
    
    Init Params:
       :useDefaults: Boolean to create a usable instance with default attributes 
                     where possible.
    
    CoAP message format [1]_::
    
         0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |Ver| T |  TKL  |      Code     |          Message ID           |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |   Token (if any, TKL bytes) ...
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |   Options (if any) ...
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |1 1 1 1 1 1 1 1|    Payload (if any) ...
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    
    Attributes:
       :version:     int CoAP version
       :messageType: int soscoap.MessageType enum value
       :tokenLength: int TKL value
       :codeClass:   int soscoap.CodeClass enum value 
       :codeDetail:  int soscoap.RequestCode or soscoap.ResponseCode[245]
       :messageId:   int Message ID
       :token:       str Token bytes, or None
    
    .. [1] http://tools.ietf.org/html/draft-ietf-core-coap-18
    '''
    
    def __init__(self, useDefaults=True):
        '''
        :param useDefaults: Boolean to create a useable instance with default
                            attributes where possible.
        '''
        if useDefaults:
            self.version     = 0
            self.messageType = None
            self.tokenLength = 0
            self.codeClass   = 0
            self.codeDetail  = 0
            self.messageId   = 0
            
    def __str__(self):
        return 'CoapMessage( t:{0} )'.format(coap.MessageType._key[self.messageType])

#
# Build functions
#

def buildFrom(bytestr, addr=None):
    '''
    Creates a CoapMessage from a raw byte source.
    
    :param addr:    IPv6 address 4-tuple
    :param bytestr: Raw bytes comprising the message
    '''
    if len(bytestr) < 4:
        raise RuntimeError('fixedBytes attribute too short')
        
    msg = CoapMessage(useDefaults=False)
    readFixedBytes(msg, bytestr)
    pos = 4
    if msg.tokenLength:
        msg.token = bytestr[pos : pos+msg.tokenLength]
        pos      += msg.tokenLength
    else:
        msg.token = None
    
    return msg

def readFixedBytes(msg, bytestr):
    '''Set the message object attributes from the first four raw bytes.'''
    byte0 = ord(bytestr[0])
    byte1 = ord(bytestr[1])
    
    msg.version     = (byte0 & 0xc0) >> 6
    msg.messageType = (byte0 & 0x30) >> 4
    msg.tokenLength = (byte0 & 0x0f)
    msg.codeClass   = (byte1 & 0xe0) >> 5
    msg.codeDetail  = (byte1 & 0x1f)
    msg.messageId   = (ord(bytestr[2]) << 8) + ord(bytestr[3])
