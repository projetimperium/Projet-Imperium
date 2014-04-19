# -*- coding: utf-8 -*-

import datetime
import time
from app import app, db, models

import xmltodict

import multiprocessing
import smtplib

import requests
import os
import math
import re

USE_SERIAL = True
PORT = None

if USE_SERIAL:
    import serial
    PORT = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=0)

LOG_WEATHER = True
WEATHER_URL = 'http://dd.weatheroffice.ec.gc.ca/citypage_weather/xml/NB/s0000654_e.xml'
LAST_WEATHER = 0

CMD_DIV = '|'
CMD_PREFIX = '<PI' + CMD_DIV
CMD_SPLIT = 'PI' + CMD_DIV
#example cmd: <PI|porte|unlock|tag1

try:
    GMAIL_USER,GMAIL_PASS = open('creds.txt','r').read().splitlines()
except:
    print 'Could not import gmail user/pass'
    GMAIL_USER,GMAIL_PASS = ('','')

class Notify():
    """
        Class Notify:
            - Responsable pour notifier par couriel s'il y a un warning
    """
    def __init__(self, subject, content):
        """
            :param subject: Le sujet du couriel
            :type subject: str
            :param content: Le contenu du couriel
            :type content: str
        """
        self.gUser = GMAIL_USER
        self.gPass = GMAIL_PASS

        self.subject = subject
        self.content = content

    def notifyByEmail(self):
        """
            Envoi des couriels selon a list de couriels
        """

        emails = [e.entry for e in self.getNotificationEntries() if e.nType == 'email']

        FROM = self.gUser
        TO = emails
        SUBJECT = self.subject
        TEXT = self.content

        # Prepare actual message
        message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        try:
            #server = smtplib.SMTP(SERVER)
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(self.gUser, self.gPass)
            server.sendmail(FROM, TO, message)
            server.close()
            print 'Message notification envoyer'
        except:
            print "Erreur: Message notification pas envoyer"

    def getNotificationEntries(self):
        """
            :returns: Tout les entrées de notifications
        """

        entries = models.Notification.query.all()
        return entries


class SerialMonitor(multiprocessing.Process):
    """
        Class SerialMonitor:
            - Responsable a lire le port serie pour des confirmations, warnings, data, etc.
            - Cette instance crée un nouveau processus pour ne pas intervenir avec le serveur web
    """
    def __init__(self, interval=3):
        """
            :param interval: Interval de temps a lire de port serie
            :type interval: int
        """
        super(SerialMonitor, self).__init__()
        self.PI = None
        self.interval = interval
        self.dataHandler = DataHandler()

    def onReceiveLine(self, rawLine):
        """
            Une ligne de commande a été reçu sur le port serie.
            La ligne est ensuite analyser selon le format: <PI|module|commande|param

            :param rawLine: Ligne de commande
            :type rawLine: str
        """

        toks = rawLine[len(CMD_SPLIT):].split(CMD_DIV)

        if len(toks) < 2:  # prefix + module
            return False

        fromModule = toks[0]
        cmd = toks[1]
        params = toks[2:]

        recvMsg = 'Module: {} Command: {} Params: {}' \
            .format(fromModule, cmd, str(params))
        logMsg = 'Command {} de {} avec parametre {}'.format(cmd, fromModule, ','.join(params))
        if cmd == 'warning':
            logMsg = 'WARNING: ' + params[0]
            n = Notify('WARNING', params[0])
            n.notifyByEmail()

        # wattmetre
        if cmd == "power":
            V, I, P_s, P_a, P_f, freq = params[0:6]
            I = float(I)/1000; # amps
            self.dataHandler.logPower(V, I, P_s, P_a, P_f, freq)



        self.PI.log(logMsg)
        #print recvMsg

    def run(self):
        """
            Début du Serial Monitor

            Lecture du port serial a un interval déterminer.
            Si une commande est reçu, la fonction onReceiveLine() est appelé
        """
        while True:
            recv = PORT.readline()
            for r in recv.split('<'):
                if r.startswith(CMD_SPLIT):
                    self.onReceiveLine(r)

            time.sleep(self.interval)


