# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Definitions for CoAP constants. 

Enum values like MessageType also support reverse lookup. For example::

    MessageType._key[0] --> 'CON'
    
This capability means an enum key must *not* be '_key'.
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
    enums['_key'] = dict((value, key) for key, value in enums.iteritems())
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