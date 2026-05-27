"""
Configuração do aplicativo Flask.
Define SECRET_KEY, URI do banco SQLite e outras configurações.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'acutis-game-secret-2024-carlo')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'acutis_game.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB máximo para upload de avatar
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'avatars')
    QRCODE_FOLDER = os.path.join(BASE_DIR, 'static', 'qrcodes')