class Module():
    """
        Class Module:
            - Responsable de la gestion d'un sous-modules
            - Instances initializer par la class Imperium
    """
    def __init__(self, mId, slugName, name, description=''):
        """
            :param mId: Id du module
            :type mId: int
            :param slugName: Nom court pour le module
            :type slugName: str
            :param name: Nom du module
            :type name: str
            :param description: Description du module
            :type description: str
        """
        self.mId = mId
        self.slugName = slugName
        self.name = name
        self.description = description

        self.data = dict()

    def getDict(self):
        """
            {mId,slugName,name,description}

            :returns: Dictionnaire de valeurs du module
        """
        return {
            'mId': self.mId,
            'slugName': self.slugName,
            'name': self.name,
            'description': self.description
        }

    def sendCommand(self, cmd):
        """
            Envoi d'une commande au module

            :param cmd: Commande a envoyer. Par defaut, un préfix s'ajouteras a la command.
            :type cmd: str

            Pour envoyer une commande sans le préfix, raw:<commande>
        """
        if cmd.startswith('raw:'):
            cmdSend = cmd[4:]
        else:
            cmd = cmd.replace(' ', CMD_DIV)
            cmdSend = '{prefix}{module}{div}{cmd}' \
                .format(prefix=CMD_PREFIX, div=CMD_DIV, module=self.slugName, cmd=cmd)
        logMsg = 'Envoi de la command {} au module {}'.format(cmd, self.name)
        app.control.log(logMsg)
        if USE_SERIAL:
            PORT.write(cmdSend)

        print cmdSend
        return logMsg

    def getStatus(self):
        """
            TODO

            Envoi un PING au module, attend pour une réponse PONG
            :returns: True si la réponse est reçu
        """
        pass


class DataHandler():
    """
        Class DataHandler
            - Responsable pour la gestion des données des sous-modules
    """

    def __init__(self):
        pass

    def logPower(self, V, I, P_s, P_a, P_f, freq):
        timestamp = self.getTimestamp()
        angle = math.acos(float(P_f))
        P_q = float(P_s) * float(math.sin(angle))

        # Tension
        db.session.add(models.Data(
        entryType='wattmetre-V',
        entryName='Tension (V)',
        entryData=str(V),
        entryDate=timestamp))
        # Courant
        db.session.add(models.Data(
        entryType='wattmetre-I',
        entryName='Courant (A)',
        entryData=str(I),
        entryDate=timestamp))
        # Power S
        db.session.add(models.Data(
        entryType='wattmetre-S',
        entryName='Puissance S (VA)',
        entryData=str(P_s),
        entryDate=timestamp))
        # Power A
        db.session.add(models.Data(
        entryType='wattmetre-W',
        entryName='Puissance A (W)',
        entryData=str(P_a),
        entryDate=timestamp))
        # Power Q
        db.session.add(models.Data(
        entryType='wattmetre-Q',
        entryName='Puissance Q (VAR)',
        entryData=str(P_q),
        entryDate=timestamp))
        # Power factor
        db.session.add(models.Data(
        entryType='wattmetre-Pf',
        entryName='Facteur de puissance',
        entryData=str(P_f),
        entryDate=timestamp))
        # Frequence
        db.session.add(models.Data(
        entryType='wattmetre-freq',
        entryName='Frequence (Hz)',
        entryData=str(freq),
        entryDate=timestamp))


        db.session.commit()
        self.logTemperature(timestamp)

    def getTimestamp(self):
        """
            :returns: int, temps unix
        """
        d = datetime.datetime.now()
        return time.mktime(d.timetuple())

    def logTemperature(self, timestamp):
        """
            Vas chercher la température de dd.weatheroffice.ec.gc.ca
            et l'insert dans la base des données
        """
        if LOG_WEATHER:
            global LAST_WEATHER
            try:
                xmlData = requests.get(WEATHER_URL).text

                weatherDict = xmltodict.parse(xmlData)
                currentCond = weatherDict['siteData']['currentConditions']
                currentTemp = currentCond['temperature']['#text']
            except:
                currentTemp = LAST_WEATHER

            print 'Current temperature: ' + currentTemp

            d = models.Data(
                entryType='temperature',
                entryName='Temperature Moncton (C)',
                entryData=str(currentTemp),
                entryDate=timestamp)
            db.session.add(d)
            db.session.commit()
            LAST_WEATHER = currentTemp

    def formatAsDict(self, entries, entryType, entryName):
        """
            Prend les données et fait un dictionnaire en format pour le graph Flot

            :param entries: Entrées de la base de données
            :type entries: models.Data
            :param entryType: Le type d'entrée (wattmetre, temperature, etc)
            :type entryType: str
            :param entryName: Le nom (label) des données sur le graph
            :type entryName: str


            :returns: dict
        """
        obj = dict()
        obj[entryType] = dict()
        obj[entryType]['label'] = entryName
        obj[entryType]['data'] = []
        for entry in entries:
            obj[entryType]['data'].append([float(entry.entryDate) * 1000, entry.entryData])

        return obj

    def getAllData(self, entryType, asDict=False):
        """
            :param entryType: Le type de données a chercher
            :type entryType: str
            :param asDict: Retour un dictionnaire en format Flot
            :type asDict: bool
            :returns: list(models.Data) ou dict()
        """
        entries = list(models.Data.query.filter_by(entryType=entryType))
        if entries:
            if asDict:
                return self.formatAsDict(entries, entryType, entries[0].entryName)
            else:
                return entries
        else:
            return dict()


