# Omron Sensor Parameters

Programma sviluppato come Tesi di Laurea Triennale all'Università Degli Studi Della Basilicata del corso di studi in Scienze e Tecnologie Informatiche.

# Requisiti per eseguire Programma

Il programma seguente è stato sviluppato utilizzando un sensore Omron 2JCIE-BU01 per misurare parametri ambientali e una base Omron LD60 per gestire il problema SLAM tramite software proprietario Omron Mobile Planner. Sempre tramite la base comunicando tramite protocollo telnet preleviamo le coordinate del robot nell'ambiente.
Per la fase di memorizzazione utilizziamo un database relazionale di tipo PostgreSql , ma per quanto riguarda questo non esistono restrizioni precise sul tupi di database da utilizzare.

# File di Configurazione 

Nella cartella cfg sono presenti diversi file di configurazione per gestire concetti come login database , login telnet e parametri per creazione della mappa

# Installazione Programma

Il programma è stato testato su una versione di Ubunti 20.4 e una versione di ROS Noetic , quindi per un corretto utilizzo si consiglia di utilizzare le seguenti versioni.
Scaricato il repository nell'ambiente di lavoro ros si consiglia di utilizzare il comando catkin_make nella cartella radice dell'ambiente di lavoro.
Per le librerie utilizzate nel progetto vedere il file details.txt presente nella cartella del progetto

# Tabelle Database

Il formato delle tabelle create nel database si trovano in un file .sql della cartella di progetto in cui sono mostrati i comandi per creare le rispettive tabelle dei punti , misurazioni e giri.

