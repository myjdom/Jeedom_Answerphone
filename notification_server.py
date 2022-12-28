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

import sys
import os
import pwd
import grp
import socket
import traceback
import calendar
import time
from threading import Thread
from datetime import datetime

def log_write(msg):
   dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
   log_file="/var/log/notifications.log"
   log=open(log_file,"a+")
   log.write("server : %s : %s\n" % (dt,msg));
   print("server : %s : %s" % (dt,msg))
   log.close()
   os.chmod(log_file, 0o664)
   os.chown(log_file, pwd.getpwnam("www-data").pw_uid, grp.getgrnam("www-data").gr_gid)

def size_list(tag,answerphone_number):
   size=0
   if len(message_list) != 0:
      for index in range(len(message_list)):
         if read_status_list[index] == 0 and cancel_status_list[index] == 0:
            if (tag_list[index] == tag or tag == "unknown") and ((answerphone_number == -1 and answerphone_number_list[index] == 0) or (answerphone_number == answerphone_number_list[index])):
               size += 1
   log_write ("INFO : size return : %s" % size)
   return size

def push_and_pull(input_string):

    log_write ("INFO : input %s" % input_string)
    message=""
    push=0
    pull_one=0
    pull_all=0
    get_all=0
    list_queued=0
    list_all=0
    size=0
    cancel=0
    cancel_all=0
    tag="unknown"
    priority=-1
    timestamp=1
    expire=-1
    replace=0
    no_duplicate=0
    myreturn=0
    answerphone_number=-1
    repull=0
    prefix=1
    try:
       res = input_string.split(' ')
       totw=len(res)
    except:
       log_write ("ERROR : return input failed : -1")
       return "-1"
    #-----------------------------
    # cancel expire message
    #-----------------------------
    for index in range(len(message_list)):
       timestamp_sec=calendar.timegm(time.gmtime())
       elapse_time=timestamp_sec-timestamp_list[index]
       if elapse_time > int(expire_time_list[index]) and expire_time_list[index] != 0:
          cancel_status_list[index]=1
          log_write ("INFO : cancel expired message : %s read: %s cancel: %s timestamp: %ss expire: %ss elapse: %ss" % (index,read_status_list[index],cancel_status_list[index],timestamp_list[index],expire_time_list[index],elapse_time))

    i=0
    while i < totw:
       cmd = res[i]
       if cmd == "--list":
          list_queued=1; list_all=0; size=0; push=0; pull_one=0; pull_all=0; get_all=0; cancel=0; cancel_all=0; replace=0; no_duplicate=0
       if cmd == "--list-all":
          list_queued=0; list_all=1; size=0; push=0; pull_one=0; pull_all=0; get_all=0; cancel=0; cancel_all=0; replace=0; no_duplicate=0
       elif cmd == "--size":
          list_queued=0; list_all=0; size=1; push=0; pull_one=0; pull_all=0; get_all=0; cancel=0; cancel_all=0; replace=0; no_duplicate=0
       elif cmd == "--purge":
          list_queued=0; list_all=0; size=0; push=0; pull_one=0; pull_all=0; get_all=0; cancel=0; cancel_all=0; replace=0; no_duplicate=0
          del message_list[:]
          del timestamp_list[:]
          del timestamp_long_list[:]
          del read_timestamp_list[:]
          del read_timestamp_long_list[:]
          del expire_time_list[:]
          del read_status_list[:]
          del priority_list[:]
          del tag_list[:]
          del cancel_status_list[:]
          del answerphone_number_list[:]
          myreturn=str(len(message_list))
          break
       elif cmd == "--pull":
          list_queued=0; list_all=0; size=0; push=0; pull_one=1; pull_all=0; get_all=0; cancel=0; cancel_all=0; replace=0; no_duplicate=0
       elif cmd == "--get":
          list_queued=0; list_all=0; size=0; push=0; pull_one=0; pull_all=0; get_all=0; cancel=0; cancel_all=0; replace=0; no_duplicate=0
       elif cmd == "--pull-all":
          list_queued=0; list_all=0; size=0; push=0; pull_one=0; pull_all=1; get_all=0; cancel=0; cancel_all=0; replace=0; no_duplicate=0
       elif cmd == "--get-all":
          list_queued=0; list_all=0; size=0; push=0; pull_one=0; pull_all=0; get_all=1; cancel=0; cancel_all=0; replace=0; no_duplicate=0
       elif cmd == "--no-timestamp":
          list_queued=0; list_all=0; size=0; pull_one=0; pull_all=0; get_all=0; cancel=0; cancel_all=0; timestamp=0
       elif cmd == "--no-prefix":
          list_queued=0; list_all=0; size=0; cancel=0; cancel_all=0; prefix=0
       elif cmd == "--replace":
          list_queued=0; list_all=0; size=0; pull_one=0; pull_all=0; get_all=0; cancel=0; cancel_all=0; replace=1; no_duplicate=0
       elif cmd == "--no-duplicate":
          list_queued=0; list_all=0; size=0; pull_one=0; pull_all=0; get_all=0; cancel=0; cancel_all=0; replace=0; no_duplicate=1
       elif cmd == "--push":
          list_queued=0; list_all=0; size=0; push=1; pull_one=0; pull_all=0; get_all=0; cancel=0; cancel_all=0
       elif cmd == "--tag":
          cancel=0; cancel_all=0; list_all=0
          if i < totw-1:
             i += 1
             tag=res[i]
          else:
             log_write ("ERROR : cmd tag empty")
       elif cmd == "--answerphone-number":
          list_all=0
          if i < totw-1:
             i += 1
             answerphone_number=int(res[i])
          else:
             log_write ("ERROR : cmd answerphone number empty")
       elif cmd == "--cancel":
          list_queued=0; list_all=0; size=0; push=0; pull_one=0; pull_all=0; get_all=0; cancel=1; cancel_all=0; replace=0; no_duplicate=0
          if i < totw-1:
             i += 1
             tag=res[i]
          else:
             log_write ("ERROR : cmd tag empty")
       elif cmd == "--cancel-all":
          list_queued=0; list_all=0; size=0; push=0; pull_one=0; pull_all=0; get_all=0; cancel=1; cancel_all=1; replace=0; no_duplicate=0
          if i < totw-1:
             i += 1
             tag=res[i]
          else:
             log_write ("ERROR : cmd tag empty")
       elif cmd == "--priority":
          list_all=0; cancel=0; cancel_all=0
          if i < totw-1:
             i += 1
             priority=int(res[i])
          else:
             log_write ("ERROR : cmd priority empty")
       elif cmd == "--expire":
          list_queued=0; list_all=0; size=0; pull_one=0; pull_all=0; get_all=0; cancel=0; cancel_all=0
          if i < totw-1:
             i += 1
             expire=int(res[i])
          else:
             log_write ("ERROR : cmd expire time empty")
       elif cmd == "--repull":
          list_queued=0; list_all=0; size=0; push=0; pull_one=0; pull_all=1; get_all=0; cancel=0; cancel_all=0; replace=0; no_duplicate=0
          if i < totw-1:
             i += 1
             repull=int(res[i])
          else:
             log_write ("ERROR : repull number empty")
       else:
          if push == 1:
             if message == "":
                message = res[i]
             else:
                message = message + " " + res[i]
       i += 1
       #end while

    if message != "" and push == 1:
       log_write("INFO : message=%s" % message)
       add_message_queue=1
       if tag != "unknown" and replace == 1:
          if len(message_list) != 0:
             for index in range(len(message_list)):
                if tag_list[index] == tag and ((answerphone_number == -1 and answerphone_number_list[index] == 0) or (answerphone_number == answerphone_number_list[index])):
                   if read_status_list[index] == 0 and cancel_status_list[index] == 0:
                      cancel_status_list[index]=1
                      log_write ("INFO : message canceled to replace : %s read: %s cancel: %s timestamp: %s" % (index,read_status_list[index],cancel_status_list[index],timestamp_list[index]))
       if tag != "unknown" and no_duplicate == 1:
          if len(message_list) != 0:
             for index in range(len(message_list)):
                if tag_list[index] == tag and ((answerphone_number == -1 and answerphone_number_list[index] == 0) or (answerphone_number == answerphone_number_list[index])):
                   if read_status_list[index] == 0 and cancel_status_list[index] == 0:
                      add_message_queue=0
                      log_write ("INFO : message keep the original (no duplicate) : %s read: %s cancel: %s timestamp: %s" % (index,read_status_list[index],cancel_status_list[index],timestamp_list[index]))
       if add_message_queue == 1:
          if timestamp == 1:
             message = "à " + datetime.now().strftime('%Hh%M') + " " + message
          message_list.append(message.rstrip('\n'))
          timestamp_list.append(calendar.timegm(time.gmtime()))
          #tt=calendar.timegm(time.gmtime())
          timestamp_long_list.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
          if expire == -1:
             expire_time_list.append(0)
          else:
             expire_time_list.append(expire)
          if tag == "unknown":
             tag_list.append("notag")
          else:
             tag_list.append(tag)
          if priority == -1:
             priority_list.append(0)
          else:
             priority_list.append(priority)
          if answerphone_number == -1:
             log_write("ans set %s" % answerphone_number)
             answerphone_number_list.append(0)
          else:
             log_write("ans %s" % answerphone_number)
             answerphone_number_list.append(answerphone_number)
          read_timestamp_list.append(calendar.timegm(time.gmtime()))
          read_timestamp_long_list.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
          read_status_list.append(0)
          cancel_status_list.append(0)
          #index=len(message_list)-1
       myreturn=str(size_list(tag,answerphone_number))

    if pull_one == 1 or pull_all == 1 or get_all == 1 :
       myreturn="empty"
       total_messages=0
       if len(message_list) != 0:
          if repull == 0:
             for index in range(len(message_list)):
                if read_status_list[index] == 0 and cancel_status_list[index] == 0:
                   if (tag_list[index] == tag or tag == "unknown") and ((answerphone_number == -1 and answerphone_number_list[index] == 0) or (answerphone_number == answerphone_number_list[index])):
                      if priority_list[index] == priority or priority == -1:
                         if get_all != 1:
                             read_status_list[index]=1
                         read_timestamp_list[index]=calendar.timegm(time.gmtime())
                         read_timestamp_long_list[index]=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                         total_messages += 1
                         if pull_one == 1:
                            myreturn=message_list[index]
                            break
                         else:
                            if myreturn == "empty":
                               myreturn=message_list[index]
                            else:
                               myreturn=myreturn + " " + message_list[index]
             if (pull_all == 1 or get_all == 1) and total_messages>=1 and prefix == 1:
                myreturn="Vous avez " + str(total_messages) + " messages " + myreturn
          else:
             for index in reversed(range(len(message_list))):
                if read_status_list[index] == 1:
                   if (tag_list[index] == tag or tag == "unknown") and ((answerphone_number == -1 and answerphone_number_list[index] == 0) or (answerphone_number == answerphone_number_list[index])):
                      if priority_list[index] == priority or priority == -1:
                         total_messages += 1
                         if myreturn == "empty":
                            myreturn=message_list[index]
                         else:
                            myreturn=myreturn + " " + message_list[index]
                         repull += -1
                         if repull == 0:
                            break
             if total_messages>=1 and prefix == 1:
                myreturn="Vous avez " + str(total_messages) + " messages " + myreturn
       log_write ("INFO : pull return : %s" % myreturn)

    if cancel == 1:
       myreturn="empty"
       if len(message_list) != 0:
          for index in range(len(message_list)):
             if read_status_list[index] == 0 and cancel_status_list[index] == 0:
                if ((tag_list[index] == tag or tag == "unknown") and ((answerphone_number == -1 and answerphone_number_list[index] == 0) or (answerphone_number == answerphone_number_list[index]))) or (tag_list[index] == tag and cancel_all == 1):
                   cancel_status_list[index]=1
                   log_write ("INFO : message canceled : %s read: %s cancel: %s tag: %s priority: %s" % (index,read_status_list[index],cancel_status_list[index],tag,priority))
       myreturn=str(size_list(tag,answerphone_number))

    if list_queued == 1 or list_all == 1:
       myreturn="empty"
       if len(message_list) != 0:
          for index in reversed(range(len(message_list))):
             if (read_status_list[index] == 0 and cancel_status_list[index] == 0 and list_queued == 1) or list_all == 1:
                if (tag_list[index] == tag or tag == "unknown") and ((list_queued == 1 and ((answerphone_number == -1 and answerphone_number_list[index] == 0) or (answerphone_number == answerphone_number_list[index]))) or (list_all == 1 and (answerphone_number == -1 or answerphone_number == answerphone_number_list[index]))):
                   timestamp_sec=calendar.timegm(time.gmtime())
                   if expire_time_list[index] != 0:
                      elapse_time=timestamp_sec-timestamp_list[index]
                   else:
                      elapse_time="no_expire"
                   message=("index=%s answerphone=%s %s read=%s cancel=%s priority=%s expire=%s elapse=%s tag:%s message:|%s|" % (index,answerphone_number_list[index],timestamp_long_list[index],read_status_list[index],cancel_status_list[index],priority_list[index],expire_time_list[index],elapse_time,tag_list[index],message_list[index]))
                   if myreturn == "empty":
                      myreturn=message
                   else:
                      myreturn=message + "\n" + myreturn
                      #myreturn=message + " " + myreturn
       if myreturn != "empty":
         myreturn=myreturn + "\n" + str(size_list(tag,answerphone_number))
         #myreturn=myreturn + " " + str(size_list(tag,answerphone_number))

    if size == 1:
       myreturn=str(size_list(tag,answerphone_number))

    if len(message_list) != 0:
       dump_file="/var/tmp/notifications.dump"
       dump=open(dump_file,"w")
       message=("#answer_number|timestamp_long|timestamp|read_timestamp_long|read_timestamp|read|cancel|priority|expire|tag|message|\n")
       dump.write(message)
       for index in range(len(message_list)):
          message=("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n" % (answerphone_number_list[index],timestamp_long_list[index],timestamp_list[index],read_timestamp_long_list[index],read_timestamp_list[index],read_status_list[index],cancel_status_list[index],priority_list[index],expire_time_list[index],tag_list[index],message_list[index]))
          dump.write(message)
       dump.close()
       os.chmod(dump_file, 0o664)
       os.chown(dump_file, pwd.getpwnam("www-data").pw_uid, grp.getgrnam("www-data").gr_gid)

    log_write("INFO : push=%s pull_one=%s pull_all=%s get_all=%s repull=%s list_queued=%s list_all=%s size=%s cancel=%s tag=%s priority=%s timestamp=%s expire=%s replace=%s myreturn=%s answerphone_number=%s" % (push, pull_one, pull_all, get_all, repull, list_queued, list_all, size, cancel, tag, priority, timestamp, expire, replace, myreturn, answerphone_number))
    return str(myreturn)

