# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Provides CoapMessage and CoapOption classes. Provides functions to build a message 
from a raw byte array, and to serialize the message back out bytes.
'''
import functools
import json
import logging
import soscoap as coap
import sys
import numbers

log = logging.getLogger(__name__)
    
def int2buf(intVal, length):
    '''
    Creates a buffer with the hex values that represent the provided integer.
    
    :param intVal:    [in] integer to convert
    :param length:    [in] required buffer length
    :return:         Big endian list of integer bytes
    '''
    buf = [0] * length
    pos = length - 1
    while intVal > 0:
        if pos < 0:
            raise IndexError('buffer too short ({0})'.format(length))
        buf[pos] = intVal & 0xFF
        intVal   = intVal >> 8
        pos      = pos - 1
    return buf

class CoapOption(object):
    '''A CoAP message option.
    
    Attributes:
       :type:   OptionType metadata
       :value:  str, bytes/bytearray, or int - Application value read from a network
                message; or the value to write into a network message. Stored 
                as a plain str if the type stores a string; otherwise stored as 
                bytes/bytearray.
    '''
    
    def __init__(self, optionType, value=None):
        self.type   = optionType
        self.value  = value

        # Determine length
        if isinstance(value, numbers.Integral):
            self.length = 1 if value else 0
            value       = value >> 8
            while value > 0:
                self.length = self.length + 1
                value       = value >> 8
        else:
            self.length = len(value) if value else 0
            
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
       :address:     address tuple Stored as an optional convenience for lower
                     layers
       :version:     int CoAP version, defaults to 1
       :messageType: int :const:`soscoap.MessageType` enum value
       :tokenLength: int TKL value, defaults to 0
       :codeClass:   int :const:`soscoap.CodeClass` enum value 
       :codeDetail:  int Enum value for :const:`soscoap.RequestCode`; or response 
                         code -- :const:`soscoap.SuccessResponseCode`, 
                         :const:`soscoap.ClientResponseCode`,
                         :const:`soscoap.ServerResponseCode`
       :messageId:   int Message ID
       :token:       bytes/bytearray Token bytes, or None
       :options:     list CoapOption objects for this message; ordered by increasing
                          option number
       :payload:     bytes/bytearray Payload contents, or None
       
    Supported Option types:
       :UriPath:
       :ContentFormat:
    
    .. [1] http://datatracker.ietf.org/doc/rfc7252/

    .. automethod:: soscoap.message.CoapMessage.__init__
    '''
    
    def __init__(self, address=None):
        '''Minimally initializes a message.'''
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
        
    def payloadStr(self, text):
        '''Sets the payload from the provided string, using the default string 
        encoding.
        '''
        self.payload = bytearray(text, coap.BYTESTR_ENCODING)
        
    def strPayload(self):
        '''Returns the payload interpreted as a str.'''
        return str(self.payload) if sys.version_info.major == 2 \
          else str(self.payload, encoding=coap.BYTESTR_ENCODING)
        
    def jsonPayload(self):
        '''Returns the payload interpreted as JSON data.'''
        return json.loads(self.strPayload())
          
    def typedPayload(self):
        '''Returns the payload interpreted per the Content-Format option, or the 
        raw payload if no such option.
        '''
        cf = self.findOption(coap.OptionType.ContentFormat)
        if cf:
            if cf[0].value == coap.MediaType.TextPlain:
                return self.strPayload()
            elif cf[0].value == coap.MediaType.OctetStream:
                return self.payload
            elif cf[0].value == coap.MediaType.Json:
                return self.jsonPayload()
            else:
                raise NotImplementedError('MediaType {0} not implemented'.format(cf.value))
        else:
            return self.payload
        
    def lastOptionNumber(self):
        '''Returns the number of the last option in the options list.'''
        return self.options[-1].type.number if len(self.options) else 0
        
    def findOption(self, optionType):
        '''Returns the list of options for this message with the provided type, 
        or an empty list if not found.
        
        :param optionType: soscoap.OptionType
        '''
        return [o for o in self.options if o.type == optionType]
        
    def addOption(self, option):
        '''Adds an option to this message.
        
        :param option: soscoap.CoapOption the option to add
        '''
        # must insert in ascending option type order
        for (i,o) in enumerate(self.options):
            if o.type > option.type:
                self.options.insert(i, option)
                break;
        else:
            self.options.append(option)
        
#
# Build functions
#

