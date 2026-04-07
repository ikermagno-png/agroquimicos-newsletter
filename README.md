# AgroQuímicos Brasil Newsletter

Sistema automatizado de newsletter diária sobre agroquímicos no Brasil, rodando no GitHub Actions.

## Funcionalidades

- **Scraping automático** de múltiplos sites brasileiros sobre agroquímicos
- **Monitoramento do MAPA Agrofit** para novos registros
- **Newsletter em HTML** profissional com tema agrícola
- **Envio automático via e-mail** (GMail)
- **Execução agendada** todo dia ao meio-dia (horário de Brasília)

## Segmentos Cobertos

- Herbicidas
- Fungicidas
- Inseticidas
- Acaricidas
- Nematicidas
- Adjuvantes
- Biodefensivos & Bioinsumos
- Fertilizantes Foliares
- Registros Oficiais MAPA

## Fontes Monitoradas

### Portais de Notícias
- Agrolink (RSS)
- Grupo Cultivar (RSS)
- Agronegócio
- Agropage

### Sites de Empresas
- Bayer Crop Science
- Syngenta Brasil
- Corteva Agriscience
- Nortox
- UPL Brasil

### Governamental
- MAPA Agrofit (Registros Oficiais)

## Estrutura do Projeto

```
agroquimicos-newsletter/
├── .github/
│   └── workflows/
│       └── newsletter.yml    # Workflow do GitHub Actions
├── logs/                     # Logs de execução (gerado automaticamente)
├── scraper.py                # Coleta de dados dos sites
├── newsletter.py             # Geração do HTML da newsletter
├── send_email.py             # Envio de e-mail via SMTP
├── main.py                   # Script principal
├── requirements.txt          # Dependências Python
└── README.md                 # Este arquivo
```

## Configuração

### Opção 1: SMTP2GO (Recomendado - Gratuito)

O SMTP2GO é um serviço gratuito que permite enviar até 1.000 e-mails/mês sem precisar de senha de app.

#### Passo 1: Criar conta no SMTP2GO

1. Acesse: **https://www.smtp2go.com**
2. Clique em **"Sign Up Free"**
3. Preencha os dados:
   - Email: seu e-mail
   - Senha: crie uma senha
4. Confirme seu e-mail clicando no link que receber

#### Passo 2: Obter credenciais SMTP

1. Após logar, vá em **Settings** → **SMTP Users**
2. Clique no usuário padrão (ou crie um novo)
3. Copie:
   - **Username SMTP** (geralmente seu e-mail)
   - **Password SMTP** (sua senha da conta SMTP2GO)

#### Passo 3: Configurar secrets no GitHub

No seu repositório: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Nome do Secret | Valor |
|----------------|-------|
| `SENDER_EMAIL` | Seu e-mail cadastrado no SMTP2GO |
| `SENDER_PASSWORD` | Sua senha SMTP2GO |
| `RECIPIENT_EMAIL` | E-mail que receberá a newsletter |
| `SMTP_PROVIDER` | `smtp2go` |

---

### Opção 2: Gmail com Senha de App

Se você tem uma conta Gmail pessoal (não estudantil/empresarial):

#### Passo 1: Ativar verificação em duas etapas

1. Acesse: **https://myaccount.google.com/security**
2. Ative a "Verificação em duas etapas"

#### Passo 2: Gerar senha de app

1. Vá em **https://myaccount.google.com/apppasswords**
2. Selecione "Outro (nome personalizado)"
3. Digite "Newsletter" e clique em "Gerar"
4. Copie a senha de 16 caracteres

#### Passo 3: Configurar secrets no GitHub

| Nome do Secret | Valor |
|----------------|-------|
| `SENDER_EMAIL` | Seu Gmail |
| `SENDER_PASSWORD` | Senha de app de 16 caracteres |
| `RECIPIENT_EMAIL` | E-mail de destino |
| `SMTP_PROVIDER` | `gmail` (ou deixe vazio) |

---

### Opção 3: Brevo (Gratuito - 300 e-mails/dia)

1. Acesse: **https://www.brevo.com**
2. Crie uma conta gratuita
3. Vá em **SMTP & API** → copie suas credenciais
4. Configure o secret `SMTP_PROVIDER` como `brevo`

## Execução

### Automática

O workflow roda automaticamente todo dia às **15:00 UTC** (12:00 horário de Brasília).

### Manual

Para testar, você pode executar manualmente:

1. Vá na aba **Actions** do repositório
2. Selecione o workflow "Newsletter Agroquímicos Brasil"
3. Clique em **Run workflow**

### Local (para desenvolvimento)

```bash
# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
export SENDER_EMAIL="seu_email@gmail.com"
export SENDER_PASSWORD="sua_senha_de_app"
export RECIPIENT_EMAIL="email_destino@gmail.com"

# Execute
python main.py
```

## Verificando os Logs

Após cada execução, um arquivo de log é gerado na pasta `logs/` do repositório. Você pode:

1. Ver os logs diretamente no GitHub (pasta logs/)
2. Ver o histórico de execuções na aba **Actions**
3. Clicar em uma execução específica para ver o output completo

## Personalização

### Adicionar Novos Sites

Edite o arquivo `scraper.py` e adicione uma nova entrada no dicionário `SITES_CONFIG`:

```python
'novo_site': {
    'name': 'Nome do Site',
    'base_url': 'https://www.exemplo.com.br',
    'type': 'rss',  # ou 'scrape'
    'rss': 'https://www.exemplo.com.br/rss',  # se for RSS
    'segments': ['todos']  # ou segmentos específicos
}
```

### Alterar Horário de Execução

Edite o arquivo `.github/workflows/newsletter.yml`:

```yaml
schedule:
  - cron: '0 15 * * *'  # Minuto Hora Dia Mês DiaDaSemana
```

Para Brasília (UTC-3):
- 12:00 → 15:00 UTC
- 08:00 → 11:00 UTC

## Troubleshooting

### E-mail não enviado

- Verifique se a **verificação em duas etapas** está ativa na conta Google
- Verifique se está usando a **senha de app** correta (não a senha normal)
- Verifique se os secrets estão configurados corretamente no GitHub

### Nenhuma notícia coletada

- Alguns sites podem bloquear o scraping
- Verifique os logs na pasta `logs/`
- O sistema usa delays e headers para evitar bloqueios

### Workflow falhou

1. Vá em **Actions** → clique na execução que falhou
2. Clique no job para ver o log detalhado
3. Verifique se todas as dependências foram instaladas
4. Verifique se os secrets estão configurados

## Licença

MIT License

## Autor

Newsletter automatizada criada para monitoramento de agroquímicos no Brasil.