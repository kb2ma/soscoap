# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Provides a resource class.
'''
import logging
import soscoap as coap

log = logging.getLogger(__name__)

class SosResource(object):
    '''A RESTful application resource in CoAP messaging.
    
    Attributes:
        :path:    str URI path for the resource
        :value:   object Representation of the resource suitable for messaging
        :message: CoapMessage CoAP message relevant to the resource, for example
                  the message requesting the resource
    '''
    
    def __init__(self, path, value=None, message=None):
        self.path    = path
        self.value   = value
        self.message = message
            
    def __str__(self):
        return 'SosResource( {0}, val: {1} )'.format(self.path, self.value)
 