def buildFrom(bytestr, address=None):
    '''Creates a CoapMessage from a raw byte source.
    
    :param bytestr: str Bytes comprising the message
    :param addr:    4-tuple IPv6 address
    '''
    tooShortText = 'source byte string too short'
    if len(bytestr) < 4:
        raise RuntimeError(tooShortText)
        
    msg     = CoapMessage(address)
    # Ensure we have a string of ordinals (Python3 bytes) for consistency
    msgords = bytearray(bytestr) if sys.version_info.major == 2 else bytestr
    _readFixedBytes(msg, msgords)
    log.debug('Building message for ID {0}'.format(msg.messageId))
    pos = 4
    
    # Read token
    if msg.tokenLength:
        if len(msgords) < pos + msg.tokenLength:
            raise RuntimeError(tooShortText)
        # TODO Test for excessive token length
        msg.token = msgords[pos : pos+msg.tokenLength]
        pos      += msg.tokenLength
    else:
        msg.token = None
        
    # Read options and payload
    while pos < len(msgords):
        if msgords[pos] == 0xFF:
            pos += 1
            if pos < len(msgords):
                msg.payload = msgords[pos : len(msgords)]
                pos         = len(msgords)
            else:
                raise NotImplementedError('Must generate a message format error')
        else:
            pos = _readOption(msg, msgords, pos)
            
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
    
    if msg.tokenLength:
        msgBytes.extend(msg.token)
    
    lastOptnum = 0   # supports encoding delta between option numbers
    for option in msg.options:
        delta = option.type.number - lastOptnum
        if (delta > 12):
            raise NotImplementedError('Option delta greater than 12')
        
        headerByte  = (delta & 0xF) << 4
        headerByte |= option.length
        msgBytes.append(headerByte)
        lastOptnum  = option.type.number
        log.debug('option.value type is {0}'.format(type(option.value)))
        if option.length > 0:
            if option.type.valueFormat == 'string':
                msgBytes.extend(bytearray(option.value, coap.BYTESTR_ENCODING))
            elif option.type.valueFormat == 'uint':
                msgBytes.extend(bytearray(int2buf(option.value, option.length)))
            else:
                raise NotImplementedError('Value format {0}'.format(option.type.valueFormat))
    
    if msg.payload:
        msgBytes.append(0xFF)
        msgBytes.extend(msg.payload)
    
    return msgBytes

def _readFixedBytes(msg, ords):
    '''Sets the CoapMessage attributes from the first four network bytes as ordinals.
    Used to initially build the message.
    '''
    msg.version     = (ords[0] & 0xC0) >> 6
    msg.messageType = (ords[0] & 0x30) >> 4
    msg.tokenLength = (ords[0] & 0x0F)
    msg.codeClass   = (ords[1] & 0xE0) >> 5
    msg.codeDetail  = (ords[1] & 0x1F)
    msg.messageId   = (ords[2] << 8) + ords[3]
    
def _readOption(msg, ords, pos):
    '''Reads the next option from the network bytes as ordinals, and appends it 
    to the options for the provided CoapMessage. Used to initially build the message.
    
    :param pos: int Position of next byte in ords
    :return:    int Position of next byte after this option; may be past the end
                    of bytestr
    '''
    delta = (ords[pos] & 0xF0) >> 4
    if (delta > 12):
        if (delta == 15):   # 0xF
            raise NotImplementedError(
                        'Message format error: Delta 15 but not payload marker')
        else:
            raise NotImplementedError('Option delta of 13 or 14')
    optlen  = ords[pos] & 0x0F
    optnum  = msg.lastOptionNumber() + delta
    bytepos = pos + 1 
    optval  = ords[bytepos : bytepos+optlen]
    
    optionType = coap.OptionType._reverse[optnum]
    
    option        = CoapOption(optionType)
    option.length = optlen
    
    if optionType == coap.OptionType.UriPath or optionType == coap.OptionType.UriHost:
        if optionType.valueFormat == 'string':
            option.value = _readOptionValue(optval, optionType.valueFormat)
        else:
            raise NotImplementedError('Option value must be string')
                
    elif optionType == coap.OptionType.ContentFormat:
        if optionType.valueFormat == 'uint':
            option.value = _readOptionValue(optval, optionType.valueFormat)
            try:
                coap.MediaType._reverse[option.value]
            except KeyError:
                log.warn('Content-Format undefined: {0}'.format(option.value))
        else:
            raise NotImplementedError('Option value must be uint')
                
    elif optionType == coap.OptionType.MaxAge:
        # TODO: Must add code to enforce this request
        if optionType.valueFormat == 'uint':
            option.value = _readOptionValue(optval, optionType.valueFormat)
        else:
            raise NotImplementedError('Option value must be uint')
                
    elif optionType == coap.OptionType.Observe:
        if optionType.valueFormat == 'uint':
            option.value = _readOptionValue(optval, optionType.valueFormat)
        else:
            raise NotImplementedError('Option value must be uint')
        
    else:
        raise NotImplementedError('Option number {0} not implemented'.format(optnum))
    
    # OK to violate encapsulation because we're building the message privately.
    msg.options.append(option)
    log.debug('Found option {0} at pos {1}'.format(option, pos))
    
    return bytepos + optlen
    
def _readOptionValue(value, format):
    if format == 'string':
        return str(value) if sys.version_info.major == 2 \
                           else str(value, coap.BYTESTR_ENCODING)
    elif format == 'uint':
        return functools.reduce(lambda sum, elem: (sum << 8) + elem, value, 0)
        
    else:
        raise NotImplementedError('Option format {0} not implemented'.format(format))
