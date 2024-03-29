#!/usr/bin/env python3
# coding: utf8
#-------------------------------------------------------------
# philippeLC92 Version 1.0 Décembre 2019
#              Version 1.1 Décembre 2022
#-------------------------------------------------------------
# Installation :
# cd ~
# git clone https://github.com/myjdom/Jeedom_Answerphone.git
# cd Jeedom_Answerphone
# Optional : Change port 8085 if you want in python code notification_server.py and notification_client.py
# sudo mkdir /root/daemon_server
# sudo cp -p notification_server.py notification_client.py /root/daemon_server
# sudo chmod +x /root/daemon_server/notification_server.py /root/daemon_server/notification_client.py
# sudo cp -p notification_server.service /etc/systemd/system/notification_server.service
# sudo cp -p /root/daemon_server/notification_client.py /var/www/html/plugins/script/core/ressources/notification_client.py
# sudo chown www-data:www-data /var/www/html/plugins/script/core/ressources/notification_client.py
# sudo systemctl enable notification_server
# sudo systemctl start notification_server
# sudo systemctl status notification_server
#-----------------------------------------------------------------------------------------------------------------------
# Configurer Etape 1 PUSH et Etape 2 PULL dans Jeedom : voir README.md
#-----------------------------------------------------------------------------------------------------------------------

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

port=8085
clients_input=""
for i in range(0,len(sys.argv)):
   log_write("arg[%s] : %s" % (i,str(sys.argv[i])))
   if sys.argv[i] == "--help":
      print("Usage1  : --push 'message'  [--answerphone-number number] [--tag tag_name] [--priority number] [--replace] [--no-duplicate] [--expire seconds] [--no-timestamp]")
      print("Usage2  : --pull            [--answerphone-number number] [--tag tag_name] [--priority number]")
      print("Usage3  : --pull-all        [--answerphone-number number] [--tag tag_name] [--priority number] [--repull number] [--no-prefix] ")
      print("Usage4  : --get-all         [--answerphone-number number] [--tag tag_name] [--priority number] [--no-prefix]")
      print("                            as --pull-all but keep queued : to manage queue use --push with --replace or --cancel or --cancel-all")
      print("Usage5  : --size            [--answerphone-number number] [--tag tag_name] [--priority numner]")
      print("Usage6  : --list            [--answerphone-number number] [--tag tag_name] [--priority number]")
      print("Usage7  : --cancel tag_name [--answerphone-number number]")
      print("Usage8  : --cancel-all tag_name")
      print("Usage9  : --list-all")
      print("Usage10 : --purge")
      print("Usage11 : --help")
      break
   elif sys.argv[i] == "--port":
      try:
         i += 1
         port = int(sys.argv[i])
      except:
         pass
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
      soc.connect(("127.0.0.1", port))
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
      log_write("Socket 127.0.0.1:%s connection error" % port)
      traceback.print_exc()
else:
   print("Usage : --help")
