# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Provides a CoapOption class.
'''
import logging
import soscoap as coap

log = logging.getLogger(__name__)

class CoapOption(object):
    '''An instance of a CoAP option.
    
    Attributes:
       :optionType: OptionType metadata
       :value:      Application value parsed from bytestr if reading; or value
                    to write if writing
    '''
    
    def __init__(self, optionType, value=None):
        self.optionType = optionType
        self.value      = value
            
    def __str__(self):
        return 'CoapOption( {0}, val: {1} )'.format(self.optionType.name, self.value)
        
    def isPathElement(self):
        return self.optionType == coap.OptionType.UriPath

