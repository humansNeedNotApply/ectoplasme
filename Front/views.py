import sqlite3
import json
from flask import Flask, render_template, request, redirect, url_for, g, session



app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)
app.secret_key = "ectoplasme_secret"

DATABASE = "../Back/ectoplase_bdr.db"

def get_db():
    db = getattr(g, "_database", None)
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
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route('/questionnaire')
def questionnaire():
    quest_req = query_db("SELECT * FROM Questions")
    questions = [{'id_question': x['id_question'], 'liste_niveaux': x['liste_niveaux'], 'indice_reponse': x['indice_reponse']} for x in quest_req]

    if request.form.get(""):
        role = request.form.get("role")
        email = request.form.get("email")
        password = request.form.get("password")
        lang = request.form.get("lang", "fr")
        
        if not role or not email or not password or not lang:
            return render_template("access.html", error="Champs manquants.", lang=lang)

    if (request.form.get("lang", "fr")):
        questions_lang = [{'id_question': x['id_question'], 'intitule': x['intitule'], 'liste_reponses': x['liste_reponses'], 'explication': x['explication']} for x in query_db("SELECT * FROM Questions_FR")]
    else:
        questions_lang = [{'id_question': x['id_question'], 'intitule': x['intitule'], 'liste_reponses': x['liste_reponses'], 'explication': x['explication']} for x in query_db("SELECT * FROM Questions_EN")]
    print(questions_lang)
    return render_template("questionnaire.html", questions=questions, questions_lang=questions_lang)


@app.route('/resultats', methods=['GET'])
def resultats():
    solutions = request.form.get("reponses")
    
    return render_template("resultats.html")


@app.route('/leaderboard')
def leaderboard():
    eleves = []
    for x in query_db("SELECT * FROM Elèves"):
        classes = query_db("SELECT niveau, numéro FROM Classes JOIN ON Elèves WHERE Classes.id_classe = Elèves.id_classe")
        eleves += {'prenom': x['prenom'], 'nom': x['nom'], 'classe': classes['niveau'] + ' ' + classes['numéro'], 'meilleur_score': x['meilleur_score']}
    json_eleves = json.dump(eleves)
    return render_template("leaderboard.html", classes=classes eleves=eleves, json_eleves = json_eleves)

@app.route('/dashboard_prof')
def dashboard_prof():
    eleves = []
    for x in query_db("SELECT * FROM Elèves"):
        classes = query_db("SELECT niveau, numéro FROM Classes JOIN ON Elèves WHERE Classes.id_classe = Elèves.id_classe")
        eleves += {'prenom': x['prenom'], 'nom': x['nom'], 'classe': classes['niveau'] + ' ' + classes['numéro'], 'meilleur_score': x['meilleur_score']}
    json_eleves = json.dump(eleves)
    return render_template("leaderboard.html", eleves=eleves, json_eleves = json_eleves)
    

@app.route('/dashboard_admin')#
def dashboard_admin():
    data = query_db()

@app.get("/connexion")
def connexion_get():
    lang = session.get("lang", "fr")
    return render_template("access.html", error=None, lang=lang)

@app.get("/set_lang/<lang>")
def set_lang(lang):
    if lang not in ["fr", "en"]:
        lang = "fr"

    session["lang"] = lang
    return redirect(url_for("connexion_get"))


@app.post("/connexion")
def connexion_post():
    role = request.form.get("role")
    email = request.form.get("email")
    password = request.form.get("password")
    lang = request.form.get("lang", "fr")

    session["lang"] = lang

    if not role or not email or not password:
        return render_template("access.html", error="Champs manquants.", lang=lang)

    return #redirect(url_for("questionnaire"))



@app.get("/")
def index():
    return redirect(url_for("connexion_get"))


@app.route("/eleves")
def eleves():
    return "Page élèves "

app.run(debug=True)
