from flask import Flask
from database import init_db
from routes.auth import auth_blueprint
from routes.admin import admin_blueprint

app = Flask(__name__)
app.config.from_object('config')  # Charger la configuration

# Initialiser la base de données
init_db(app)

# Enregistrer les blueprints
app.register_blueprint(auth_blueprint, url_prefix='/api')
app.register_blueprint(admin_blueprint, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
