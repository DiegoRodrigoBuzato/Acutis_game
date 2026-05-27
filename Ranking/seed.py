"""
Seed inicial para testes — cria admin, participantes de exemplo,
atividades com QR Codes e badges.

Uso: python seed.py
"""
import os
import sys

# Ajustar path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, socketio
from models.models import db, Participante, Atividade, Badge
from utils.helpers import gerar_qrcode


def seed():
    with app.app_context():
        db.create_all()

        # ── Verificar se já existe seed ─────────────────────────
        if Participante.query.first():
            print('⚠️  Banco já possui dados. Pulando seed.')
            return

        # ── Admin ────────────────────────────────────────────────
        admin = Participante(
            nome='Administrador',
            nickname='Admin',
            email='admin@acutisgame.com',
            whatsapp='(11) 00000-0000',
            is_admin=True,
        )
        admin.set_senha('admin123')
        db.session.add(admin)
        print('✅ Admin criado: admin@acutisgame.com / admin123')

        # ── Participantes de teste ───────────────────────────────
        participantes_data = [
            ('João Silva', 'JoaoGamer', 'joao@email.com', '(11) 91111-1111'),
            ('Maria Santos', 'MariaXP', 'maria@email.com', '(11) 92222-2222'),
            ('Pedro Oliveira', 'PedroPro', 'pedro@email.com', '(11) 93333-3333'),
            ('Ana Costa', 'AnaPlay', 'ana@email.com', '(11) 94444-4444'),
            ('Lucas Lima', 'LucasTop', 'lucas@email.com', '(11) 95555-5555'),
            ('Beatriz Souza', 'BiaGamer', 'bia@email.com', '(11) 96666-6666'),
            ('Gabriel Ferreira', 'GabeXP', 'gabe@email.com', '(11) 97777-7777'),
            ('Juliana Alves', 'JuliPlay', 'juliana@email.com', '(11) 98888-8888'),
        ]

        for nome, nick, email, wpp in participantes_data:
            p = Participante(
                nome=nome,
                nickname=nick,
                email=email,
                whatsapp=wpp,
            )
            p.set_senha('1234')
            db.session.add(p)

        print(f'✅ {len(participantes_data)} participantes de teste criados (senha: 1234)')

        # ── Atividades com QR Codes ──────────────────────────────
        atividades_data = [
            ('Arena Principal', 'Escaneie o QR Code na arena principal do evento', 20),
            ('Stand de Games', 'Visite o stand de jogos e escaneie o QR', 15),
            ('Palestra Carlo Acutis', 'Participe da palestra sobre Carlo Acutis', 30),
            ('Quiz Bíblico', 'Complete o quiz bíblico no totem', 25),
            ('Desafio de Perguntas', 'Responda ao desafio no painel interativo', 20),
            ('Sala de Oração', 'Visite a sala de oração e reflexão', 35),
            ('Stand Eucarístico', 'Aprenda sobre os milagres eucarísticos', 25),
            ('Photo Booth', 'Tire uma foto no Photo Booth temático', 10),
            ('Workshop Tech', 'Participe do workshop de tecnologia', 30),
            ('Confraternização', 'Participe da confraternização final', 15),
        ]

        qr_pasta = app.config['QRCODE_FOLDER']
        for nome, desc, pts in atividades_data:
            a = Atividade(nome=nome, descricao=desc, pontos=pts)
            db.session.add(a)
            db.session.flush()
            gerar_qrcode(a.codigo, qr_pasta, "http://192.168.0.46:5000")

        print(f'✅ {len(atividades_data)} atividades criadas com QR Codes')

        # ── Badges ───────────────────────────────────────────────
        badges_data = [
            ('Primeiro Scan', 'Completou a primeira atividade', '🎯', 'scans', 1),
            ('Explorador', 'Completou 3 atividades', '🧭', 'scans', 3),
            ('Aventureiro', 'Completou 5 atividades', '⚔️', 'scans', 5),
            ('Mestre', 'Completou 8 atividades', '👑', 'scans', 8),
            ('Completista', 'Completou todas as atividades', '🏆', 'scans', 10),
            ('Pontuador', 'Alcançou 50 pontos', '💎', 'pontos', 50),
            ('Centurião', 'Alcançou 100 pontos', '🔥', 'pontos', 100),
            ('Lenda', 'Alcançou 200 pontos', '⭐', 'pontos', 200),
            ('Streak Fire', 'Atingiu streak de 3', '🔥', 'streak', 3),
            ('Combo Master', 'Atingiu streak de 5', '💥', 'streak', 5),
            ('Level 3', 'Alcançou nível 3', '📈', 'nivel', 3),
            ('Level 5', 'Alcançou nível 5', '🚀', 'nivel', 5),
        ]

        for nome, desc, icone, tipo, valor in badges_data:
            b = Badge(nome=nome, descricao=desc, icone=icone,
                      requisito_tipo=tipo, requisito_valor=valor)
            db.session.add(b)

        print(f'✅ {len(badges_data)} badges criados')

        db.session.commit()
        print()
        print('═' * 50)
        print('  ✝ Seed concluído com sucesso!')
        print('  Admin: admin@acutisgame.com / admin123')
        print('  Participantes: senha "1234"')
        print('═' * 50)


if __name__ == '__main__':
    seed()
