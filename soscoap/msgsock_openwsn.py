# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Provides the MessageSocket class.
'''
import logging
import soscoap.message as msgModule
import soscoap
import soscoap.event as event
import sys

from   openvisualizer.eventBus  import eventBusClient
import openvisualizer.openvisualizer_utils as u
from pydispatch import dispatcher

log = logging.getLogger(__name__)
                
class MessageSocket(eventBusClient.eventBusClient):
    '''Source for network CoAP messages. Implemented as a select/poll-based socket,
    based on the the built-in asyncore module. Listens on the CoAP port for the
    loopback interface.
    
    Events:
        Register a handler for an event via the 'registerFor<Event>' method.
        
        :Receive: Triggered with the received CoAP message
    
    Attributes:
        :_receiveHook: EventHook Triggered when message received
    '''
    def __init__(self):
        '''Binds the socket to the CoAP port; ready to read'''
        
        self._receiveHook = event.EventHook()
        self._outgoing    = []
        
        # initialize parent class
        eventBusClient.eventBusClient.__init__(
            self,
            name                  = 'MessageSocket',
            registrations         =  [
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'networkPrefix',
                    'callback'    : self._networkPrefix_notif,
                },
                {
                    'sender'      : self.WILDCARD,
                    'signal'      : 'infoDagRoot',
                    'callback'    : self._infoDagRoot_notif,
                },
            ]
        )
        
        # local variables
        self._networkPrefix        = None
        self._dagRoot              = None
        self.PORT_COAP             = 5683
        self.PORT_COAP_BYTES       = msgModule.int2buf(self.PORT_COAP, 2)
        log.info('Created MessageSocket')
    
    def _networkPrefix_notif(self,sender,signal,data):
        '''
        Record the network prefix.
        '''
        # store
        self._networkPrefix    = data[:]
    
    def _infoDagRoot_notif(self,sender,signal,data):
        '''
        Record the DAGroot's EUI64 address.
        '''
        
        if not self._networkPrefix:
            log.error("infoDagRoot signal received while not have been assigned a networkPrefix yet")
            return

        # Had to remove this handling. It was being received *after* the handling
        # to register the dagroot.
        #if self._dagRoot and data['isDAGroot'] == 0:
        #    self.unregister(
        #        sender            = self.WILDCARD,
        #        signal            = (
        #            tuple(self._dagRoot),
        #            self.PROTO_UDP,
        #            (0x16, 0x33)     # port 5683
        #        ),
        #        callback          = self._fromMoteDataLocal_notif,
        #    )
        #    log.info("Unregistered DAGroot {0}".format(u.formatAddr(self._dagRoot)))
        #    self._dagRoot = None
            
        if data['isDAGroot'] == 1:
            self._dagRoot = self._networkPrefix + data['eui64'][:]
            
            self.register(
                sender            = self.WILDCARD,
                signal            = (
                    tuple(self._dagRoot),
                    self.PROTO_UDP,
                    self.PORT_COAP
                ),
                callback          = self._fromMoteDataLocal_notif,
            )
            log.info("Registered DAGroot {0}".format(u.formatAddr(self._dagRoot)))
        
    def registerForReceive(self, handler):
        self._receiveHook.register(handler)
    
    def _fromMoteDataLocal_notif(self,sender,signal,data):
        '''
        Called when receiving fromMote.data.local
        '''
        addr    = (data[0],)
        payload = data[1]
        
        if log.isEnabledFor(logging.DEBUG):
            hex_addr    = ' '.join(['{:02x}'.format(b) for b in addr[0]])
            bytestr     = bytearray(payload) if sys.version_info.major == 2 else payload
            hex_payload = ' '.join(['{:02x}'.format(b) for b in bytestr])
            log.debug('Receive message from {0}; data (hex) {1}'.format(hex_addr, hex_payload))
        else:
            hex_addr    = ' '.join(['{:02x}'.format(b) for b in addr[0]])
            log.info('Receive message from {0}'.format(hex_addr))
          
        coapmsg = msgModule.buildFrom(address=addr, bytestr=payload)
        self._receiveHook.trigger(coapmsg)
        return True
        
    def send(self, message):
        '''Puts the provided message on the outgoing queue for the next write
        opportunity.
        '''
        msgArray = msgModule.serialize(message)
        if log.isEnabledFor(logging.DEBUG):
            hex_addr = ' '.join(['{:02x}'.format(b) for b in message.address[0]])
            hexstr   = ' '.join(['{:02x}'.format(b) for b in msgArray])
            log.debug('Send message to {0}; data (hex) {1}'.format(hex_addr, hexstr))
        else:
            hex_addr = ' '.join(['{:02x}'.format(b) for b in message.address[0]])
            log.info('Send message to {0}'.format(hex_addr))

        # Write IPv6 and UDP headers, then send to pydispatch.
        udplen  = len(msgArray) + 8

        udp     = []
        udp    += self.PORT_COAP_BYTES          # src port
        udp    += self.PORT_COAP_BYTES          # dst port
        udp    += [udplen >> 8, udplen & 0xff]  # length
        udp    += [0x00,0x00]                   # checksum
        udp    += msgArray
        
        # CRC See https://tools.ietf.org/html/rfc2460.
      
        # not sure if the payload contains the udp header in this case.
        udp[6:8] = u.calculatePseudoHeaderCRC(
            src         = self._dagRoot,
            dst         = message.address[0],
            length      = [0x00,0x00]+udp[4:6],
            nh          = [0x00,0x00,0x00,17],
            payload     = msgArray,
        )
        
        # IPv6
        ip     = [6<<4]                  # v6 + traffic class (upper nybble)
        ip    += [0x00,0x00,0x00]        # traffic class (lower nibble) + flow label
        ip    += udp[4:6]                # payload length
        ip    += [17]                    # next header (protocol)
        ip    += [8]                     # hop limit (pick a safe value)
        ip    += self._dagRoot           # source
        ip    += message.address[0]      # destination
        ip    += udp

        if log.isEnabledFor(logging.DEBUG):
            hexstr   = ' '.join(['{:02x}'.format(b) for b in ip])
            log.debug('About to send message'.format(ip))

        self.dispatch(
            signal        = 'v6ToMesh',
            data          = ip,
        )
