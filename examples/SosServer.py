import asyncore, socket

COAP_PORT      = 5683
SOCKET_BUFSIZE = 1024

class SosServer(asyncore.dispatcher):
   def __init__(self):
      asyncore.dispatcher.__init__(self)

      self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.bind(('', COAP_PORT))

   # Even though UDP is connectionless this is called when it binds to a port
   def handle_connect(self):
      print "Server Started..."

   # This is called everytime there is something to read
   def handle_read(self):
      data, addr = self.recvfrom(SOCKET_BUFSIZE)
      print str(addr)+" >> "+data

   # This is called all the time and causes errors if you leave it out.
   def handle_write(self):
      pass

SosServer()
asyncore.loop()

