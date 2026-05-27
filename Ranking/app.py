"""
═══════════════════════════════════════════════════════════════════
  ACUTIS GAME — Plataforma Gamificada de Ranking em Tempo Real
  Evento presencial inspirado em Carlo Acutis (1991–2006)
  Backend: Flask + Flask-SocketIO + SQLite
═══════════════════════════════════════════════════════════════════
"""
import os
from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO, emit
from config import Config
from models.models import db, Participante
from utils.helpers import obter_ranking

# ── Inicialização ────────────────────────────────────────────────
socketio = SocketIO(cors_allowed_origins='*', async_mode='gevent')
login_manager = LoginManager()


def create_app():
    """Factory de criação do app Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Garantir que pastas existam
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'static/uploads/avatars'), exist_ok=True)
    os.makedirs(app.config.get('QRCODE_FOLDER', 'static/qrcodes'), exist_ok=True)
    os.makedirs('database', exist_ok=True)

    # Inicializar extensões
    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Faça login para acessar esta página.'
    login_manager.login_message_category = 'info'

    # Carregar usuário pelo Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return Participante.query.get(int(user_id))

    # Registrar Blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Criar tabelas no primeiro request
    with app.app_context():
        db.create_all()

    return app


# ── Eventos SocketIO ─────────────────────────────────────────────
@socketio.on('connect')
def handle_connect():
    """Quando um cliente se conecta, envia o ranking atual."""
    pass


@socketio.on('solicitar_ranking')
def handle_solicitar_ranking():
    """Cliente solicita ranking atualizado."""
    ranking = obter_ranking(limite=20)
    total = Participante.query.filter_by(is_admin=False).count()
    emit('ranking_update', {'ranking': ranking, 'total': total})


# ── Ponto de entrada ─────────────────────────────────────────────
app = create_app()

if __name__ == '__main__':
    print('=' * 60)
    print('  + ACUTIS GAME - Servidor rodando!')
    print('  Acesse: http://localhost:5000')
    print('  Telao:  http://localhost:5000/telao')
    print('  Admin:  http://localhost:5000/admin')
    print('=' * 60)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
