from flask import Flask, render_template, redirect, url_for
from database import init_db, insert_db

app = Flask(__name__, template_folder='../Frontend/templates')

# Initialiser la base de données
init_db()

# Route pour la page d'accueil
@app.route('/')
def home():
    return render_template('index.html')

# Route pour insérer des données dans la base de données
@app.route('/insert', methods=['POST'])
def insert_data():
    insert_db()  # Appeler la fonction pour insérer des données dans la base
    return redirect(url_for('home'))  # Rediriger vers la page d'accueil après insertion

if __name__ == '__main__':
    app.run(debug=True)


