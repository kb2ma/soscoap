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

log = logging.getLogger(__name__)

class SosResource(object):
    '''A RESTful application resource adapter for CoAP messaging. A resource is 
    an attribute of a host.
    
    Attributes:
        :path:    str URI path for the resource
        :value:   object Representation of the resource suitable for messaging
    '''
    
    def __init__(self, path, value=None):
        self.path    = path
        self.value   = value
            
    def __str__(self):
        return 'SosResource( {0}, val: {1} )'.format(self.path, self.value)
 