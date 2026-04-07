# AgroQuímicos Brasil Newsletter

Newsletter diária automatizada sobre agroquímicos no Brasil, rodando no GitHub Actions.

## Funcionalidades

- **Scraping automático** de múltiplos sites brasileiros sobre agroquímicos
- **Monitoramento do MAPA Agrofit** para novos registros
- **Newsletter em HTML** profissional com tema agrícola
- **Envio automático via e-mail** (SMTP2GO, Gmail, Brevo)
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
- Bayer Crop Science Brasil
- Syngenta Brasil
- Corteva Agriscience
- Nortox
- UPL Brasil

### Governamental
- MAPA Agrofit (Registros Oficiais)

## Configuração

### Opção 1: SMTP2GO (Recomendado - Grátis)

O SMTP2GO permite enviar até 1.000 e-mails/mês gratuitamente.

#### Passo 1: Criar conta no SMTP2GO

1. Acesse: **https://www.smtp2go.com**
2. Clique em **"Sign Up Free"**
3. Preencha os dados e confirme seu e-mail

#### Passo 2: Obter credenciais SMTP

1. Faça login no SMTP2GO
2. Vá em **Settings** → **SMTP Users**
3. Copie seu **Username** (geralmente seu e-mail) e **Password**

#### Passo 3: Configurar secrets no GitHub

No repositório: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Nome do Secret | Valor |
|----------------|-------|
| `SENDER_EMAIL` | Seu e-mail cadastrado no SMTP2GO |
| `SENDER_PASSWORD` | Sua senha SMTP2GO |
| `RECIPIENT_EMAIL` | E-mail que receberá a newsletter |
| `SMTP_PROVIDER` | `smtp2go` |

---

### Opção 2: Gmail com Senha de App

Se você tem uma conta Gmail pessoal (não estudantil/empresarial):

1. Ative a verificação em duas etapas
2. Gere uma senha de app em: https://myaccount.google.com/apppasswords
3. Configure os secrets:
   - `SMTP_PROVIDER`: `gmail`
   - `SENDER_PASSWORD`: senha de app de 16 caracteres

---

### Opção 3: Brevo (Grátis - 300 e-mails/dia)

1. Crie conta em: https://www.brevo.com
2. Vá em **SMTP & API** → copie as credenciais
3. Configure o secret `SMTP_PROVIDER` como `brevo`

---

## Execução

### Automática

O workflow roda automaticamente todo dia às **15:00 UTC** (12:00 horário de Brasília).

### Manual

Para testar:

1. Vá na aba **Actions** do repositório
2. Selecione o workflow "Newsletter AgroQuímicos Brasil"
3. Clique em **Run workflow**
4. Acompanhe a execução em tempo real

### Local (para desenvolvimento)

```bash
# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
export SENDER_EMAIL="seu_email"
export SENDER_PASSWORD="sua_senha"
export RECIPIENT_EMAIL="email_destino"
export SMTP_PROVIDER="smtp2go"  # ou gmail, brevo

# Execute
python main.py
```

## Verificando os Logs

Após cada execução:

1. Um arquivo JSON é salvo na pasta `logs/`
2. O HTML é gerado e enviado por e-mail
3. Veja o histórico na aba **Actions** do GitHub

## Estrutura do Projeto

```
agroquimicos-newsletter/
├── .github/workflows/newsletter.yml  # Workflow GitHub Actions
├── scraper.py                        # Coleta dados dos sites
├── newsletter.py                     # Gera HTML da newsletter
├── send_email.py                     # Envia e-mail via SMTP
├── main.py                           # Script principal
├── requirements.txt                  # Dependências Python
└── README.md                         # Este arquivo
```

## Troubleshooting

### E-mail não enviado

- Verifique se as credenciais SMTP estão corretas
- Para SMTP2GO, confirme seu e-mail na conta
- Verifique os secrets no GitHub Actions

### Nenhuma notícia coletada

- Alguns sites podem bloquear o scraping
- Verifique os logs na pasta `logs/`
- O sistema usa delays e headers para evitar bloqueios

### Workflow falhou

1. Vá em **Actions** → clique na execução que falhou
2. Veja o log detalhado
3. Verifique se os secrets estão configurados

## Licença

MIT License

## Autor

Newsletter automatizada para monitoramento de agroquímicos no Brasil.