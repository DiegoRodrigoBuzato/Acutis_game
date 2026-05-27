"""
Rotas administrativas: painel, gerenciar atividades, participantes, scans, CSV.
"""
import csv
import io
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from flask_login import login_required, current_user
from models.models import db, Participante, Atividade, Scan, Badge
from utils.helpers import gerar_qrcode, obter_ranking

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorator que exige login de admin."""
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            flash('Acesso negado. Apenas administradores.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return wrapper


@admin_bp.route('/')
@admin_required
def panel():
    """Painel principal do admin com estatísticas."""
    total_participantes = Participante.query.filter_by(is_admin=False).count()
    total_atividades = Atividade.query.count()
    total_scans = Scan.query.count()
    ranking = obter_ranking(limite=10)

    return render_template('admin/panel.html',
                           total_participantes=total_participantes,
                           total_atividades=total_atividades,
                           total_scans=total_scans,
                           ranking=ranking)


# ── ATIVIDADES ───────────────────────────────────────────────────
@admin_bp.route('/atividades')
@admin_required
def atividades():
    """Lista todas as atividades."""
    lista = Atividade.query.order_by(Atividade.criada_em.desc()).all()
    return render_template('admin/atividades.html', atividades=lista)


@admin_bp.route('/atividades/criar', methods=['POST'])
@admin_required
def criar_atividade():
    """Cria nova atividade e gera QR Code automaticamente."""
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()
    pontos = int(request.form.get('pontos', 10))

    if not nome:
        flash('Nome da atividade é obrigatório.', 'error')
        return redirect(url_for('admin.atividades'))

    atividade = Atividade(nome=nome, descricao=descricao, pontos=pontos)
    db.session.add(atividade)
    db.session.flush()  # Para obter o ID e código

    # Gerar QR Code
    qr_pasta = current_app.config['QRCODE_FOLDER']
    gerar_qrcode(atividade.codigo, qr_pasta, request.host_url)

    db.session.commit()
    flash(f'Atividade "{nome}" criada com sucesso! QR Code gerado. ✅', 'success')
    return redirect(url_for('admin.atividades'))


@admin_bp.route('/atividades/<int:id>/toggle')
@admin_required
def toggle_atividade(id):
    """Ativa/desativa uma atividade."""
    atividade = Atividade.query.get_or_404(id)
    atividade.ativa = not atividade.ativa
    db.session.commit()
    status = 'ativada' if atividade.ativa else 'desativada'
    flash(f'Atividade "{atividade.nome}" {status}.', 'info')
    return redirect(url_for('admin.atividades'))


@admin_bp.route('/atividades/<int:id>/excluir')
@admin_required
def excluir_atividade(id):
    """Exclui uma atividade."""
    atividade = Atividade.query.get_or_404(id)
    Scan.query.filter_by(atividade_id=id).delete()
    db.session.delete(atividade)
    db.session.commit()
    flash(f'Atividade "{atividade.nome}" excluída.', 'warning')
    return redirect(url_for('admin.atividades'))


# ── PARTICIPANTES ────────────────────────────────────────────────
@admin_bp.route('/participantes')
@admin_required
def participantes():
    """Lista todos os participantes."""
    lista = Participante.query.filter_by(is_admin=False).order_by(Participante.pontos.desc()).all()
    return render_template('admin/participantes.html', participantes=lista)


@admin_bp.route('/participantes/<int:id>/excluir')
@admin_required
def excluir_participante(id):
    """Exclui um participante e seus dados."""
    p = Participante.query.get_or_404(id)
    if p.is_admin:
        flash('Não é possível excluir um administrador.', 'error')
        return redirect(url_for('admin.participantes'))
    Scan.query.filter_by(participante_id=id).delete()
    from models.models import ParticipanteBadge
    ParticipanteBadge.query.filter_by(participante_id=id).delete()
    db.session.delete(p)
    db.session.commit()
    flash(f'Participante "{p.nickname}" excluído.', 'warning')
    return redirect(url_for('admin.participantes'))


# ── SCANS ────────────────────────────────────────────────────────
@admin_bp.route('/scans')
@admin_required
def scans():
    """Visualizar todos os scans realizados."""
    lista = Scan.query.order_by(Scan.timestamp.desc()).limit(200).all()
    return render_template('admin/scans.html', scans=lista)


# ── RANKING ──────────────────────────────────────────────────────
@admin_bp.route('/resetar-ranking', methods=['POST'])
@admin_required
def resetar_ranking():
    """Reseta todo o ranking (zera pontos, XP, streaks, deleta scans)."""
    Scan.query.delete()
    from models.models import ParticipanteBadge
    ParticipanteBadge.query.delete()
    Participante.query.filter_by(is_admin=False).update({
        'pontos': 0,
        'xp': 0,
        'streak': 0,
        'ultimo_scan': None,
    })
    db.session.commit()

    # Emitir atualização
    from app import socketio
    socketio.emit('ranking_update', {
        'ranking': [],
        'total': Participante.query.filter_by(is_admin=False).count(),
        'evento': None
    })

    flash('Ranking resetado com sucesso! Todos os pontos foram zerados. ⚠️', 'warning')
    return redirect(url_for('admin.panel'))


@admin_bp.route('/exportar-csv')
@admin_required
def exportar_csv():
    """Exporta o ranking completo como CSV."""
    ranking = obter_ranking(limite=9999)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Posição', 'Nome', 'Nickname', 'Pontos', 'Nível', 'Streak', 'Email'])

    for p in ranking:
        part = Participante.query.get(p['id'])
        writer.writerow([
            p['posicao'],
            p['nome'],
            p['nickname'],
            p['pontos'],
            p['nivel'],
            p['streak'],
            part.email if part else '',
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=ranking_acutis_game.csv'}
    )
