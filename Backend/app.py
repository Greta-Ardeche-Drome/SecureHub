from flask import Flask
from database import init_db

app = Flask(__name__)

# Initialiser la base de données
init_db()

# Enregistrer les blueprints

if __name__ == '__main__':
    app.run(debug=True)

