# Jeedom_Answerphone

   Introduction :

    Répondeur Jeedom : gère une file d'attente des messages Jeedom en mode client/serveur 
    afin de délivrer les message en TTS (Text To Speech) avec le plugin GoogleCast au moment ou une personne 
    est présente dans la pièce ou se trouve le Google Home via un scénario basé sur un simple détecteur
    de présence ou une reconnaissance de personnes ou de visages avec opencv.
    
    Il est possible de gérer plusieurs répondeurs. Le répondeur par défault porte le numéro 0
    
   Généralités :
   
    étape 1 : PUSH (push_message)
       Pour mettre en file d'attente les messages le python notification_client.py est appelé dans Jeedom 
       via le plugin de programmation script :
       /var/www/html/plugins/script/core/ressources/notification_client.py --push "#message#" "#title#"
       Il va solliciter les services du daemon notification_server.py sur le port 8085 pour lui demander
       de prendre en charge la gestion globale des messages.
       la zone Titre (#title#) permet de postionner des options tel que par exemple : --tag verrou_portail --replace
       la zone Message (#message#) sera exclusivement réservée au contenu du message.
   
    étape 2 : PULL (lecture_repondeur)
      Pour lire les messages on se base sur la détection de présence basé sur un simple capteur
      qui sollicite un scénario à partir d'un Evénement : #[PhilipsHue][Sensor séjour][Présence]#
      Voici le code pour déterminer s'il y des messages dans la file d'attente :
       ACTION CODE :
        $output=shell_exec('/var/www/html/plugins/script/core/ressources/notification_client.py --size 2>&1');
        $scenario->setData('return', $output);
       SI variable(return) == 0 ALORS stop
       SINON ACTION CODE :  
         $output=shell_exec('/var/www/html/plugins/script/core/ressources/notification_client.py --pull-all 2>&1');
         $output = html_entity_decode($output);
         $scenario->setData('return', $output);
        ACTION : #[GoogleCast][Salon Google Home][Parle !]# 
         Message : cmd=tts|value=variable(return)|speed=1.2|engine=gttsapi|voice=male|lang=fr-FR
   
   Toutes les options : 
   
    ./notification_client.py --help

    Usage1  : --push 'message' [--answerphone-number number] [--tag tag_name] [--priority number] [--replace] [--no-duplicate] [--expire seconds] [--no-timestamp]
    Usage2  : --pull           [--answerphone-number number] [--tag tag_name] [--priority number]
    Usage2  : --pull-all       [--answerphone-number number] [--tag tag_name] [--priority number] [--repull number]
    Usage4  : --size           [--answerphone-number number] [--tag tag_name] [--priority numner]
    Usage5  : --list           [--answerphone-number number] [--tag tag_name] [--priority number]
    Usage6  : --cancel         [--answerphone-number number] tag_name
    Usage7  : --list-all
    Usage9  : --purge
    Usage10 : --help
  
    Les options --cancel --replace --no-duplicate --expire permettent de gérer les messages dans la file d'attente.
    Il faut obligatoirement les associer avec un tag pour les options : --cancel --replace --no-duplicate
    
    L'option --list-all permet de voir l'historique et comment le message a été traité 
     (soit un read ou un cancel suite à un replace ou un expire):
      read=1 cancel=0 priority=0 expire=0 elapse=no_expire
      
    Par défaut chaque message est horodaté pour le jour de sa création (timestamp) 
    pour savoir à quelle heure le message a été créé : "à 10h30 vous avez reçu un colis dans la boite au lettre"
    --no-timestamp permet de ne pas préfixer le message par l'heure arrivée
    
    
   Exemples simple sans numéro de répondeur (par défaut 0) et sans tag :
    
     ./notification_client.py --push 'bonjour philippe'
        ==> met en attente un message sur le répondeur par défaut numéro 0 'bonjour philippe'
       
     ./notification_client.py --pull
       ==> retourne le message en attente sur le répondeur : ici 'bonjour philippe'
       
     ./notification_client.py --size
       ==> retourne la taille de la liste des messages en attente sur le répondeur numéro 1 pour le tag verrou_portail
       
     ./notification_client.py --list
       ==> retourne la liste des messages en attente sur le répondeur numéro 1 pour le tag verrou_portail
       
   Exemples avec un numéro de répondeur et un tag :
    
     ./notification_client.py --push 'le vérrou du portail est ouvert' --answerphone-number 1 --tag verrou_portail
       ==> met en attente un message sur le répondeur numéro 1 avec le tag verrou_portail
       
     ./notification_client.py --push 'le vérrou du portail est fermé' --answerphone-number 1 --tag verrou_portail --replace --expire 3600
       ==> replace le message en attente sur le répondeur numéro 1 avec le tag verrou_portail qui va expirer dans 1h (cancel)
    
     ./notification_client.py --cancel --answerphone-number 1 verrou_portail
       ==> annule tous les messages en attente sur le répondeur numéro 1 pour le tag verrou_portail
       
     ./notification_client.py --list --answerphone-number 1 --tag verrou_portail
       ==> retourne la liste des messages en attente sur le répondeur numéro 1 pour le tag verrou_portail
       
     ./notification_client.py --size --answerphone-number 1 --tag verrou_portail
       ==> retourne la taile de liste des messages en attente sur le répondeur numéro 1 pour le tag verrou_portail
       
   Exercise : utilisation du répondeur pour des citations venant de Kaamelott-Quote.py
   
    script à créer /var/www/html/plugins/script/core/ressources/Kaamelott-Quote.py avec le plugin jeeXplorer ou en session ssh.
   
    #!/usr/bin/env python3
    # coding: utf8
    import wikiquote
    import random
    Quote = random.choice(wikiquote.quotes(random.choice(wikiquote.search('Kaamelott',lang='fr')),lang='fr'))
    print(Quote.encode('ascii','xmlcharrefreplace'))
    
    ne pas oublier :
    
    chmod +x /var/www/html/plugins/script/core/ressources/Kaamelott-Quote.py
    
    Scénario dans Jeedom pour appeler Kaamelott-Quote.py:
    ACTION CODE :
      $output=shell_exec('/var/www/html/plugins/script/core/ressources/Kaamelott-Quote.py 2>&1');
      $output = ltrim($output, "b");
      $output = html_entity_decode($output);
      $scenario->setData('Quote', $output);
    ACTION : #[Communications][push_message][push]#   
      Titre : --no-timestamp --tag kaamelott --priority 1 --tag PHILIPPE
      Message :  variable(Quote)
      
      Le Google home diffusera la citation Kaamelott (TTS) uniquement au moment ou une personne sera présente dans la pièce.
   
   Exemple en ligen de commande dans une session ssh :

    ./notification_client.py --purge
    0

    ./notification_client.py --push bonjour
    1

    ./notification_client.py --list
    index=0 answerphone=0 2019-12-31 15:08:42 read=0 cancel=0 priority=0 expire=0 elapse=no_expire tag:notag message:|à 15h08 bonjour|
    1

    ./notification_client.py --size
    1

    ==> Jeedom read message (pull script) and cast in TTS mode via GoogleCast plugin on Google Home Mini (lecture_repondeur)

    ./notification_client.py --list
    empty

    ./notification_client.py --list-all
    index=0 answerphone=0 2019-12-31 15:08:42 read=1 cancel=0 priority=0 expire=0 elapse=no_expire tag:notag message:|à 15h08 bonjour|
    0


   Installation en session ssh de préférence ou alors avec le plugin jeeXplorer :

    * mkdir /root/daemon_server
    * Create /root/daemon_server/notification_server.py
    * Create /root/daemon_server/notification_client.py
    * chmod +x /root/daemon_server/notification_server.py /root/daemon_server/notification_client.py
    * Optional : Change port 8085 if you want in python code notification_server.py and notification_client.py
    * ln -s /root/daemon_server/notification_client.py /var/www/html/plugins/script/core/ressources/notification_client.py
    * Create /etc/systemd/system/notification_server.service
    * systemctl enable notification_server
    * systemctl start notification_server
    * Configurer Etape 1 PUSH et Etape 2 PULL dans Jeedom


   Debug : 

    * log here : /var/log/notifications.log
    * all messages are dumped here (csv format) : /var/tmp/notifications.dump
    Sample :
       #answer_number|timestamp_long|timestamp|read_timestamp_long|read_timestamp|read|cancel|priority|expire|tag|message|
       0|2019-12-31 15:08:42|1577801322|2019-12-31 15:09:33|1577801373|1|0|0|0|notag|à 15h08 bonjour|
       
       
       
