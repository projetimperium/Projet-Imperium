# -*- coding: utf-8 -*-

from slugify import slugify
from flask import render_template, request, flash, redirect
from app import app, db, models
import forms
import re
import time
import json
import os
from datetime import datetime, timedelta


@app.route('/data/getData')
def getDataAsJson():
    toGraph = ('wattmetre-V', 'wattmetre-I', 'wattmetre-S', 'wattmetre-W', 'wattmetre-Q', 'wattmetre-freq', 'temperature')
    dataSet = dict()
    for n in toGraph:
        entries = app.control.dataHandler.getAllData(n, asDict=True)
        dataSet.update(entries)
    return json.dumps(dataSet)


@app.route('/data')
def data():

    dataSet = getDataAsJson()

    fromDate = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%dT%H:%M')
    toDate = time.strftime('%Y-%m-%dT%H:%M')
    xIncrement = 1  # default 1 day
    yMin = -30
    yMax = 30
    yIncrement = 1

    return render_template(
        'data.html',
        title='Wattmetre',
        dataSet=dataSet,
        fromDate=fromDate,
        toDate=toDate,
        xIncrement=xIncrement,
        yMin=yMin,
        yMax=yMax,
        yIncrement=yIncrement,
        modules=app.control.modules)


@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """
        Ajout d'un sous-module a la base de données
    """

    form = forms.RegisterModuleForm()
    if form.validate_on_submit():
        name = form.name.data
        slugName = slugify(name).lower()
        description = ''
        if form.description.data:
            description = form.description.data

        if not app.control.getModuleFromSlugName(slugName):  # doesn't exist
            m = models.Module(slugName=slugName, name=name, description=description)
            db.session.add(m)
            db.session.commit()
            logMsg = "Ajout d'un sous-module. Nom: {} Description: {}".format(name, description)
            app.control.log(logMsg)
            flash(logMsg)
            app.control.loadModules()  # reload module list
        else:
            logMsg = "Module avec le nom {} exists deja.".format(name)
            flash(logMsg)

    return render_template(
        'ajouter.html',
        title='Ajouter un Module',
        form=form,
        modules=app.control.modules)


@app.route('/statuts')
def statut():
    """
        Obvervé les évéenments de l'application
    """
    showDate = request.args.get('showDate', '')

    if not os.path.exists(app.config['LOG_FILE']):
        open(app.config['LOG_FILE'],'w').close()

    if showDate == 'all':
        logFileContent = open(app.config['LOG_FILE']).readlines()
    else:
        if not re.match('\d{4}-\d{2}-\d{2}', showDate):
            showDate = time.strftime('%Y-%m-%d')  # today

        logFileContent = open(app.config['LOG_FILE']).readlines()
        logFileContent = filter(lambda l: showDate in l, logFileContent)

    return render_template(
        'statuts.html',
        showDate=showDate,
        logFileContent=logFileContent,
        title='Statuts',
        modules=app.control.modules)


@app.route('/options', methods=['GET', 'POST'])
def options():
    """
        Page d'options
    """
    if request.method == 'POST':
        cmd = request.form['cmd']
        if cmd == 'deleteNotification':
            nId = request.form['nId']
            app.control.removeNotificationEntry(nId=nId)
        elif cmd == 'addNotification':
            nType = request.form['nType']
            nName = request.form['nName']
            nEntry = request.form['nEntry']
            app.control.addNotificationEntry(nType=nType, name=nName, entry=nEntry)

    notificationEntries = app.control.getNotificationEntries()

    return render_template(
        'options.html',
        title='Options',
        notificationEntries=notificationEntries,
        modules=app.control.modules)


@app.route('/module/<string:moduleSlugname>', methods=['GET', 'POST'])
def module(moduleSlugname):
    """
        Gestion d'un module
    """
    form = forms.CommandForm()
    module = app.control.getModuleFromSlugName(moduleSlugname)

    toDelete = request.args.get('delModule', '')
    if toDelete == module.slugName:
        app.control.removeModule(module)
        return redirect('/')

    if form.validate_on_submit():
        cmd = form.command.data
        retMsg = module.sendCommand(cmd)
        flash(retMsg)

    return render_template(
        'module.html',
        module=module.getDict(),
        form=form,
        modules=app.control.modules)


@app.route('/')
@app.route('/index')
def index():
    """
        Page principale
    """
    description = \
    u'''
<h1>Projet Impérium</h1>
<hr>
<br>
Le projet est composé d’une unité principale de contrôle qui communique avec différents sous module. Son objectif est d’effectuer le traitement de l’information et la collection de l’information provenant des sous-modules. Ce module principal peut se connecter à l’internet pour réaliser le contrôle par téléphone intelligent ou d’autres appareils. Avec cet élément, il est possible d’ajouter d’autres sous module si jamais on décide d’agrandir l’échelle du projet.
<br><br>
Le premier sous-module comprend un système intelligent pour déverrouiller la serrure d’une porte. Aujourd’hui, avec cet âge informatique et technologique, la majorité des gens ont des téléphones intelligents et les apportent tout au long de la journée. Leur cellulaire devient leurs identités et pourrait aussi être leurs clés et plusieurs de ces outils ont maintenant la technologie NFC intégrée. En exploitant ces facteurs, on peut créer une serrure intelligente qui pourrait être déverrouillée à distance. Cela permet aux clients de faciliter la tâche lorsqu’ils veulent entrer chez eux. En somme, le module est capable de déverrouiller une porte à distance à l’aide d’un appareil, déverrouiller une porte à l’aide de la technologie RFID ou d’une clé en cas d’urgence.
<br><br>
Le deuxième sous-module comprend un système de mesure. Il sera capable de mesurer la puissance de chaque circuit individuel provenant du panneau électrique d’une maison. Il enverra les données à notre unité principale pour effectuer le traitement des données, tel que l’analyse des coûts et de la consommation. De plus, l’unité principale sauvegardera les données pour qu’ils soient accessibles à n’importe quel moment. La demande d’énergie continue d’augmenter et donc ce sous-module devient un projet très important à réaliser pour la gestion d’énergie consommée.
'''
    return render_template(
        'index.html',
        description=description,
        modules=app.control.modules)
