#!/usr/bin/env python3
# coding: utf8
#-------------------------------------------------------------
# Create  /root/daemon_server/notification_server.py
# Create /root/daemon_server/notification_client.py
#-------------------------------------------------------------
# Optional : Change port 8085 if you want in code here notification_server.py 
# and here notification_client.py
#-------------------------------------------------------------
# Create /etc/systemd/system/notification_server.service
# systemctl enable notification_server
# systemctl start notification_server
#------------------------------------------------------------

import socket
import traceback
import sys
from datetime import datetime

def log_write(msg):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log=open("/var/log/notifications.log","a+")
    log.write("client : \t\t\t\t %s : %s\n" % (dt,msg));
    #print("client : %s : %s" % (dt,msg))
    log.close()

sys.argv.pop(0)
log_write("len sys argv : %s" %len(sys.argv))

log_write("-----------------------")
log_write("%s" % str(sys.argv))
input_encoding=sys.stdin.encoding
log_write(sys.stdin.encoding)
log_write(sys.stdout.encoding)
codechar=sys.getdefaultencoding()
log_write(codechar)
if codechar == "ascii":
   log_write("Code : %s " % codechar)
else:
   log_write("Code : %s " % codechar)

clients_input=""
for i in range(0,len(sys.argv)):
   log_write("arg[%s] : %s" % (i,str(sys.argv[i])))
   if sys.argv[i] == "--help":
      print("Usage1 : --push 'message' [--answerphone-number number] [--tag tag_name] [--replace] [--priority 0|1] [--expire seconds] [--no-timestamp]")
      print("Usage2 : --pull           [--answerphone-number number] [--tag tag_name] [--priority 0|1]")
      print("Usage3 : --cancel         [--answerphone-number number] tag_name")
      print("Usage4 : --size           [--answerphone-number number] [--tag tag_name]")
      print("Usage5 : --list           [--answerphone-number number] [--tag tag_name]")
      print("Usage6 : --list-all")
      print("Usage7 : --purge")
      print("Usage8 : --help")
      break
   else:
      if clients_input == "":
         clients_input = str(sys.argv[i])
      else:
         clients_input = clients_input + " " + str(sys.argv[i])

log_write(type(clients_input))
log_write("Args: %s" % clients_input)

if clients_input != "":
   soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      soc.connect(("127.0.0.1", 8085))
      try:
         soc.send(clients_input.encode("utf8")) # we must encode the string to bytes
         log_write("send utf8: %s" % clients_input)
         result_bytes = soc.recv(4096) # the number means how the response can be in bytes
         if input_encoding == "UTF-8":
            result_string=result_bytes.decode("utf8") # the return will be in bytes, so decode
         else:
            result_string=result_bytes.decode("utf8").encode('ascii','xmlcharrefreplace').decode("utf8")
         log_write("%s" % str(result_string))
         # ANSI_X3.4-1968
         print(result_string)
      except:
         soc.send(clients_input) # we must encode the string to bytes
         log_write("send no utf8: %s" % clients_input)
   except:
      log_write("Socket 127.0.0.1:8085 connection error")
      traceback.print_exc()
else:
   print("Usage : --help")
