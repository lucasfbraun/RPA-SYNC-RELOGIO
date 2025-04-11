import requests
import os
import urllib3
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Desabilita os avisos de SSL (apenas para ambientes de teste)
urllib3.disable_warnings()

# === CONFIGURAÇÕES ===
login_url = "https://186.195.226.138:4210/login.fcgi"
export_url_base = "https://186.195.226.138:4210/export_users_csv.fcgi?session="

# Credenciais de login
dados_login = {"login": "admin", "password": "admin"}
headers = {'Content-Type': 'application/json'}

# Caminho de saída do arquivo
output_dir = r"X:\GRUPOS\Gestão de Pessoas\DP\DP\Cartão ponto\Backup relógio ponto\Filial MG"
output_file = os.path.join(output_dir, "usuarios_exportados_filialmg.txt")

# Configurações do servidor SMTP
smtp_server = 'smtp.office365.com'  # Exemplo: 'smtp.gmail.com'
smtp_port = 587  # Porta comum para TLS
smtp_username = 'noreply@grupoflexivel.com.br'
smtp_password = 'Flex@2025!@'
destinatario = 'sistemas@grupoflexivel.com.br'

def enviar_email(assunto, corpo, destinatario):
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Inicia a conexão segura
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Falha ao enviar e-mail: {e}")

try:
    # === LOGIN ===
    sessao = requests.Session()
    resposta_login = sessao.post(login_url, json=dados_login, verify=False, headers=headers)

    if resposta_login.status_code == 200:
        print("Login bem-sucedido!")

        # Pega o token de sessão da resposta
        resposta_json = resposta_login.json()
        session_token = resposta_json.get("session")

        if not session_token:
            mensagem = "Token de sessão não encontrado na resposta."
            print(mensagem)
            enviar_email("Falha na Exportação de Usuários", mensagem, destinatario)
        else:
            # === EXPORTAÇÃO ===
            export_url = export_url_base + session_token
            resposta_export = sessao.post(export_url, verify=False)

            if resposta_export.status_code == 200:
                with open(output_file, "w", encoding="utf-8") as file:
                    file.write(resposta_export.text)
                mensagem = f"Arquivo exportado com sucesso para: {output_file}"
                print(mensagem)
                enviar_email("Backup relógio ponto filial MG finalizado com sucesso", mensagem, destinatario)
            else:
                mensagem = f"Erro ao efetuar relógio ponto filial MG : {resposta_export.status_code}\nResposta do servidor: {resposta_export.text}"
                print(mensagem)
                enviar_email("Erro ao efetuar relógio ponto filial MG", mensagem, destinatario)

    elif resposta_login.status_code == 401:
        mensagem = "Falha no login: credenciais inválidas"
        print(mensagem)
        enviar_email("Falha no Login", mensagem, destinatario)
    else:
        mensagem = f"Erro no login. Código: {resposta_login.status_code}\nResposta do servidor: {resposta_login.text}"
        print(mensagem)
        enviar_email("Erro no Login", mensagem, destinatario)

except requests.exceptions.RequestException as e:
    mensagem = f"Ocorreu um erro de requisição: {e}"
    print(mensagem)
    enviar_email("Erro de Requisição", mensagem, destinatario)

except Exception as e:
    mensagem = f"Ocorreu um erro inesperado: {e}"
    print(mensagem)
    enviar_email("Erro Inesperado", mensagem, destinatario)