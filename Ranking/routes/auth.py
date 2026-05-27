"""
Rotas de autenticação: login, cadastro, logout.
"""
import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models.models import db, Participante

auth_bp = Blueprint('auth', __name__)

EXTENSOES_PERMITIDAS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def _extensao_valida(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login para participantes e admin."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')

        participante = Participante.query.filter_by(email=email).first()

        if participante and participante.check_senha(senha):
            login_user(participante)
            flash('Login realizado com sucesso! 🎮', 'success')
            prox = request.args.get('next')
            if participante.is_admin:
                return redirect(prox or url_for('admin.panel'))
            return redirect(prox or url_for('main.dashboard'))
        else:
            flash('E-mail ou senha incorretos.', 'error')

    return render_template('login.html')


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Página de cadastro de novos participantes."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        nickname = request.form.get('nickname', '').strip()
        email = request.form.get('email', '').strip().lower()
        whatsapp = request.form.get('whatsapp', '').strip()
        senha = request.form.get('senha', '')

        # Validações
        erros = []
        if len(nome) < 2:
            erros.append('Nome deve ter pelo menos 2 caracteres.')
        if len(nickname) < 3 or len(nickname) > 30:
            erros.append('Nickname deve ter entre 3 e 30 caracteres.')
        if Participante.query.filter_by(email=email).first():
            erros.append('Este e-mail já está cadastrado.')
        if Participante.query.filter_by(nickname=nickname).first():
            erros.append('Este nickname já está em uso.')
        if len(senha) < 4:
            erros.append('Senha deve ter pelo menos 4 caracteres.')

        if erros:
            for e in erros:
                flash(e, 'error')
            return render_template('cadastro.html',
                                   nome=nome, nickname=nickname,
                                   email=email, whatsapp=whatsapp)

        # Processar avatar
        avatar_path = '/static/img/default_avatar.png'
        if 'avatar' in request.files:
            arquivo = request.files['avatar']
            if arquivo.filename and _extensao_valida(arquivo.filename):
                pasta = current_app.config['UPLOAD_FOLDER']
                os.makedirs(pasta, exist_ok=True)
                nome_arquivo = f'{uuid.uuid4().hex}.{arquivo.filename.rsplit(".", 1)[1].lower()}'
                arquivo.save(os.path.join(pasta, nome_arquivo))
                avatar_path = f'/static/uploads/avatars/{nome_arquivo}'

        # Criar participante
        novo = Participante(
            nome=nome,
            nickname=nickname,
            email=email,
            whatsapp=whatsapp,
            avatar=avatar_path,
        )
        novo.set_senha(senha)

        db.session.add(novo)
        db.session.commit()

        login_user(novo)
        flash(f'Bem-vindo ao Acutis Game, {nickname}! 🚀', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('cadastro.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Encerra a sessão do usuário."""
    logout_user()
    flash('Você saiu. Até a próxima! ✝️', 'info')
    return redirect(url_for('main.index'))
