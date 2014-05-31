# Copyright (c) 2014, Ken Bannister
# All rights reserved. 
#  
# Released under the GNU Library General Public License, version 3.0 (LGPLv3), 
# as published at the link below.
# http://opensource.org/licenses/LGPL-3.0
'''
Provides a simple event mechanism with the EventHook class.
'''
import logging

log = logging.getLogger(__name__)

class EventHook(object):
    '''A hook for generating and processing instances of a type of event. An event 
    consumer registers interest in the event type, and a producer triggers an 
    instance of the event.
    '''

    def __init__(self):
        self.__handlers = []

    def register(self, handler):
        self.__handlers.append(handler)

    def unregister(self, handler):
        self.__handlers.remove(handler)

    def clear(self):
        del self.__handlers[:]

    def trigger(self, *args, **kwargs):
        for h in self.__handlers:
            h(*args, **kwargs)
