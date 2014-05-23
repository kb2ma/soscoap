# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
import logging

# Add NullHandler to package-level log to support a library user without a logging 
# setup.
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
        
pkglog = logging.getLogger(__name__)        
pkglog.addHandler(NullHandler())

def _enum(**enums):
    return type('Enum', (), enums)

COAP_PORT = 5683

MsgType = _enum(CON=0, NON=1, ACK=2, RST=3)

