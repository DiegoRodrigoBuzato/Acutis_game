# ✝ Acutis Game — Plataforma Gamificada de Ranking em Tempo Real

Plataforma para eventos presenciais inspirada em **Carlo Acutis** (1991–2006).
Participantes escaneiam QR Codes espalhados pelo espaço para acumular pontos e subir
em um **ranking dinâmico em tempo real** exibido em telão.

---

## 🎮 Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| **Cadastro** | Nome, nickname, e-mail, WhatsApp, avatar |
| **Login** | Participantes + Admin |
| **QR Codes** | Gerados automaticamente por atividade |
| **Ranking em tempo real** | Atualizado via WebSocket (sem refresh) |
| **Telão** | Tela fullscreen para TV com ranking gigante |
| **Gamificação** | Badges, níveis, streak/combo, barra de XP |
| **Admin** | Criar atividades, ver scans, exportar CSV, resetar |
| **Tela de vencedor** | Animação de confete para anúncio final |

---

## 🛠 Tecnologias

- **Backend:** Python 3.10+ · Flask · Flask-SocketIO
- **Banco:** SQLite (sem dependência externa)
- **Frontend:** HTML5 · CSS3 · JavaScript · Socket.IO
- **QR Code:** biblioteca `qrcode` (Python)
- **Tempo real:** WebSocket via eventlet

---

## 📦 Instalação

```bash
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Rodar seed para dados de teste
python seed.py

# 5. Iniciar servidor
python app.py
```

---

## 🌐 URLs do Sistema

| URL | Descrição |
|---|---|
| `http://localhost:5000` | Página inicial |
| `http://localhost:5000/login` | Login |
| `http://localhost:5000/cadastro` | Cadastro |
| `http://localhost:5000/dashboard` | Dashboard do participante |
| `http://localhost:5000/ranking` | Ranking completo |
| `http://localhost:5000/telao` | Dashboard para TV/Telão (fullscreen) |
| `http://localhost:5000/vencedor` | Tela de anúncio do vencedor |
| `http://localhost:5000/admin` | Painel administrativo |

---

## 👤 Credenciais de Teste

| Tipo | E-mail | Senha |
|---|---|---|
| **Admin** | `admin@acutisgame.com` | `admin123` |
| **Participante** | `joao@email.com` | `1234` |
| **Participante** | `maria@email.com` | `1234` |

---

## 📁 Estrutura do Projeto

```
Ranking/
├── app.py                  # Ponto de entrada Flask + SocketIO
├── config.py               # Configurações
├── seed.py                 # Dados iniciais para teste
├── requirements.txt        # Dependências Python
├── database/               # Banco SQLite
├── models/
│   ├── __init__.py
│   └── models.py           # Modelos SQLAlchemy
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Login/Cadastro/Logout
│   ├── main.py             # Index/Dashboard/Ranking/Scan
│   ├── admin.py            # Painel administrativo
│   └── api.py              # API JSON
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Ranking, badges, QR Code, frases
├── static/
│   ├── css/main.css        # Design system completo
│   ├── img/                # Imagens
│   ├── qrcodes/            # QR Codes gerados
│   └── uploads/avatars/    # Avatares dos participantes
└── templates/
    ├── base.html           # Layout base
    ├── index.html          # Página inicial
    ├── login.html          # Login
    ├── cadastro.html       # Cadastro
    ├── dashboard.html      # Dashboard do participante
    ├── ranking.html        # Ranking completo
    ├── telao.html          # Dashboard para telão
    ├── perfil.html         # Perfil do participante
    ├── winner.html         # Tela do vencedor
    └── admin/
        ├── panel.html      # Painel admin
        ├── atividades.html # Gerenciar atividades
        ├── participantes.html # Gerenciar participantes
        └── scans.html      # Histórico de scans
```

---

## 🎯 Como Funciona

1. **Admin** cria atividades no painel → QR Codes são gerados
2. QR Codes são impressos e espalhados pelo evento
3. **Participantes** se cadastram e escaneiam QR Codes com o celular
4. Cada scan registra pontos + bônus de streak
5. **Ranking atualiza em tempo real** via WebSocket em todas as telas
6. **Telão** mostra ranking gigante com animações
7. No final, **Tela de Vencedor** anuncia o campeão com confete! 🎉

---

*"Você foi feito para o Paraíso — não perca de vista o objetivo!"* — **Carlo Acutis** ✝️


Alugue um VPS (Servidor):

Você pode usar a DigitalOcean (plano de US$ 4 ou 6/mês) ou Hostinger.
Ao criar o servidor, escolha o sistema operacional Ubuntu 22.04 ou 24.04 com o pacote Docker já instalado (na DigitalOcean chama-se Docker on Ubuntu no Marketplace).
Jogue os arquivos pra lá: Você só precisa zipar a pasta do seu projeto (menos a pasta venv que é pesada) e jogar para o servidor (via SFTP/FileZilla) ou colocar no GitHub e baixar lá dentro.

Inicie o Sistema: No painel do seu servidor (terminal), entre na pasta do projeto e digite um único comando:

bash
docker compose up -d --build

Pronto! O Docker vai baixar tudo, instalar e rodar o projeto na porta 80. A partir desse momento, qualquer pessoa que digitar o IP do seu servidor no celular, vai cair no sistema. Se você comprar um domínio (ex: www.acutisgame.com.br), é só apontar pra esse IP.

⚠️ DICA DE OURO PRO EVENTO: Quando o sistema estiver rodando no servidor oficial (seja pelo IP dele ou pelo domínio), você entra no /admin, apaga as atividades antigas e Cria Novas Atividades. Assim, os novos QR Codes gerados já vão sair impressos com a URL oficial da nuvem e você pode imprimir e espalhar pelo evento.

E se precisar de uma mãozinha minha na hora de jogar os arquivos no servidor, é só chamar!