class Imperium(object):
    """
        Class Imperium:
            - Responsable pour la gestion des sous-modules
            - Contient une référence au SerialMonitor
            - L'ajout d'entrée au server log
    """

    def __init__(self):
        self.modules = set()
        self.startTime = time.time()
        self.loadModules()

        self.dataHandler = DataHandler()

        # thread.start_new_thread(logTemp,()) #  temperature logging test

        if USE_SERIAL:
            self.serialMonitor = SerialMonitor()
            self.serialMonitor.PI = self
            self.serialMonitor.start()

    def getUptimeStr(self):
        """
            :returns: String - Durée de fonctionnent du serveur
        """
        d = datetime.timedelta(seconds=(time.time() - self.startTime))
        return str(d).split('.')[0]

    def getModuleFromSlugName(self, slugName):
        """
            Obtenir l'instance d'un module a partir de son nom court

            :param slugName: Nom court
            :type slugName: str
            :returns: Instance du module rechercher, else False
        """
        for m in self.modules:
            if m.slugName == slugName:
                return m
        return False

    def removeModule(self, module):
        """
            Supprimer un module de la base de données

            :param module: Instance d'un module
            :type module: Module
        """
        modules = models.Module.query.filter_by(slugName=module.slugName)
        for m in modules:
            db.session.delete(m)
        db.session.commit()
        self.log('Supprimer module {}'.format(m.slugName))
        return self.loadModules()  # re-load modules

    def loadModules(self):
        """
            Ajout des modules de la base de données
        """
        self.modules = set()
        for m in models.Module.query.all():
            self.modules.add(Module(m.mId, m.slugName, m.name, m.description))
        return True

    def log(self, msg):
        """
            L'ajout d'entrée au server log (config: LOG_FILE)

            :param msg: Message a enregistré
            :type msg: str
        """
        logFile = app.config['LOG_FILE']
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        logMsg = '[{ts}]: {msg}\n'.format(ts=timestamp, msg=msg)

        if not os.path.exists(logFile):
            open(logFile,'w').close()

        with open(logFile, 'a')as f:
            f.write(logMsg)
        print logMsg

    def addNotificationEntry(self, nType, name, entry):
        """
            Ajoute un email a la base des données pour la notification

            :param nType: Le type de notification
            :type nType: str
            :param name: Le nom de la personne qui receveras le message
            :type name: str
            :param entry: L'entrée correspondant
            :type entry: str
        """
        n = models.Notification(nType=nType, name=name, entry=entry)
        db.session.add(n)
        db.session.commit()

    def removeNotificationEntry(self, nId):
        """
            Supprimer une entrée de notification
            :param nId: Le nId de l'entrée a Supprimer
            :type nId: int
        """
        nEntries = models.Notification.query.filter_by(nId=nId)
        for n in nEntries:
            db.session.delete(n)
        db.session.commit()

    def getNotificationEntries(self):
        """
            :returns: Tout les entrées de notifications
        """

        entries = models.Notification.query.all()
        return entries

