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
   | -a <hostAddr> -- Host address to query
   | -q <query>  -- Name of query to run. Options:
   |                  core -- GET /.well-known/core
   | -s <port> -- Source port from which to send query and listen for
   |              response. Valuable for the Observe mechanism, where the
   |              server periodically sends responses.

Run the reader on POSIX with:
   ``$ PYTHONPATH=../.. ./stats_reader.py -s 5682 -a bbbb::1 -q core``
'''
from   __future__ import print_function
import logging
import asyncore
import random
import sys
from   soscoap  import CodeClass
from   soscoap  import MessageType
from   soscoap  import OptionType
from   soscoap  import RequestCode
from   soscoap  import COAP_PORT
from   soscoap.resource import SosResourceTransfer
from   soscoap.message  import CoapMessage
from   soscoap.message  import CoapOption
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

    NB: As shown in the Usage section below, StatsReader starts the asyncore
    loop before sending the query, like a server. This approach means the
    query must be called via another thread. Another approach would be to use
    asyncore's capabilities to create a single-use CoapClient and send the
    query at startup, in the same thread.
    
    Attributes:
        :_addrTuple:  tuple IPv6 address tuple for message destination
        :_client:   CoapClient Provides CoAP message protocol
    
    Usage:
        #. sr = StatsReader(sourcePort, hostAddr)  -- Create instance
        #. sr.start() -- Starts asyncore networking loop
        #. sr.query() -- Runs a named query. Must be called from a different
                         thread, for example from a timer.
        #. sr.close() -- Cleanup
    '''
    def __init__(self, hostAddr, hostPort, sourcePort):
        '''Initializes on destination host and source port.'''
        self._hostTuple = (hostAddr, hostPort)
        self._client    = CoapClient(sourcePort=sourcePort, dest=self._hostTuple)

    def start(self):
        '''Starts networking; returns when networking is stopped.'''
        self._client.start()

    def query(self, queryName):
        '''Runs a named query'''
        # create message
        msg             = CoapMessage(self._hostTuple)
        msg.messageType = MessageType.NON
        msg.codeClass   = CodeClass.Request
        msg.codeDetail  = RequestCode.GET
        msg.messageId   = random.randint(0, 65535)

        if queryName == 'core':
            msg.addOption( CoapOption(OptionType.UriPath, '.well-known') )
            msg.addOption( CoapOption(OptionType.UriPath, 'core') )
        
        # send message
        log.debug('Sending query')
        self._client.send(msg)

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
    parser.add_option('-p', type='int', dest='hostPort', default=COAP_PORT)
    parser.add_option('-s', type='int', dest='sourcePort', default=COAP_PORT)
    parser.add_option('-q', type='string', dest='query', default='')

    (options, args) = parser.parse_args()
    
    reader = None
    try:
        reader = StatsReader(options.hostAddr, options.hostPort, options.sourcePort)
        if reader:
            # Setup query here since start() call doesn't return until the
            # reader is terminated.
            t = Timer(2, StatsReader.query, args=(reader, options.query))
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


