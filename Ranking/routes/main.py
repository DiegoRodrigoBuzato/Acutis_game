"""
Rotas principais: index, dashboard, ranking, perfil, scan, telão, vencedor.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models.models import db, Participante, Atividade, Scan
from utils.helpers import obter_ranking, obter_frase_aleatoria

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página inicial do evento."""
    total = Participante.query.filter_by(is_admin=False).count()
    return render_template('index.html', total_participantes=total)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard pessoal do participante."""
    ranking = obter_ranking(limite=10)
    scans_recentes = (
        Scan.query
        .filter_by(participante_id=current_user.id)
        .order_by(Scan.timestamp.desc())
        .limit(10)
        .all()
    )

    # Encontrar posição do usuário atual
    posicao = None
    ranking_completo = obter_ranking(limite=500)
    for p in ranking_completo:
        if p['id'] == current_user.id:
            posicao = p['posicao']
            break

    progresso = current_user.progresso_nivel()

    return render_template('dashboard.html',
                           ranking=ranking,
                           scans_recentes=scans_recentes,
                           posicao=posicao,
                           progresso=progresso)


@main_bp.route('/ranking')
def ranking():
    """Página de ranking completo com tabs geral/semanal."""
    ranking_data = obter_ranking(limite=100)
    total = Participante.query.filter_by(is_admin=False).count()
    return render_template('ranking.html', ranking=ranking_data, total=total)


@main_bp.route('/telao')
def telao():
    """Dashboard para TV/telão — fullscreen, sem navbar."""
    ranking_data = obter_ranking(limite=10)
    total = Participante.query.filter_by(is_admin=False).count()
    frase = obter_frase_aleatoria()
    return render_template('telao.html', ranking=ranking_data, total=total, frase=frase)


@main_bp.route('/perfil/<nickname>')
@login_required
def perfil(nickname):
    """Página de perfil de um participante."""
    participante = Participante.query.filter_by(nickname=nickname).first_or_404()

    scans = (
        Scan.query
        .filter_by(participante_id=participante.id)
        .order_by(Scan.timestamp.desc())
        .limit(20)
        .all()
    )

    # Posição no ranking
    posicao = None
    ranking_completo = obter_ranking(limite=500)
    for p in ranking_completo:
        if p['id'] == participante.id:
            posicao = p['posicao']
            break

    return render_template('perfil.html',
                           participante=participante,
                           scans=scans,
                           posicao=posicao)


@main_bp.route('/scan/<codigo>', methods=['GET', 'POST'])
def scan_qr(codigo):
    """
    Rota chamada quando um participante escaneia um QR Code.
    Exibe a tela de scan mobile-friendly e registra pontos/streaks.
    """
    from utils.helpers import calcular_streak, calcular_streak_bonus, verificar_badges
    from flask_login import login_user

    atividade = Atividade.query.filter_by(codigo=codigo, ativa=True).first()

    if not atividade:
        flash('QR Code inválido ou atividade desativada! ❌', 'error')
        return redirect(url_for('main.dashboard'))

    ja_escaneou = False
    if current_user.is_authenticated:
        scan_existente = Scan.query.filter_by(
            participante_id=current_user.id,
            atividade_id=atividade.id
        ).first()
        if scan_existente:
            ja_escaneou = True

    if request.method == 'GET':
        return render_template('scan.html', atividade=atividade, ja_escaneou=ja_escaneou)

    # POST - Processar pontuação
    erro = None
    modo = request.form.get('modo')

    if modo == 'identificar' and not current_user.is_authenticated:
        identificador = request.form.get('identificador')
        senha = request.form.get('senha')
        
        user = Participante.query.filter((Participante.email == identificador) | (Participante.nickname == identificador)).first()
        if user and user.check_senha(senha):
            login_user(user)
            scan_existente = Scan.query.filter_by(participante_id=user.id, atividade_id=atividade.id).first()
            if scan_existente:
                return render_template('scan.html', atividade=atividade, ja_escaneou=True)
            # Se não escaneou ainda, continua o fluxo para pontuar
        else:
            erro = "Credenciais inválidas! Verifique seu nickname/e-mail e senha."
            return render_template('scan.html', atividade=atividade, ja_escaneou=False, erro=erro)

    if not current_user.is_authenticated:
        return render_template('scan.html', atividade=atividade, erro="Você precisa se identificar primeiro.")

    if ja_escaneou:
        return render_template('scan.html', atividade=atividade, ja_escaneou=True)

    # Lógica de pontuar
    streak = calcular_streak(current_user)
    bonus = calcular_streak_bonus(streak)
    pontos_totais = atividade.pontos + bonus

    scan = Scan(
        participante_id=current_user.id,
        atividade_id=atividade.id,
        pontos_ganhos=atividade.pontos,
        streak_bonus=bonus,
    )
    db.session.add(scan)

    ranking_antes = obter_ranking(limite=500)
    pos_antes = next((p['posicao'] for p in ranking_antes if p['id'] == current_user.id), None)

    current_user.pontos += pontos_totais
    current_user.xp += pontos_totais
    db.session.commit()

    novos_badges = verificar_badges(current_user)
    db.session.commit()

    ranking_depois = obter_ranking(limite=500)
    pos_depois = next((p['posicao'] for p in ranking_depois if p['id'] == current_user.id), None)

    from app import socketio
    socketio.emit('ranking_update', {
        'ranking': ranking_depois[:20],
        'total': Participante.query.filter_by(is_admin=False).count(),
        'evento': {
            'participante_id': current_user.id,
            'participante': current_user.nickname,
            'atividade': atividade.nome,
            'pontos': pontos_totais,
            'streak': streak,
            'posicao_anterior': pos_antes,
            'nova_posicao': pos_depois,
            'badges_novos': [{'nome': b.nome, 'icone': b.icone} for b in novos_badges],
        }
    })

    sucesso = {
        'pontos_totais': pontos_totais,
        'streak': streak,
        'bonus': bonus,
        'badges_novos': novos_badges,
        'posicao': pos_depois,
        'pontos_total_user': current_user.pontos
    }

    return render_template('scan.html', atividade=atividade, sucesso=sucesso)


@main_bp.route('/vencedor')
def vencedor():
    """Tela especial para anunciar o vencedor do evento."""
    ranking_data = obter_ranking(limite=3)
    return render_template('winner.html', ranking=ranking_data)
