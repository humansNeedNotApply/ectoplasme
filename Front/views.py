import sqlite3
from flask import Flask
from flask import render_template, request, redirect, url_for, g
app = Flask(__name__, template_folder = "./Templates", static_folder='./Styles')

DATABASE = "../Back/ectoplase_bdr.db"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def change_db(query, args=()):
    cur = get_db().execute(query, args)
    get_db().commit()
    cur.close()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index(): 
    return render_template("access.html")

@app.route('/questionnaire', methods=['GET'])
def questionnaire():
    quest_req = query_db("SELECT * FROM Questions")
    questions = [{'id_question': x['id_question'], 'liste_niveaux': x['liste_niveaux'], 'indice_reponse': x['indice_reponse']} for x in quest_req]

    if (request.args.get("lang") == "fr"):
        questions_lang = [{'id_question': x['id_question'], 'intitulé': x['intitulé'], 'liste_reponses': x['liste_reponses'], 'explication': x['explication']} for x in query_db("SELECT * FROM questions_FR")]
    else:
        questions_lang = [{'id_question': x['id_question'], 'intitulé': x['intitulé'], 'liste_reponses': x['liste_reponses'], 'explication': x['explication']} for x in query_db("SELECT * FROM questions_EN")]
    return render_template("questionnaire.html", questions=questions, questions_lang=questions_lang)


@app.route('/resultats')
def resultats():
    return render_template("resultats.html")

app.run(debug=False)

