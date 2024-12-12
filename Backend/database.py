from sqlalchemy import create_engine, text

# Créer l'engine pour la base de données SQLite
db = create_engine("sqlite:///app.db", echo=True, future=True)

# Définir la requête SQL pour créer la table
strSQLCreate = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            name VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        );
        """

# Définir la requête SQL pour insérer des données
strSQLInsert = """
        INSERT INTO users (name, password) VALUES ('Joris', 'test');
        """

def init_db():
    # Créer la table 'users' si elle n'existe pas
    with db.connect() as conn:
        conn.commit()

    # Insérer une ligne de données dans la table 'users'
    with db.connect() as conn:
        conn.commit()  # Commit des changements
        

