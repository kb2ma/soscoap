# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Definitions for CoAP constants.

Includes a custom enum type to map a constant to a value. For example, the value 
of the code for a confirmable message type is an integer provided by the MessageType
enum::

    MessageType.CON --> 0

Enums also support reverse lookup via the '_key' attribute. For example::

    MessageType._key[0] --> 'CON'
    
The values for an enum may be traditional integers or objects. If the value is 
an object, the enum definition uses an enum-specific integer as the key for this 
reverse lookup. In addition, the reverse lookup returns the value object rather
then the enum key. For example::

    OptionType._key[11]   --> 'UriPath'
    OptionType._value[11] --> OptionType instance for OptionType.UriPath
'''
import logging

# Add NullHandler to package-level log to support a library user without a logging 
# setup.
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
        
pkglog = logging.getLogger(__name__)        
pkglog.addHandler(NullHandler())

def _enum(**enums):
    # If the enum values are objects, optionally include a '_reverseFunc' item 
    # whose value is a function that returns the key for a reverse lookup. For 
    # example, the OptionType enum uses a lambda expression to return the 'number' 
    # member of each CoapOption value.
    try:
        reverseFunc = enums['_reverseFunc']
    except KeyError:
        enums['_reverse'] = dict((value, key) for key, value in enums.iteritems())
    else:
        del enums['_reverseFunc']
        enums['_reverse'] = dict((reverseFunc(value), value) for value in enums.itervalues())
    
    return type('Enum', (), enums)


COAP_PORT = 5683

MessageType = _enum(CON=0, NON=1, ACK=2, RST=3)
'''Message type enum -- CON, etc.'''

CodeClass = _enum(Request=0, Success=2, ClientError=4, ServerError=5)
'''Message code class enum -- Request, etc.'''

RequestCode = _enum(GET=1, POST=2, PUT=3, DELETE=4)
'''Message code detail enum for requests (Class 0) -- GET, etc.'''

ResponseCode2 = _enum(Created=1, Deleted=2, Valid=3, Changed=4, Content=5)
'''Message code detail enum for Class 2 responses -- Created, etc.'''

ResponseCode4 = _enum(BadRequest=0, Unauthorized=1, BadOption=2, Forbidden=3,
                      NotFound=4, MethodNotAllowed=5, NotAcceptable=6, PreconditionFailed=12,
                      RequestEntityTooLarge=13, UnsupportedContentFormat=15)
'''Message code detail enum for Class 4 responses -- BadRequest, etc.'''

ResponseCode5 = _enum(InternalServerError=0, NotImplemented=1, BadGateway=2, 
                      ServiceUnavailable=3, GatewayTimeout=4, ProxyingNotSupported=5)
'''Message code detail enum for Class 5 responses -- InternalServerError, etc.'''
    
class OptionType(object):
    '''
    A type of CoAP Option as defined in section 5.4 of the spec. Provides metadata 
    about an option in a message.
    '''
    def __init__(self, number, name, repeatable, format, lengthRange, default):
        self.number       = number
        self.name         = name
        self.isRepeatable = repeatable
        self.valueFormat  = format
        self.lengthRange  = lengthRange
        self.defaultValue = default

#     Option arguments
#   Section 5.10 of spec       #    Name             R     Format   Length  Default
OptionType = _enum(
    _reverseFunc  = lambda opt: opt.number,
    IfMatch       = OptionType(1, 'If-Match',       True, 'opaque', (0,8),   None),
    UriHost       = OptionType(3, 'Uri-Host',       False,'string', (1,255), None),
    ETag          = OptionType(4, 'ETag',           True, 'opaque', (1,8),   None),
    IfNoneMatch   = OptionType(5, 'If-None-Match',  False,'empty',  (0,0),   None),
    UriPort       = OptionType(7, 'Uri-Port',       False,'uint',   (0,2),   None),
    LocationPath  = OptionType(8, 'Location-Path',  True, 'string', (0,255), None),
    UriPath       = OptionType(11,'Uri-Path',       True, 'string', (0,255), None),
    ContentFormat = OptionType(12,'Content-Format', False,'uint',   (0,2),   None),
    MaxAge        = OptionType(14,'Max-Age',        False,'uint',   (0,4),   60),
    UriQuery      = OptionType(15,'Uri-Query',      True, 'string', (0,255), None),
    Accept        = OptionType(17,'Accept',         False,'uint',   (0,2),   None),
    LocationQuery = OptionType(20,'Location-Query', True, 'string', (0,255), None),
    ProxyUri      = OptionType(35,'Proxy-Uri',      False,'string', (1,1034),None),
    ProxyScheme   = OptionType(39,'Proxy-Scheme',   False,'string', (1,255), None),
    Size1         = OptionType(60,'Size1',          False,'uint',   (0,4),   None),
)
'''OptionType enum -- If-Match, etc. Values are OptionType objects. Uses option 
   number for reverse lookup.'''
