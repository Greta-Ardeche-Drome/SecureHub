from flask import Blueprint, request, jsonify
import pyotp
from models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    """
    Authentification via TOTP.
    L'utilisateur doit fournir son nom d'utilisateur et son code TOTP.
    """
    data = request.get_json()
    username = data.get('username')
    totp_code = data.get('totp_code')

    # Récupération de l'utilisateur dans la base
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    # Vérification du TOTP
    totp = pyotp.TOTP(user.totp_secret)
    if totp.verify(totp_code):
        return jsonify({"message": "Authentification réussie"}), 200
    else:
        return jsonify({"error": "Code TOTP invalide"}), 401

@auth.route('/generate_qr', methods=['GET'])
def generate_qr():
    """
    Génération d'un QR Code pour lier un utilisateur à une application 2FA.
    """
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    # Génération d'une clé TOTP
    if not user.totp_secret:
        user.totp_secret = pyotp.random_base32()
        db.session.commit()

    # URL pour application TOTP (exemple : Google Authenticator)
    totp = pyotp.TOTP(user.totp_secret)
    url = totp.provisioning_uri(username, issuer_name="My2FAProject")
    return jsonify({"qr_url": url}), 200
