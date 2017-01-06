#!/usr/bin/python
# Copyright (c) 2017, Ken Bannister
# All rights reserved. 
#  
# Released under the Mozilla Public License 2.0, as published at the link below.
# http://opensource.org/licenses/MPL-2.0
'''
Defines and runs a StatsReader to query statistics from the RIOT gcoap example.
Provides an example use of an SOS CoAP client.

Options:

-a <hostAddr> -- Host address to query
-q <query>  ---- Name of query to run. Options:
                   get -- Simple GET request
-s <port> ------ Source port from which to send query and listen for response

Run the reader on POSIX with:
   ``$PYTHONPATH=../.. ./stats_reader.py -s 5682 -a bbbb::1 -q get``
'''
from   __future__ import print_function
import logging
import asyncore
import sys
from   soscoap  import MessageType
from   soscoap  import RequestCode
from   soscoap  import COAP_PORT
from   soscoap.resource import SosResourceTransfer
from   soscoap.msgsock  import MessageSocket
from   soscoap.client   import CoapClient
from   threading import Timer
import time

logging.basicConfig(filename='reader.log', level=logging.DEBUG, 
                    format='%(asctime)s %(module)s %(message)s')
log = logging.getLogger(__name__)

VERSION = '0.1'

class StatsReader(object):
    '''Reads statistics from a RIOT gcoap URL.
    
    Attributes:
        :_hostAddr:  str Target for messages
        :_client:   CoapClient Provides CoAP message protocol
    
    Usage:
        #. sr = StatsReader(sourcePort, hostAddr)  -- Create instance
        #. sr.start() -- Sets timer to run the query
        *. sr.close() -- Cleanup
    '''
    def __init__(self, sourcePort, hostAddr):
        self._hostAddr = hostAddr
        self._client   = CoapClient(port=sourcePort)

    def start(self):
        '''Starts networking; returns when networking is stopped.'''
        self._client.start()

    def query(self, queryName):
        '''Runs a named query'''
        # create message
        # send message
        log.debug('Sending query')

    def close(self):
        '''Releases resources'''
        self._client.close()

# Start the reader
if __name__ == '__main__':
    formattedPath = '\n\t'.join(str(p) for p in sys.path)
    log.info('Running stats reader with sys.path:\n\t{0}'.format(formattedPath))

    from optparse import OptionParser

    # read command line
    parser = OptionParser()
    parser.add_option('-a', type='string', dest='hostAddr')
    parser.add_option('-s', type='int', dest='sourcePort', default=COAP_PORT)
    parser.add_option('-q', type='string', dest='query', default='')

    (options, args) = parser.parse_args()
    
    reader = None
    try:
        reader = StatsReader(options.sourcePort, options.hostAddr)
        if reader:
            # Setup query here since start() call doesn't return until the
            # reader is terminated.
            t = Timer(2, StatsReader.query, args=[ reader, options.query ])
            t.start()

            print('Starting stats reader')
            reader.start()
    except KeyboardInterrupt:
        pass
    except:
        log.exception('Catch-all handler for stats reader')
        print('\nAborting; see log for exception.')
    finally:
        if reader:
            reader.close()
            log.info('Reader closed')


