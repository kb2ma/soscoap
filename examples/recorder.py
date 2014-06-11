#!/usr/bin/python
# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the Mozilla Public License 2.0, as published at the link below.
# http://opensource.org/licenses/MPL-2.0
'''
Defines and runs a ChannelRecorder for values received by a CoAP server. Provides
an example use of an SOS CoAP server.

Start the recorder on POSIX with:
   ``$PYTHONPATH=.. ./recorder.py``
'''
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

class ChannelRecorder(object):
    '''Records a channel of data for a provided URI. Records the data to a file.
    
    Attributes:
        :uripath:  str URI for channel
        :filename: str Name of target file for recording
        :_chanfile: File Recording target
        :_server:   CoapServer Provides CoAP message protocol
    
    Usage:
        #. cr = ChannelRecorder()  -- Create instance
        #. cr.start()  -- Starts to listen and record messages
        #. cr.close()  -- Releases sytem resources
    '''
    def __init__(self, uripath, filename):
        self.uripath  = uripath
        self.filename = filename
        
        self._server   = CoapServer()
        self._server.registerForResourceGet(self._getResource)
        
    def close(self):
        '''Releases system resources.
        '''
        if self._chanfile:
            self._chanfile.close() 
                
    def _getResource(self, resource):
        '''Sets the value for the provided resource.
        '''
        log.debug('Resource path is {0}'.format(resource.path))
        if resource.path == '/ver':
            resource.value = VERSION
            log.debug('Set resource value for /ver')
            
    def start(self):
        '''Creates the server, and opens the file for this recorder.
        
        :raises IOError: If cannot open file
        '''
        self._chanfile = open(self.filename, 'w')
        self._server.start()

# Start the recorder
if __name__ == '__main__':
    try:
        recorder = ChannelRecorder('/chan/example', 'example.txt')
        print 'Sock it to me!'
        recorder.start()
    except KeyboardInterrupt:
        pass
    except:
        log.exception('Catch-all handler for recorder')
    finally:
        recorder.close()
        log.info('Recorder closed')


