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
   |                  stats -- GET /cli/stats
   | -s <port> -- Source port from which to send query and listen for
   |              response. Valuable for the Observe mechanism, where the
   |              server periodically sends responses.
   | -o           Register as an observer for the query

Run the reader on POSIX with:
   ``$ PYTHONPATH=../.. ./stats_reader.py -s 5682 -a fe80::bbbb:2%tap0 -q core``
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
from   soscoap.server   import CoapServer
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
        :_queryName: string GET query to send to CoAP server
    
    Usage:
        #. sr = StatsReader(hostAddr, hostPort, sourcePort, query)  -- Create instance
        #. sr.start() -- Starts asyncore networking loop
        #. sr.close() -- Cleanup
    '''
    def __init__(self, hostAddr, hostPort, sourcePort, query):
        '''Initializes on destination host and source port.'''
        self._hostTuple  = (hostAddr, hostPort)
        self._client     = CoapClient(sourcePort=sourcePort, dest=self._hostTuple)
        self._client.registerForResponse(self._responseClient)

        self._server     = CoapServer(port=5681)
        self._server.registerForResourcePost(self._postServerResource)

        self._queryName  = query

    def _responseClient(self, message):
        '''Reads a response to a request
        '''
        prefix   = '0' if message.codeDetail < 10 else ''
        obsList  = message.findOption(OptionType.Observe)
        obsValue = '<none>' if len(obsList) == 0 else obsList[0].value
        obsText  = 'len: {0}; val: {1}'.format(len(obsList), obsValue)
        
        print('Response code: {0}.{1}{2}; Observe {3}'.format(message.codeClass, prefix,
                                                              message.codeDetail, obsText))

    def _postServerResource(self, resource):
        '''Reads a command
        '''
        log.debug('Resource path is {0}'.format(resource.path))
        
        observeAction = None
        if resource.path == '/reg':
            observeAction = 'reg'
        elif resource.path == '/dereg':
            observeAction = 'dereg'

        self._query(observeAction)

    def _query(self, observeAction):
        '''Runs the reader's query

        :param observeAction: reg (register), dereg (deregister), or None;
                              triggers inclusion of Observe option
        '''
        # create message
        msg             = CoapMessage(self._hostTuple)
        msg.messageType = MessageType.NON
        msg.codeClass   = CodeClass.Request
        msg.codeDetail  = RequestCode.GET
        msg.messageId   = random.randint(0, 65535)
        msg.tokenLength = 2
        msg.token       = (0x35, 0x61)

        if self._queryName == 'core':
            msg.addOption( CoapOption(OptionType.UriPath, '.well-known') )
            msg.addOption( CoapOption(OptionType.UriPath, 'core') )
        elif self._queryName == 'stats':
            msg.addOption( CoapOption(OptionType.UriPath, 'cli') )
            msg.addOption( CoapOption(OptionType.UriPath, 'stats') )

        if observeAction == 'reg':
            # register
            msg.addOption( CoapOption(OptionType.Observe, 0) )
        elif observeAction == 'dereg':
            # deregister
            msg.addOption( CoapOption(OptionType.Observe, 1) )

        # send message
        log.debug('Sending query')
        self._client.send(msg)

    def start(self):
        '''Starts networking; returns when networking is stopped.

        Only need to start client, which automatically starts server, too.
        '''
        self._client.start()

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
    parser.add_option('-o', action='store_true', dest='isObserver', default=False)
    parser.add_option('-p', type='int', dest='hostPort', default=COAP_PORT)
    parser.add_option('-s', type='int', dest='sourcePort', default=COAP_PORT)
    parser.add_option('-q', type='string', dest='query', default='')

    (options, args) = parser.parse_args()
    
    reader = None
    try:
        reader = StatsReader(options.hostAddr, options.hostPort, options.sourcePort,
                                                                 options.query)
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


