import os
import sqlite3
import json
from flask import Flask, render_template, request, redirect, url_for, g, session, jsonify
import Routes.back as back


FIX_TEMPORAIRE = 'AND Questions.id_question < 17'
AUTH_ACTIVE = True

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)
app.secret_key = "ectoplasme_secret"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "..", "Back", "ectoplase_bdr.db")

# Recuperation de données

@app.get("/data/eleve/<id>")
def get_data_eleve(id):
    if session.get("role", None) not in ["prof", "admin"] and session.get("id", -1) != id:
        return redirect(url_for("connexion"))
    quest_req = back.query_db(f"SELECT * FROM Elèves JOIN Classes ON Classes.id_classe = Elèves.id_classe WHERE id_eleve='{id}'")
    return quest_req[0]

@app.get("/data/questions/<niveau>")
def get_data_questions_niveau(niveau):
    lang = session.get("lang", "fr")
    table = "Questions_FR" if lang == "fr" else "Questions_EN"
    quest_req = back.query_db(f"SELECT * FROM Questions JOIN {table} ON {table}.id_question = Questions.id_question WHERE liste_niveaux LIKE '%{niveau}%' {FIX_TEMPORAIRE}")
    questions = [{'id_question': x['id_question'], 'liste_niveaux': x['liste_niveaux'], 'indice_reponse': x['indice_reponse'], 'intitule': x['intitule'], 'liste_reponses': [r.strip() for r in x['liste_reponses'].split(',')], 'explication': x['explication']} for x in quest_req]
    
    return jsonify({"questions" : questions})


@app.get("/data/questions")
def get_data_questions():
    id = session["id"]
    donnesEleve = get_data_eleve(id)

    return get_data_questions_niveau(donnesEleve["niveau"])

# Route affichant des pages

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
        return render_template("access.html", error="Champs manquants. Missing input fields.", lang=lang)
    
    # logique d'authentification
    session["role"] = role
    if not AUTH_ACTIVE:
        return redirect(url_for("questionnaire"))
    if role == "eleve":
        quest_req = back.query_db(f"SELECT mdp, id_eleve FROM Elèves WHERE email='{email}'")
        mdpCorrecte = quest_req[0]["mdp"]
        id = quest_req[0]["id_eleve"]
        if password == mdpCorrecte:
            session["id"] = id
            return redirect(url_for("questionnaire"))
        else:
            session["role"] = None
            return render_template("access.html", error="Mot de Passe Incorrecte. Incorrect Password.", lang=lang)
    if role == "prof":
        quest_req = back.query_db(f"SELECT mdp, id_prof FROM Profs WHERE email='{email}'")
        mdpCorrecte = quest_req[0]["mdp"]
        id = quest_req[0]["id_prof"]
        if password == mdpCorrecte:
            return redirect(url_for("dashboard_prof"))
        else:
            session["role"] = None
            return render_template("access.html", error="Mot de Passe Incorrecte. Incorrect Password.", lang=lang)
    if role == "admin":
        quest_req = back.query_db(f"SELECT mdp, id_admin FROM Admin WHERE email='{email}'")
        mdpCorrecte = quest_req[0]["mdp"]
        id = quest_req[0]["id_admin"]
        if password == mdpCorrecte:
            session["id"] = id
            return redirect(url_for("dashboard_admin"))
        else:
            session["role"] = None
            return render_template("access.html", error="Mot de Passe Incorrecte. Incorrect Password.", lang=lang)
    
    session["role"] = None
    return render_template("access.html", error="Type d'utilisateur non reconnu. Unrecognizable user type.", lang=lang)


    

@app.get("/")
def index():
    return redirect(url_for("connexion_get"))

@app.route('/questionnaire')
def questionnaire():
    id = session["id"]
    donnesEleve = get_data_eleve(id)

    quest_req = back.query_db("SELECT * FROM Questions")
    questions = [{'id_question': x['id_question'], 'liste_niveaux': x['liste_niveaux'], 'indice_reponse': x['indice_reponse']} for x in quest_req]
    lang = session.get("lang", "fr")
    if lang == "fr":
        questions_lang = [{'id_question': x['id_question'], 'intitule': x['intitule'], 'liste_reponses': [r.strip() for r in x['liste_reponses'].split(',')], 'explication': x['explication']} for x in back.query_db("SELECT * FROM Questions_FR")]
    else:
        questions_lang = [{'id_question': x['id_question'], 'intitule': x['intitule'], 'liste_reponses': [r.strip() for r in x['liste_reponses'].split(',')], 'explication': x['explication']} for x in back.query_db("SELECT * FROM Questions_EN")]

    # return render_template("questionnaire.html", questions=questions, questions_lang=questions_lang)
    return render_template("questionnaire2.html")


@app.route('/resultats', methods=['POST'])
def resultats():
    lang = session.get("lang", "fr")
    reponses = request.form
    

    questions = get_data_questions().get_json()["questions"]

    print(reponses.get("1"))
    total = len(questions)
    score = 0
    for q in questions:
        print(reponses.get(str(q["id_question"])), q["indice_reponse"] - 1)
        if reponses.get(str(q["id_question"])) == str(q["indice_reponse"] - 1):
            score += 1

    pourcentage = round((score / total * 100) if total else 0)

    id = session["id"]
    donnesEleve = get_data_eleve(id)

    nbTentatives = donnesEleve["nb_tentatives"]
    if not isinstance(nbTentatives, int):
        nbTentatives = 0
    nbTentatives += 1
    back.change_db(f"UPDATE Elèves SET nb_tentatives={nbTentatives} WHERE id_eleve={id}")

    meilleur_score = donnesEleve["meilleur_score"]
    if not isinstance(meilleur_score, int):
        meilleur_score = 0
    if score > meilleur_score:
        meilleur_score = score
        back.change_db(f"UPDATE Elèves SET meilleur_score={score} WHERE id_eleve={id}")

    return render_template("resultats.html", score=score, total=total, pourcentage=pourcentage, meilleur_score=meilleur_score, lang=lang)


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