def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 4096):

    # the input is in bytes, so decode it
    input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)

    # MAX_BUFFER_SIZE is how big the message can be
    # this is test if it's sufficiently big
    #import sys
    siz = sys.getsizeof(input_from_client_bytes)
    if  siz >= MAX_BUFFER_SIZE:
        log_write("ERROR : The length of input is probably too long: {}".format(siz))

    # decode input and strip the end of line
    input_from_client = input_from_client_bytes.decode("utf8").rstrip()

    res = push_and_pull(input_from_client)
    log_write("INFO : Result of processing {} is: {}".format(input_from_client, res))

    vysl = res.encode("utf8")  # encode the result string
    conn.sendall(vysl)  # send it to client
    conn.close()  # close connection
    log_write('INFO : Connection ' + ip + ':' + port + " ended")

def start_server():

    port=8085
    for i in range(0,len(sys.argv)):
       log_write("arg[%s] : %s" % (i,str(sys.argv[i])))
       if sys.argv[i] == "--port":
          try:
             i += 1
             port = int(sys.argv[i])
             break
          except:
             pass

    #import socket
    global answerphone_number_list, message_list, timestamp_list, timestamp_long_list, read_timestamp_long_list, read_timestamp_list, expire_time_list, tag_list, priority_list, read_status_list, cancel_status_list
    answerphone_number_list = list()
    message_list = list()
    timestamp_list = list()
    timestamp_long_list = list()
    read_timestamp_list = list()
    read_timestamp_long_list = list()
    expire_time_list = list()
    tag_list = list()
    priority_list = list()
    read_status_list = list()
    cancel_status_list = list()
    # reload data
    #timestamp_long|timestamp|read|cancel|priority|expire|tag|message|
    dump_file="/var/tmp/notifications.dump"
    index=0
    if os.path.isfile(dump_file) == True:
       with open(dump_file,"r") as file:
          for line in file:
             try:
                res = line.split('|')
                if res[0][0] != "#":
                   answerphone_number_list.append(int(res[0]))
                   timestamp_long_list.append(str(res[1]))
                   timestamp_list.append(int(res[2]))
                   read_timestamp_long_list.append(str(res[3]))
                   read_timestamp_list.append(int(res[4]))
                   read_status_list.append(int(res[5]))
                   cancel_status_list.append(int(res[6]))
                   priority_list.append(int(res[7]))
                   expire_time_list.append(int(res[8]))
                   tag_list.append(str(res[9]))
                   message_list.append(str(res[10]))
                   index += 1
                   log_write("INFO : dump file %s read line %s value %s" % (dump_file,index,res))
             except:
               log_write("WARNING : read format error file %s line %s" % (dump_file,index))
               traceback.print_exc()
          file.close()
    else:
        log_write("WARNING : file %s not found" % dump_file)

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this is for easy starting/killing the app
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    log_write('INFO : Socket created')

    try:
        soc.bind(("127.0.0.1", port))
        log_write('INFO : Socket bind complete')
    except socket.error as msg:
        #import sys
        log_write('ERROR : Bind failed. Error : ' + str(sys.exc_info()))
        sys.exit()

    #Start listening on socket
    soc.listen(10)
    log_write("INFO : Socket now listening 127.0.0.1:%s" % port )

    # for handling task in separate jobs we need threading
    #from threading import Thread

    # this will make an infinite loop needed for
    # not reseting server for every client
    while True:
        conn, addr = soc.accept()
        ip, port = str(addr[0]), str(addr[1])
        log_write('INFO : Accepting connection from ' + ip + ':' + port)
        try:
            Thread(target=client_thread, args=(conn, ip, port)).start()
        except:
            log_write("ERROR : Socket error")
            traceback.print_exc()
    soc.close()

#log_write("-----------------------")
#log_write("%s" % str(sys.argv))
#log_write(sys.stdin.encoding)
#log_write(sys.stdout.encoding)
#log_write(sys.getdefaultencoding())

start_server()
