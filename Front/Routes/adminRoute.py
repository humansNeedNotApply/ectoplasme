import os
import sqlite3
import json
from flask import Flask, render_template, request, redirect, url_for, g, session, make_response
from back import query_db, change_db
import csv
import io

def get_data_classes():
    return query_db("SELECT * FROM Classes;")

def get_data_classe_id(id):
    classe = query_db(f"SELECT * FROM Classes WHERE id_classe = {id};", one=True)
    prof = query_db(f"SELECT * FROM Profs WHERE id_classe = {id};", one=True)
    
    return {"classe" : classe, "prof" : prof}

def get_data_eleves_classe_csv(id):
    eleves = query_db(f"SELECT * FROM Elèves WHERE id_classe = {id};")

    if not len(eleves):
        raise Exception("Il n'y a pas d'eleves dans cette classe")

    colonnes = list(eleves[0].keys())
    values = [[eleve[colonne] for colonne in colonnes]  for eleve in eleves]

    #il existe une solution plus simple avec FLASK mais elle demande de rajouter des fichiers temporaires sur le serveur, ce qui serait une galère en plus
    output = io.StringIO()
    write = csv.writer(output)
    write.writerow(colonnes)
    write.writerows(values)

    return output.getvalue()

def download_data_eleves_classe_csv(id):
    csv_string = get_data_eleves_classe_csv(id)
    
    response = make_response(csv_string)
    response.headers["Content-Disposition"] = f"attachment; filename=classe{id}.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

    