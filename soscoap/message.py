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
import soscoap

log = logging.getLogger(__name__)

class CoapMessage(object):
    '''
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
       version
    
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
    
    return msg

def readFixedBytes(msg, bytestr):
    '''Set the message object attributes from the first four raw bytes.'''
    msg.version     = (ord(bytestr[0]) & 0xc0) >> 6
    msg.messageType = (ord(bytestr[0]) & 0x30) >> 4
