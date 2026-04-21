import os
import sqlite3
import json
from flask import Flask, render_template, request, redirect, url_for, g, session
import Routes.back as back


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)
app.secret_key = "ectoplasme_secret"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "..", "Back", "ectoplase_bdr.db")

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
    return redirect(url_for("questionnaire"))

@app.get("/")
def index():
    return redirect(url_for("connexion_get"))

@app.route('/questionnaire')
def questionnaire():
    quest_req = back.query_db("SELECT * FROM Questions")
    questions = [{'id_question': x['id_question'], 'liste_niveaux': x['liste_niveaux'], 'indice_reponse': x['indice_reponse']} for x in quest_req]
    lang = session.get("lang", "fr")
    if lang == "fr":
        questions_lang = [{'id_question': x['id_question'], 'intitule': x['intitule'], 'liste_reponses': [r.strip() for r in x['liste_reponses'].split(',')], 'explication': x['explication']} for x in back.query_db("SELECT * FROM Questions_FR")]
    else:
        questions_lang = [{'id_question': x['id_question'], 'intitule': x['intitule'], 'liste_reponses': [r.strip() for r in x['liste_reponses'].split(',')], 'explication': x['explication']} for x in back.query_db("SELECT * FROM Questions_EN")]

    return render_template("questionnaire.html", questions=questions, questions_lang=questions_lang)


@app.route('/resultats', methods=['POST'])
def resultats():
    lang = session.get("lang", "fr")
    reponses_json = request.form.get("reponses", "{}")
    try:
        reponses = json.loads(reponses_json)
    except json.JSONDecodeError:
        reponses = {}

    questions = back.query_db("SELECT id_question, indice_reponse FROM Questions")
    total = len(questions)
    score = 0
    for q in questions:
        if reponses.get(str(q["id_question"])) == q["indice_reponse"] - 1:
            score += 1

    pourcentage = round((score / total * 100) if total else 0)
    return render_template("resultats.html", score=score, total=total, pourcentage=pourcentage, meilleur_score=score, lang=lang)


@app.route('/leaderboard')
def leaderboard():
    lang = session.get("lang", "fr")
    eleves = back.query_db("""
        SELECT e.prenom, e.nom, c.niveau, c.numéro,
               COALESCE(e.meilleur_score, 0) AS meilleur_score,
               COALESCE(e.nb_tentatives, 0)  AS nb_tentatives
        FROM "Elèves" e
        JOIN Classes c ON e.id_classe = c.id_classe
        ORDER BY meilleur_score DESC
    """)
    return render_template("leaderboard.html", eleves=eleves, lang=lang)


@app.route('/dashboard_prof')
def dashboard_prof():
    lang = session.get("lang", "fr")
    eleves = back.query_db("""
        SELECT e.prenom, e.nom, c.niveau, c.numéro,
               COALESCE(e.meilleur_score, 0) AS meilleur_score,
               COALESCE(e.nb_tentatives, 0)  AS nb_tentatives
        FROM "Elèves" e
        JOIN Classes c ON e.id_classe = c.id_classe
        ORDER BY meilleur_score DESC
    """)
    return render_template("dashboard_prof.html", eleves=eleves, lang=lang)


@app.route('/dashboard_admin')
def dashboard_admin():
    lang = session.get("lang", "fr")
    eleves = back.query_db('SELECT * FROM "Elèves"')
    return render_template("leaderboard.html", eleves=eleves, lang=lang)


@app.route("/eleves")
def eleves():
    return "Page élèves"

if __name__ == "__main__":
    app.run(debug=True)