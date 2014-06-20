#!/usr/bin/python
# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the Mozilla Public License 2.0, as published at the link below.
# http://opensource.org/licenses/MPL-2.0
'''
Defines and runs a ValueRecorder for values received by a CoAP server. Provides
an example use of an SOS CoAP server.

Start the recorder on POSIX with:
   ``$PYTHONPATH=.. ./recorder.py``
'''
from   __future__ import print_function
import logging
import asyncore
import sys
from   soscoap  import MessageType
from   soscoap  import RequestCode
from   soscoap.resource import SosResource
from   soscoap.msgsock  import MessageSocket
from   soscoap.server   import CoapServer

logging.basicConfig(filename='recorder.log', level=logging.DEBUG, 
                    format='%(asctime)s %(module)s %(message)s')
log = logging.getLogger(__name__)

VERSION = '0.1'

class ValueRecorder(object):
    '''Records the values posted to a provided URI. Records the values to a file.
    
    Attributes:
        :uripath:  str URI for resource
        :filename: str Name of target file for recording
        :_chanfile: File Recording target
        :_server:   CoapServer Provides CoAP message protocol
    
    Usage:
        #. cr = ValueRecorder()  -- Create instance
        #. cr.start()  -- Starts to listen and record messages
        #. cr.close()  -- Releases sytem resources
    '''
    def __init__(self, uripath, filename):
        self.uripath  = uripath
        self.filename = filename
        
        self._server   = CoapServer()
        self._server.registerForResourceGet(self._getResource)
        self._server.registerForResourcePut(self._putResource)
        
    def close(self):
        '''Releases system resources.
        '''
        if self._chanfile:
            self._chanfile.close() 
                
    def _getResource(self, resource):
        '''Sets the value for the provided resource, for a Get request.
        '''
        log.debug('Resource path is {0}'.format(resource.path))
        if resource.path == '/ver':
            resource.type  = 'string'
            resource.value = VERSION
            log.debug('Got resource value')
        else:
            log.debug('Unknown path')
    
    def _putResource(self, resource):
        '''Records the value for the provided resource, for a Put request.
        
        :param resource.value: str ASCII in CSV format, with two fields:
                               1. int Time
                               2. int Value
        '''
        log.debug('Resource path is {0}'.format(resource.path))
        if resource.path == '/ping':
            self._chanfile.writelines((resource.value, '\n'))
            self._chanfile.flush()
            log.debug('Put resource value done')
        else:
            raise NotImplementedError('Unknown path')
    
    def start(self):
        '''Creates the server, and opens the file for this recorder.
        
        :raises IOError: If cannot open file
        '''
        self._chanfile = open(self.filename, 'w')
        self._server.start()

# Start the recorder
if __name__ == '__main__':
    recorder = None
    try:
        recorder = ValueRecorder('/ping', 'ping.txt')
        print('Sock it to me!')
        if recorder:
            recorder.start()
    except KeyboardInterrupt:
        pass
    except:
        log.exception('Catch-all handler for recorder')
        print('\nKnocked out :-(\nSee log for exception.')
    finally:
        if recorder:
            recorder.close()
            log.info('Recorder closed')


