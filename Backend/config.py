import os

class Config:
    SECRET_KEY = 'dev'  # À remplacer par une clé secrète
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://flaskuser:securepassword@localhost/2fa_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = Config()