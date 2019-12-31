# Jeedom_Answerphone

###########################################################################################

    Répondeur Jeedom : gère une file d'attente des messages Jeedom en mode client/serveur 
    afin des délivrer en TTS avec GoogleCast au moment ou une personne est présente 
    dans la pièce ou se trouve le Google Home via un scénario 
    
    ./notification_client.py --help

    Usage1 : --push 'message' [--answerphone-number number] [--tag tag_name] [--replace] [--priority 0|1] [--expire seconds] [--no-timestamp]
    Usage2 : --pull           [--answerphone-number number] [--tag tag_name] [--priority 0|1]
    Usage3 : --cancel         [--answerphone-number number] tag_name
    Usage4 : --size           [--answerphone-number number] [--tag tag_name]
    Usage5 : --list           [--answerphone-number number] [--tag tag_name]
    Usage6 : --list-all
    Usage7 : --purge
    Usage8 : --help


###########################################################################################

    Sample :

    ./notification_client.py --purge
    0

    ./notification_client.py --push bonjour
    1

    ./notification_client.py --list
    index=0 answerphone=0 2019-12-31 15:08:42 read=0 cancel=0 priority=0 expire=0 elapse=no_expire tag:notag message:|à 15h08 bonjour|
    1

    ./notification_client.py --size
    1

    ==> Jeedom push message in TTS mode via GoogleCast plugin on Google Home Mini

    ./notification_client.py --list
    empty

    ./notification_client.py --list-all
    index=0 answerphone=0 2019-12-31 15:08:42 read=1 cancel=0 priority=0 expire=0 elapse=no_expire tag:notag message:|à 15h08 bonjour|
    0


###########################################################################################

    Installation :


    * Create  /root/daemon_server/notification_server.py
    * Create /root/daemon_server/notification_client.py
    * Optional : Change port 8085 if you want in code here notification_server.py and here notification_client.py
    * Create /etc/systemd/system/notification_server.service
    * systemctl enable notification_server
    * systemctl start notification_server


###########################################################################################

    Debug : 

    * log here : /var/log/notifications.log
    * all messages are dumped here (csv format) : /var/tmp/notifications.dump
    Sample :
       #answer_number|timestamp_long|timestamp|read_timestamp_long|read_timestamp|read|cancel|priority|expire|tag|message|
       0|2019-12-31 15:08:42|1577801322|2019-12-31 15:09:33|1577801373|1|0|0|0|notag|à 15h08 bonjour|
