#!/usr/bin/python3
# -*- coding: latin-1 -*-
import os
import sys
# import psycopg2
import json

from bson import json_util
from pymongo import MongoClient
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash,Response


def create_app():
    app = Flask(__name__)
    return app

app = create_app()

# REPLACE WITH YOUR DATABASE NAME
MONGODATABASE = "test"
#MONGOSERVER = "localhost"
MONGOSERVER = "query17-12.ing.puc.cl"
MONGOPORT = 27017
client = MongoClient(MONGOSERVER, MONGOPORT)
mongodb = client[MONGODATABASE]

collection = mongodb["test"]
collection.create_index([('contenido', 'text')])

''' # Uncomment for postgres connection
# REPLACE WITH YOUR DATABASE NAME, USER AND PASS
POSTGRESDATABASE = "mydatabase"
POSTGRESUSER = "myuser"
POSTGRESPASS = "mypass"
postgresdb = psycopg2.connect(
    database=POSTGRESDATABASE,
    user=POSTGRESUSER,
    password=POSTGRESPASS)
'''
#print("hola")
#Cambiar por Path Absoluto en el servidor
QUERIES_FILENAME = '/var/www/flaskr/queries'


@app.route("/")
def home():
    with open(QUERIES_FILENAME, 'r', encoding='utf-8') as queries_file:
        json_file = json.load(queries_file)
        pairs = [(x["name"],
                  x["database"],
                  x["description"],
                  x["query"]) for x in json_file]
        return render_template('file.html', results=pairs)


@app.route("/mongo")
def mongo():
    query = request.args.get("query")
    results = eval('mongodb.'+query)
    results = json_util.dumps(results, sort_keys=True, indent=4)
    if "find" in query:
        return render_template('mongo.html', results=results)
    else:
        return "ok"


@app.route("/postgres")
def postgres():
    query = request.args.get("query")
    cursor = postgresdb.cursor()
    cursor.execute(query)
    results = [[a for a in result] for result in cursor]
    print(results)
    return render_template('postgres.html', results=results)


@app.route("/example")
def example():
    return render_template('example.html')

#Consultas

@app.route('/api/fecha/', methods=['GET'])
def consulta_1():
	date = request.args.get('date')
	escuchas=mongodb.entidades
	result = json_util.dumps(escuchas.find({'fecha':date},{'numero':1, 'fecha':1, 'ciudad':1 , 'contenido':1}))
	response = Response(result)
	response.headers.add('Access-Control-Allow-Origin','*')
	return(response)

@app.route('/api/keyword/', methods=['GET'])
def consulta_2():
	palabra = '"'+request.args.get('keyword')+'"'
	escuchas=mongodb.entidades
    #entidades.find({'$text': {'$search': 'borracho'}},{'numero':1, 'fecha':1, 'ciudad':1 , 'contenido':1})
	result = json_util.dumps(escuchas.find({'$text': {'$search': palabra}},{'numero':1, 'fecha':1, 'ciudad':1 , 'contenido':1}))
	response = Response(result)
	response.headers.add('Access-Control-Allow-Origin','*')
	return(response)

@app.route('/api/numero/', methods=['GET'])
def consulta_3():
    numero = request.args.get('numero')
    k = int(request.args.get('k'))

    escuchas=mongodb.entidades
    #entidades.find({'$text': {'$search': 'borracho'}},{'numero':1, 'fecha':1, 'ciudad':1 , 'contenido':1})
    result = json_util.dumps(escuchas.find({'numero':numero},{'numero':1, 'fecha':1, 'ciudad':1 , 'contenido':1}).limit(k).sort('fecha',-1))
    response = Response(result)
    response.headers.add('Access-Control-Allow-Origin','*')
    return(response)

if __name__ == "__main__":
    app.run()
