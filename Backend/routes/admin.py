from flask import Blueprint, request, jsonify
from models import db, User

admin = Blueprint('admin', __name__)

@admin.route('/users', methods=['GET'])
def list_users():
    """
    Retourne la liste de tous les utilisateurs pour l'administration.
    """
    users = User.query.all()
    users_data = [{"id": u.id, "username": u.username, "is_admin": u.is_admin} for u in users]
    return jsonify(users_data), 200

@admin.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Supprime un utilisateur par son ID.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Utilisateur supprimé"}), 200

@admin.route('/users/<int:user_id>/reset_totp', methods=['POST'])
def reset_totp(user_id):
    """
    Régénère une clé TOTP pour un utilisateur spécifique.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    user.totp_secret = pyotp.random_base32()
    db.session.commit()
    return jsonify({"message": "Clé TOTP régénérée"}), 200
