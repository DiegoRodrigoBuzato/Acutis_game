"""
API JSON para ranking e dados (usado pelo JavaScript do frontend).
"""
from flask import Blueprint, jsonify, request
from models.models import Participante
from utils.helpers import obter_ranking

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/ranking')
def ranking_json():
    """Retorna ranking em JSON. Query param: semana=true para semanal."""
    semanal = request.args.get('semana', 'false').lower() in ('true', '1', 'yes')
    limite = int(request.args.get('limite', 50))
    ranking = obter_ranking(semanal=semanal, limite=limite)
    total = Participante.query.filter_by(is_admin=False).count()
    return jsonify({'ranking': ranking, 'total': total})


@api_bp.route('/participante/<int:id>')
def participante_json(id):
    """Retorna dados de um participante em JSON."""
    p = Participante.query.get_or_404(id)
    return jsonify({
        'id': p.id,
        'nome': p.nome,
        'nickname': p.nickname,
        'pontos': p.pontos,
        'nivel': p.calcular_nivel(),
        'streak': p.streak,
        'avatar': p.avatar,
    })
