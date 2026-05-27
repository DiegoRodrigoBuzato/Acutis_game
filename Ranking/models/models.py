"""
Modelos do banco de dados — SQLAlchemy.
Define: Participante, Atividade, Scan, Badge, ParticipanteBadge.
"""
import uuid
import math
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ── Tabela associativa Participante ↔ Badge ──────────────────────
class ParticipanteBadge(db.Model):
    __tablename__ = 'participante_badge'
    id = db.Column(db.Integer, primary_key=True)
    participante_id = db.Column(db.Integer, db.ForeignKey('participantes.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)


# ── Participante (jogador) ───────────────────────────────────────
class Participante(UserMixin, db.Model):
    __tablename__ = 'participantes'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(120), nullable=False)
    nickname = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    whatsapp = db.Column(db.String(20), nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    avatar = db.Column(db.String(200), default='/static/img/default_avatar.png')
    pontos = db.Column(db.Integer, default=0)
    xp = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    ultimo_scan = db.Column(db.DateTime, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    scans = db.relationship('Scan', backref='participante', lazy='dynamic')
    badges = db.relationship('ParticipanteBadge', backref='participante', lazy='dynamic')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def calcular_nivel(self):
        """Nível baseado em XP — fórmula logarítmica inspirada em RPG."""
        if self.xp <= 0:
            return 1
        return min(int(math.log2(self.xp / 50 + 1)) + 1, 99)

    def xp_para_proximo_nivel(self):
        """XP necessário para o próximo nível."""
        prox = self.calcular_nivel() + 1
        return int((2 ** (prox - 1) - 1) * 50)

    def progresso_nivel(self):
        """Porcentagem de progresso para o próximo nível (0–100)."""
        atual = self.calcular_nivel()
        xp_atual = int((2 ** (atual - 1) - 1) * 50)
        xp_prox = self.xp_para_proximo_nivel()
        diff = xp_prox - xp_atual
        if diff <= 0:
            return 100
        return min(int(((self.xp - xp_atual) / diff) * 100), 100)


# ── Atividade (um QR Code do evento) ────────────────────────────
class Atividade(db.Model):
    __tablename__ = 'atividades'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, default='')
    pontos = db.Column(db.Integer, nullable=False, default=10)
    codigo = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    ativa = db.Column(db.Boolean, default=True)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)

    scans = db.relationship('Scan', backref='atividade', lazy='dynamic')


# ── Scan (registro de participante escaneando QR Code) ───────────
class Scan(db.Model):
    __tablename__ = 'scans'

    id = db.Column(db.Integer, primary_key=True)
    participante_id = db.Column(db.Integer, db.ForeignKey('participantes.id'), nullable=False)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividades.id'), nullable=False)
    pontos_ganhos = db.Column(db.Integer, nullable=False)
    streak_bonus = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ── Badge (conquista / medalha) ──────────────────────────────────
class Badge(db.Model):
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), unique=True, nullable=False)
    descricao = db.Column(db.String(200), default='')
    icone = db.Column(db.String(10), default='🏅')
    requisito_tipo = db.Column(db.String(30), default='scans')    # 'scans', 'pontos', 'streak', 'nivel'
    requisito_valor = db.Column(db.Integer, default=1)

    participantes = db.relationship('ParticipanteBadge', backref='badge', lazy='dynamic')
