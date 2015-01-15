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

class SosResourceTransfer(object):
    '''Provides application access to the resource being transferred between client
    and server. This transfer is the core of messaging.
    
    Attributes:
        :path:    str URI path for the resource
        :value:   object Representation of the resource suitable for messaging
        :type:    str Type of the value, using the same classification as 
                      soscoap.OptionType.valueFormat.
        :sourceAddress: str tuple, Address of the host that is the source of the 
                                   transfer.
        :resultClass:   CodeClass Type of outcome of the transfer
        :resultCode:    Detailed outcome of the transfer. The type depends on 
                        resultClass, and may be SuccessResponseCode, ServerResponseCode, 
                        or ClientResponseCode
    '''
    
    def __init__(self, path, value=None, resourceType=None, sourceAddress=None):
        self.path          = path
        self.value         = value
        self.type          = resourceType
        self.sourceAddress = sourceAddress
        self.resultClass   = None
        self.resultCode    = None
            
    def __str__(self):
        attrs = ', '.join(['{0}', 
                           'val: {1}', 
                           'type: {2}', 
                           'sourceAddress: {3}',
                           'resultClass: {4}',
                           'resultCode: {5}']).format(self.path,
                                                      self.value,
                                                      self.type,
                                                      self.sourceAddress,
                                                      self.resultClass,
                                                      self.resultCode)
        return 'SosResourceTranfer( ' + attrs + ' )'
 