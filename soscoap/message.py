# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Provides CoapMessage and CoapOption classes, and functions to build a message 
from a raw byte array.
'''
import logging
import soscoap as coap

log = logging.getLogger(__name__)

class CoapOption(object):
    '''A CoAP message option.
    
    Attributes:
       :type:   OptionType metadata
       :value:  Application value parsed from bytestr if reading; or value
                to write if writing
       :length: int Length of value
    '''
    
    def __init__(self, optionType, value=None, length=0):
        self.type   = optionType
        self.value  = value
        self.length = length
            
    def __str__(self):
        return 'CoapOption( {0}, val: {1}, len: {2} )'.format(self.type.name, 
                                                              self.value,
                                                              self.length)
        
    def isPathElement(self):
        return self.type == coap.OptionType.UriPath


class CoapMessage(object):
    '''Modifiable representation of a CoAP message.
    
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
       :address:     address tuple 
       :version:     int CoAP version, defaults to 1
       :messageType: int :const:`soscoap.MessageType` enum value
       :tokenLength: int TKL value
       :codeClass:   int :const:`soscoap.CodeClass` enum value 
       :codeDetail:  int Enum value for :const:`soscoap.RequestCode`; or response 
                         code -- :const:`soscoap.SuccessResponseCode`, 
                         :const:`soscoap.ClientResponseCode`,
                         :const:`soscoap.ServerResponseCode`
       :messageId:   int Message ID
       :token:       str Token bytes, or None
       :options:     list CoapOption objects for this message
       :payload:     str Payload contents, or None
    
    .. [1] http://tools.ietf.org/html/draft-ietf-core-coap-18
    '''
    
    def __init__(self, address=None):
        self.address     = address
        self.version     = 1
        self.messageType = None
        self.tokenLength = 0
        self.codeClass   = 0
        self.codeDetail  = 0
        self.messageId   = 0
        self.token       = None
        self.options     = []
        self.payload     = None
            
    def __str__(self):
        return 'CoapMessage( t:{0} p:{1})'.format(
                                coap.MessageType._reverse[self.messageType],
                                self.absolutePath())
                                
    def absolutePath(self):
        '''Returns the full string path for the resource transferred in this message,
        or None if not present.
        '''
        relative = '/'.join([opt.value for opt in self.options if opt.isPathElement()])
        return '/' + relative if relative else None
        
    def lastOptionNumber(self):
        '''Returns the number of the last option in the options list.'''
        return self.options[-1].type.number if len(self.options) else 0
        
#
# Build functions
#

def buildFrom(bytestr, address=None):
    '''Creates a CoapMessage from a raw byte source.
    
    :param addr:    IPv6 address 4-tuple
    :param bytestr: Raw bytes comprising the message
    '''
    tooShortText = 'source byte string too short'
    if len(bytestr) < 4:
        raise RuntimeError(tooShortText)
        
    msg = CoapMessage(address)
    _readFixedBytes(msg, bytestr)
    pos = 4
    
    # read token
    if msg.tokenLength:
        if len(bytestr) < pos + msg.tokenLength:
            raise RuntimeError(tooShortText)
        msg.token = bytestr[pos : pos+msg.tokenLength]
        pos      += msg.tokenLength
    else:
        msg.token = None
        
    # read options and payload
    while pos < len(bytestr):
        if ord(bytestr[pos]) == 0xFF:
            if pos <= len(bytestr):
                # store payload
                pass
            else:
                # error if no options; expect payload after payload marker
                pass
        else:
            pos = _readOption(msg, bytestr, pos)
            
    return msg

def serialize(msg):
    '''Returns a CoAP-formatted bytearray for the provided message.
    '''
    # First four header bytes
    msgBytes    = bytearray(4)
    nextByte    = (msg.version     & 0x3) << 6
    nextByte   |= (msg.messageType & 0x3) << 4
    nextByte   |=  msg.tokenLength & 0xF
    msgBytes[0] = nextByte
    
    nextByte    = (msg.codeClass  & 0x0E) << 5
    nextByte   |=  msg.codeDetail & 0x1F
    msgBytes[1] = nextByte
    
    msgBytes[2] = (msg.messageId & 0xFF00) >> 8
    msgBytes[3] =  msg.messageId & 0xFF
    
    lastOptnum = 0   # supports encoding delta between option numbers
    for option in msg.options:
        headerByte  = ((option.type.number - lastOptnum) & 0xF) << 4
        headerByte |= option.length
        msgBytes.append(headerByte)
        lastOptnum  = option.type.number
        msgBytes.extend(option.value)
    
    # Payload
    if msg.payload:
        msgBytes.append(0xFF)
        # Assumes payload is a string
        msgBytes += msg.payload
    
    return msgBytes

def _readFixedBytes(msg, bytestr):
    '''Sets the CoapMessage attributes from the first four network bytes. Used to
    initially build the message.
    '''
    byte0 = ord(bytestr[0])
    byte1 = ord(bytestr[1])
    
    msg.version     = (byte0 & 0xC0) >> 6
    msg.messageType = (byte0 & 0x30) >> 4
    msg.tokenLength = (byte0 & 0x0F)
    msg.codeClass   = (byte1 & 0xE0) >> 5
    msg.codeDetail  = (byte1 & 0x1F)
    msg.messageId   = (ord(bytestr[2]) << 8) + ord(bytestr[3])
    
def _readOption(msg, bytestr, pos):
    '''Reads the next option from the network bytes, and appends it to the options
    for the provided CoapMessage. Used to initially build the message.
    
    :param pos: int Position of next byte in bytestr
    :return:    int Position of next byte after this option; may be past the end
                    of bytestr
    '''
    byte0 = ord(bytestr[pos])
    
    delta   = (byte0 & 0xF0) >> 4
    optlen  = (byte0 & 0x0F)
    optnum  = msg.lastOptionNumber() + delta
    bytepos = pos + 1 
    
    optionType = coap.OptionType._reverse[optnum]
    option     = CoapOption(optionType)
    
    if optionType == coap.OptionType.UriPath:
        option.value  = bytestr[bytepos : bytepos+optlen]
        option.length = optlen
    else:
        raise NotImplementedError('Option number {0} not implemented'.format(optnum))
    
    # OK to violate encapsulation because we're building the message privately.
    msg.options.append(option)
    log.debug('Found option {0} at pos {1}'.format(option, pos))
    
    return bytepos + optlen
