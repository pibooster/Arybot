from flask import Flask
from threading import Thread

# Créer une application Flask
app = Flask('')

# Définir une route pour la page d'accueil
@app.route('/')
def home():
    return "Le bot est en ligne !"

# Fonction pour exécuter l'application Flask
def run():
    app.run(host='0.0.0.0', port=8080)

# Fonction pour maintenir le bot en ligne
def keep_alive():
    # Créer un thread pour exécuter l'application Flask
    t = Thread(target=run)
    t.start()
