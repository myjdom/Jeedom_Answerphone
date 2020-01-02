# Jeedom_Answerphone

    #-------------------------------------------------------------
    # philippeLC92 Version 1.0 Décembre 2019
    #-------------------------------------------------------------

https://community.jeedom.com/t/proposition-de-repondeur-jeedom/12781

# Introduction :

    Répondeur Jeedom : gère une file d'attente des messages Jeedom en mode client/serveur 
    afin de délivrer les message en TTS (Text To Speech) avec le plugin GoogleCast au moment ou une personne 
    est présente dans la pièce ou se trouve le Google Home via un scénario basé sur un simple détecteur
    de présence ou une reconnaissance de personnes ou de visages avec opencv.
    
    Il est possible de gérer plusieurs répondeurs. Le répondeur par défault porte le numéro 0
    
 # Généralités :
   
    Tout ce passe toujours en deux étapes :
   
   étape 1 : PUSH (push_message)
    
       Pour mettre en file d'attente les messages le python notification_client.py est appelé dans Jeedom 
       via le plugin de programmation script (c'est la méthode la plus simple pour un appel depuis les scénarios)
       Type script , action, message :
         /var/www/html/plugins/script/core/ressources/notification_client.py --push "#message#" "#title#"
       Il va solliciter les services du daemon notification_server.py sur le port 8085 pour lui demander
       de prendre en charge la gestion globale des messages.
       La zone Titre (#title#) permet de poistionner des options tel que par exemple : --tag verrou_portail --replace
       La zone Message (#message#) sera exclusivement réservée au contenu du message.
   
   étape 2 : PULL (lecture_repondeur)
    
      Pour lire les messages on se base sur la détection de présence basée sur un simple capteur
      qui sollicite un scénario à partir d'un Evénement : #[PhilipsHue][Sensor séjour][Présence]# par exemple.
      La reconnaissance des personnes avec une camera et opencv est une autre méthode de détection 
      qui permet une meilleure identification. Le scénario sera appelé dans ce cas avec les API de Jeedom
      (voir les exercises plus loin)
      Ce scénario sollicité par une présence utilise des blocs CODE de trois lignes de PHP 
      (c'est ce qui fonctionne le mieux pour ma part) :
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
         
# --help
   
    Toutes les options que l'on peut passer dans #TITLE# (le message étant passé obligatoirement dans #MESSAGE#): 
   
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
    --no-duplicate va éviter de remettre dans la file d'attente du répondeur une occurrence du même message tagué 
    avec la même valeur.
        
    L'option --list-all permet de voir l'historique et comment le message a été traité 
     (soit un read ou un cancel suite à un replace ou un expire):
     Exemple de valeurs pour un message :
      read=1 cancel=0 priority=0 expire=0 elapse=no_expire
      
    Par défaut chaque message est horodaté pour le jour courant de sa création (timestamp) 
    pour savoir à quelle heure le message a été créé.
    Exemple : "à 10h30 vous avez reçu un colis dans la boite au lettre"
    --no-timestamp permet de ne pas préfixer le message par l'heure arrivée 
    
    L'option --expire seconds donne une durée de vie au message et va permette de faire un cancel automatique.
    
    L'option --repull number avec --pull-all permet de retourner la liste des derniers messages qui ont été été lu.
    Il est interessant de réaliser une interaction et un scénario utilisant cette relecture du répondeur.
    
    L'option --priority number (valeur par défaut 0) peut être très utile pour donner une criticité relative aux messages.
    On peut ainsi lire les messages importants avant tous les autres pour les délivrer en priorité à la personne. 
    
    
# Exemples 

   Exemple simple sans numéro de répondeur (par défaut 0) et sans tag :
    
     ./notification_client.py --push 'bonjour philippe'
        ==> met en attente un message sur le répondeur par défaut numéro 0 'bonjour philippe'
       
     ./notification_client.py --pull
       ==> retourne le dernier message non lu en attente sur le répondeur : ici 'bonjour philippe'
       
     ./notification_client.py --pull-all
       ==> retourne tous les derniers messages non lu en attente sur le répondeur
       
       ./notification_client.py --pull-all --repull 4
       ==> retourne les quatre derniers messages déja lu sur le répondeur
       
     ./notification_client.py --size
       ==> retourne la taille de la liste des messages en attente de lecture sur le répondeur
       
     ./notification_client.py --list
       ==> retourne la liste des messages en attente de lecture sur le répondeur
       
   Exemples avec un numéro de répondeur et un tag :
    
     ./notification_client.py --push 'le verrou du portail est ouvert' --answerphone-number 1 --tag verrou_portail
       ==> met en attente un message sur le répondeur numéro 1 avec le tag verrou_portail
       
     ./notification_client.py --push 'le verrou du portail est fermé' --answerphone-number 1 --tag verrou_portail --replace --expire 3600
       ==> remplace le message en attente sur le répondeur numéro 1 avec le tag verrou_portail et va expirer dans 1h (cancel)
    
     ./notification_client.py --cancel --answerphone-number 1 verrou_portail
       ==> annule tous les messages en attente sur le répondeur numéro 1 avec le tag verrou_portail
       
     ./notification_client.py --list --answerphone-number 1 --tag verrou_portail
       ==> retourne la liste des messages en attente de lecture sur le répondeur numéro 1 pour le tag verrou_portail
       
     ./notification_client.py --size --answerphone-number 1 --tag verrou_portail
       ==> retourne la taille de liste des messages en attente sur le répondeur numéro 1 pour le tag verrou_portail
       
     ./notification_client.py --pull --answerphone-number 1 --tag verrou_portail
       ==> retourne le dernier message en attente de lecture sur le répondeur numéro 1 pour le tag verrou_portail
       
     ./notification_client.py --pull-all --answerphone-number 1 --tag verrou_portail
       ==> retourne tous les derniers messages en attente de lecture sur le répondeur numéro 1 pour le tag verrou_portail
       
# Exercises

   Exercise 1 : utilisation du répondeur pour des citations venant de Kaamelott-Quote.py
   
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
      
      ==> Jeedom va mettre une citation Kaamelott sur le répondeur pour le mettre en attente de lecture (étape 1 PUSH)
      ==> Puis Google home diffusera une citation Kaamelott (TTS) uniquement au moment ou une personne 
      sera présente dans la pièce (étape 2 PULL).
      
   Exercise 2 : utilisation du répondeur avec telegram
   
      L'idée est de déposer avec telegram un message sur le répondeur qui sera lu dès qu'une personne sera 
      présente dans la pièce du Google Home. 
      Ainsi à distance de votre domicile vous pouvez envoyer des messages en TTS.
        Sur telegram cela donne quelque chose comme ça :
        push je suis bloqué dans les transports et je serai en retard.
        retour : j'ai écrit sur le répondeur je suis bloqué dans les transports et je serai en retard.
        
      Pour cela vous devez créer une interaction que l'on va appeler "push" dans l'exemple.
      L'argument de push sera le contenu du message sur le répondeur :
      Demande : [écrit sur le répondeur|message|push] #value#
      Réponse : j'ai écrit sur le répondeur #value#
      Le scénario appelé sera :
      #[Communications][push_message][push]#
      Titre : --tag telegram --expire 3600
      Message : #value#
      
   Exercise 3 : détection des personnes avec opencv face recognition
   
    opencv (fonction face recognition) va permettre de déterminer le prénom de la personne qui sera utilisé comme tag 
    pour ne lire que les messages qui lui sont adressés.
       
    python3 opencv face recognition pour l'appel du scénario :
        #!/usr/bin/env python3
        .../...
        import cv2
        import face_recognition
        import numpy as np
        from tqdm import tqdm
        from collections import defaultdict
        from imutils.video import VideoStream
        .../...
        # interface avec JEEDOM
        URL_JEEDOM = "http://192.168.xxx.yyy/";
        API_KEY    = "xxxxxxxxxxxxxxxxxxxxxxxx";
        # connection
        URL=URL_JEEDOM+'/core/api/jeeApi.php'
        PHILIPPE={'apikey' : API_KEY , 'type' : 'scenario' , 'id' : 'zz', 'action' : 'start', 'tags' : 'HUMAN=PHILIPPE'}
        .../...
        # Detect faces
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(40, 40),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        # for each detected face
        for (x,y,w,h) in faces:
            # Encode the face into a 128-d embeddings vector
            encoding = face_recognition.face_encodings(rgb, [(y, x+w, y+h, x)])[0]
            # Compare the vector with all known faces encodings
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            # For now we don't know the person name
            name = "Unknown"
            # If there is at least one match:
            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1
                # determine the recognized face with the largest number of votes
                name = max(counts, key=counts.get)
                log_write("[LOG] human %s here" % name)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                y = y - 15 if y - 15 > 15 else y + 15
                cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
                if name == 'philippe.jpg':
                    try:
                        response = requests.post(URL, params=PHILIPPE)
                    except OSError:
                        #pass
                        log_write("Jeedom is offline")
        .../...    
   
   Création du scénario numéro zz appelé par le python3 opencv face recognition : OpenCV_Présence_Séjour_Lecture_Répondeur
   
    SI tag(HUMAN) == "PHILIPPE"
    ACTION CODE :
      $output=shell_exec('/var/www/html/plugins/script/core/ressources/notification_client.py --size --tag PHILIPPE 2>&1');
      $scenario->setData('return', $output);
    SI variable(return) != 0 ACTION CODE :
      $output=shell_exec('/var/www/html/plugins/script/core/ressources/notification_client.py --pull --tag PHILIPPE 2>&1');
      $output = html_entity_decode($output);
      $scenario->setData('return', $output);
      ACTION : 
       #[GoogleCast][Salon Google Home][Parle !]# 
       cmd=tts|value=PHILIPPE variable(return)|speed=1.2|engine=gttsapi|voice=male|lang=fr-FR
   
# CLI exemples

   Exemples en ligne de commande dans une session ssh :

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

# Installation 

   Installation en session ssh de préférence ou alors avec le plugin jeeXplorer :

    cd ~
    git clone https://github.com/myjdom/Jeedom_Answerphone.git
    cd Jeedom_Answerphone
    # Optional : Change port 8085 if you want in python code notification_server.py and notification_client.py
    sudo mkdir /root/daemon_server
    sudo cp -p notification_server.py notification_client.py /root/daemon_server
    sudo chmod +x /root/daemon_server/notification_server.py /root/daemon_server/notification_client.py
    sudo cp -p notification_server.service /etc/systemd/system/notification_server.service
    sudo ln -s /root/daemon_server/notification_client.py /var/www/html/plugins/script/core/ressources/notification_client.py
    sudo systemctl enable notification_server
    sudo systemctl start notification_server
    sudo systemctl status notification_server
    #-----------------------------------------------------------------------------------------------------------------------
    # Configurer Etape 1 PUSH et Etape 2 PULL dans Jeedom (vous devez être à l'aise avec Jeedom pour faire ces deux étapes)
    #-----------------------------------------------------------------------------------------------------------------------
    # Etape 1 :
    # je propose pour le push d'utiliser le plugin de programmation script car très facile à appelé dans les scénarios :
    # Type script, action, message : /var/www/html/plugins/script/core/ressources/notification_client.py --push "#message#" "#title#"
    # La zone Titre (#title#) permet de poistionner des options tel que par exemple : --tag verrou_portail --replace
    # La zone Message (#message#) sera exclusivement réservée au contenu du message.
    #-----------------------------------------------------------------------------------------------------------------------
    # Etape 2 :
    # Pour le pull il faut utiliser un scénario avec des blocs CODE de trois lignes de PHP 
    # (c'est ce qui fonctionne le mieux pour ma part).
    # le Scénario doit être sollicité par une présence ou appelé en API par opencv avec le numéro de scénario
    #   ACTION CODE :
    #    $output=shell_exec('/var/www/html/plugins/script/core/ressources/notification_client.py --size 2>&1');
    #    $scenario->setData('return', $output);
    #   SI variable(return) == 0 ALORS stop
    #   SINON ACTION CODE :  
    #     $output=shell_exec('/var/www/html/plugins/script/core/ressources/notification_client.py --pull-all 2>&1');
    #     $output = html_entity_decode($output);
    #     $scenario->setData('return', $output);
    #     ACTION : #[GoogleCast][Salon Google Home][Parle !]# 
    #       Message : cmd=tts|value=variable(return)|speed=1.2|engine=gttsapi|voice=male|lang=fr-FR
    #-----------------------------------------------------------------------------------------------------------------------

# Debug

    * log here : /var/log/notifications.log
    * all messages are dumped here (csv format) : /var/tmp/notifications.dump
    Sample :
       #answer_number|timestamp_long|timestamp|read_timestamp_long|read_timestamp|read|cancel|priority|expire|tag|message|
       0|2019-12-31 15:08:42|1577801322|2019-12-31 15:09:33|1577801373|1|0|0|0|notag|à 15h08 bonjour|
       
    ### THE END ###
       
