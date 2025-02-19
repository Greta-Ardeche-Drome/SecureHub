from ldap3 import Server, Connection, ALL
from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

# Configuration LDAP
AD_SERVER = '192.168.1.149'
AD_USER = 'CN=securehub,CN=Users,DC=securehub,DC=fr'
AD_PASSWORD = 'Testmdp2025!3'
BASE_DN = 'OU=site,DC=securehub,DC=fr'

def get_ad_users():
    """
    Récupère tous les utilisateurs de l'Active Directory et retourne un dictionnaire {username: fullname}.
    """
    server = Server(AD_SERVER, get_info=ALL)
    conn = Connection(server, AD_USER, AD_PASSWORD, auto_bind=True)

    conn.search(
        search_base=BASE_DN,
        search_filter='(objectClass=user)',
        attributes=['sAMAccountName', 'displayName']
    )

    return {
        entry.sAMAccountName.value: entry.displayName.value if entry.displayName else entry.sAMAccountName.value
        for entry in conn.entries
    }


def initialize_users_from_ad():
    """
    Initialise la base de données locale avec les utilisateurs récupérés depuis l'Active Directory.
    Cette fonction est utilisée une seule fois pour créer les utilisateurs au départ.
    """
    ad_users = get_ad_users()

    with db.connect() as conn_db:
        for username, fullname in ad_users.items():
            hashed_password = generate_password_hash("SecHub")
            conn_db.execute(
                text("""
                    INSERT INTO users (name, fullname, password, is_password_changed) 
                    VALUES (:username, :fullname, :password, 0)
                """),
                {"username": username, "fullname": fullname, "password": hashed_password}
            )
        conn_db.commit()

    print("Initialisation terminée : utilisateurs importés depuis l'AD.")


def update_users_from_ad():
    """
    Vérifie les nouveaux utilisateurs et ceux supprimés de l'AD, puis met à jour la base locale.
    """
    ad_users = get_ad_users()

    with db.connect() as conn_db:
        # Récupérer les utilisateurs existants en base
        db_users = {row['name'] for row in conn_db.execute(text("SELECT name FROM users")).fetchall()}

        # Ajouter les nouveaux utilisateurs
        new_users = set(ad_users.keys()) - db_users
        for username in new_users:
            fullname = ad_users[username]
            hashed_password = generate_password_hash("SecHub")
            conn_db.execute(
                text("""
                    INSERT INTO users (name, fullname, password, is_password_changed) 
                    VALUES (:username, :fullname, :password, 0)
                """),
                {"username": username, "fullname": fullname, "password": hashed_password}
            )

        # Supprimer les utilisateurs qui ne sont plus dans l'AD
        users_to_remove = db_users - set(ad_users.keys())
        for user in users_to_remove:
            if user != "SecureHub":
                conn_db.execute(
                    text("DELETE FROM users WHERE name = :users_to_remove"),
                    {"users_to_remove": user}
                )

        # Appliquer les modifications
        conn_db.commit()

    print("Mise à jour terminée : base de données synchronisée avec l'AD.")
