# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the Mozilla Public License 2.0, as published at the link below.
# http://opensource.org/licenses/MPL-2.0
'''
Tests for the resource module.
'''
import logging
import pytest
from   soscoap import resource as rscModule

logging.basicConfig(filename='test.log', level=logging.DEBUG, 
                    format='%(asctime)s %(module)s %(message)s')
log = logging.getLogger(__name__)
        
def test_resource():
    '''Creates and queries an SosResourceTransfer'''
    rsc       = rscModule.SosResourceTransfer('/rsc/foo')
    rsc.value = 'bar'

    assert rsc.path == '/rsc/foo'
