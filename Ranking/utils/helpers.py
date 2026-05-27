"""
Funções utilitárias: ranking, badges, streak, QR Code.
"""
import os
import io
import qrcode
from datetime import datetime, timedelta
from models.models import db, Participante, Scan, Badge, ParticipanteBadge


# ── Frases motivacionais de Carlo Acutis ─────────────────────────
FRASES = [
    "Você foi feito para o Paraíso — não perca de vista o objetivo!",
    "A nossa meta é o infinito, não o finito. O infinito é a nossa pátria.",
    "Todos nascem originais, mas muitos morrem como fotocópias.",
    "A Eucaristia é a minha autoestrada para o Céu.",
    "Quem não reza é como alguém que tem um celular e nunca liga para Deus.",
    "Estar sempre unido a Jesus: este é o meu programa de vida.",
    "A tristeza é olhar para si. A felicidade é olhar para Deus.",
    "O que é que nos devemos preocupar? O Paraíso!",
    "De que adianta ganhar mil batalhas se não consegues vencer a ti mesmo?",
    "A conversão é nada mais do que deslocar o olhar do baixo para o Alto.",
]


def obter_frase_aleatoria():
    """Retorna uma frase motivacional aleatória."""
    import random
    return random.choice(FRASES)


def obter_ranking(semanal=False, limite=50):
    """
    Retorna lista de dicionários com ranking ordenado por pontos.
    Se semanal=True, considera apenas scans da semana atual.
    """
    if semanal:
        inicio_semana = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)

        from sqlalchemy import func
        # Soma pontos dos scans da semana
        resultados = (
            db.session.query(
                Participante,
                func.coalesce(func.sum(Scan.pontos_ganhos + Scan.streak_bonus), 0).label('pontos_semana')
            )
            .outerjoin(Scan, (Scan.participante_id == Participante.id) & (Scan.timestamp >= inicio_semana))
            .filter(Participante.is_admin == False)
            .group_by(Participante.id)
            .order_by(func.coalesce(func.sum(Scan.pontos_ganhos + Scan.streak_bonus), 0).desc())
            .limit(limite)
            .all()
        )

        ranking = []
        for i, (p, pts_semana) in enumerate(resultados, 1):
            ranking.append(_participante_to_dict(p, i, int(pts_semana)))
        return ranking
    else:
        participantes = (
            Participante.query
            .filter_by(is_admin=False)
            .order_by(Participante.pontos.desc())
            .limit(limite)
            .all()
        )
        return [_participante_to_dict(p, i + 1) for i, p in enumerate(participantes)]


def _participante_to_dict(p, posicao, pontos_override=None):
    """Converte Participante em dicionário para o ranking."""
    badges_lista = []
    for pb in p.badges.all():
        badges_lista.append({
            'nome': pb.badge.nome,
            'icone': pb.badge.icone,
            'descricao': pb.badge.descricao,
        })

    return {
        'id': p.id,
        'uid': p.uid,
        'nome': p.nome,
        'nickname': p.nickname,
        'avatar': p.avatar or '/static/img/default_avatar.png',
        'pontos': pontos_override if pontos_override is not None else p.pontos,
        'xp': p.xp,
        'nivel': p.calcular_nivel(),
        'streak': p.streak,
        'posicao': posicao,
        'badges': badges_lista,
    }


def calcular_streak(participante):
    """
    Calcula streak: se o último scan foi há menos de 10 min, incrementa.
    Caso contrário, reseta para 1.
    """
    agora = datetime.utcnow()
    if participante.ultimo_scan:
        diff = (agora - participante.ultimo_scan).total_seconds()
        if diff <= 600:  # 10 minutos
            participante.streak += 1
        else:
            participante.streak = 1
    else:
        participante.streak = 1
    participante.ultimo_scan = agora
    return participante.streak


def calcular_streak_bonus(streak):
    """Bônus de pontos baseado no streak atual."""
    if streak < 2:
        return 0
    elif streak < 4:
        return 5      # x2-x3: +5 bonus
    elif streak < 6:
        return 10     # x4-x5: +10 bonus
    elif streak < 10:
        return 20     # x6-x9: +20 bonus
    else:
        return 50     # x10+: +50 bonus


def verificar_badges(participante):
    """Verifica e atribui badges novos ao participante."""
    badges_ganhos = []
    badges_existentes = {pb.badge_id for pb in participante.badges.all()}

    for badge in Badge.query.all():
        if badge.id in badges_existentes:
            continue

        concedido = False
        if badge.requisito_tipo == 'scans':
            concedido = participante.scans.count() >= badge.requisito_valor
        elif badge.requisito_tipo == 'pontos':
            concedido = participante.pontos >= badge.requisito_valor
        elif badge.requisito_tipo == 'streak':
            concedido = participante.streak >= badge.requisito_valor
        elif badge.requisito_tipo == 'nivel':
            concedido = participante.calcular_nivel() >= badge.requisito_valor

        if concedido:
            pb = ParticipanteBadge(participante_id=participante.id, badge_id=badge.id)
            db.session.add(pb)
            badges_ganhos.append(badge)

    return badges_ganhos


def gerar_qrcode(codigo, pasta, base_url="http://localhost:5000"):
    """Gera imagem QR Code com a URL completa e salva como PNG."""
    os.makedirs(pasta, exist_ok=True)
    filepath = os.path.join(pasta, f'{codigo}.png')

    qr = qrcode.QRCode(version=1, box_size=10, border=4,
                        error_correction=qrcode.constants.ERROR_CORRECT_H)
    
    # Criar URL completa para o celular reconhecer como link
    url_completa = f"{base_url.rstrip('/')}/scan/{codigo}"
    qr.add_data(url_completa)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1E40FF", back_color="#050510")
    img.save(filepath)

    return f'/static/qrcodes/{codigo}.png'
