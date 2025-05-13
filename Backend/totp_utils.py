import pyotp
import qrcode
import os
from io import BytesIO

# Clé secrète pour l'ensemble de l'entreprise

def create_secret_key(filepath=".secret_totp"):
    secret = pyotp.random_base32()
    with open(filepath, "w") as file:
        file.write(secret)

def get_secret_key(filepath=".secret_totp"):
    with open(filepath, "r") as file:
        return file.read().strip()

def generate_totp():
    """
    Génère un code TOTP valable 30 secondes.
    """
    totp = pyotp.TOTP(get_secret_key(".secret_totp"))
    return totp.now()

def generate_qr_code():
    """
    Génère un QR code pour configurer TOTP sur une application comme Okta.
    """
    # Création de l'URI TOTP compatible avec Google Authenticator et Okta
    totp = pyotp.TOTP(get_secret_key(".secret_totp"))
    otp_uri = totp.provisioning_uri(name="SecureHub:Utilisateur", issuer_name="SecureHub")

    # Génération du QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(otp_uri)
    qr.make(fit=True)

    # Convertir le QR code en image
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf)
    buf.seek(0)
    return buf

def response_totp(totp_code):
    totp = pyotp.TOTP(get_secret_key(".secret_totp"))
    return totp.verify(totp_code)
    

