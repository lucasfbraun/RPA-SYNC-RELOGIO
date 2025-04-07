
import requests
import os
import urllib3
import json

# Desabilita os avisos de SSL (apenas para ambientes de teste)
urllib3.disable_warnings()

# === CONFIGURAÇÕES ===
login_url = "https://10.1.1.212/login.fcgi"
export_url_base = "https://10.1.1.212/export_users_csv.fcgi?session="

# Credenciais de login
dados_login = {"login": "admin", "password": "admin"}
headers = {'Content-Type': 'application/json'}

# Caminho de saída do arquivo
output_dir = r"X:\GRUPOS\Administrativo\T.I\relogio ponto backup"
output_file = os.path.join(output_dir, "usuarios_exportados_matriz.txt")

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
            print("Token de sessão não encontrado na resposta.")
        else:
            # === EXPORTAÇÃO ===
            export_url = export_url_base + session_token
            resposta_export = sessao.post(export_url, verify=False)

            if resposta_export.status_code == 200:
                with open(output_file, "w", encoding="utf-8") as file:
                    file.write(resposta_export.text)
                print(f"Arquivo exportado com sucesso para: {output_file}")
            else:
                print(f"Erro ao exportar usuários. Código: {resposta_export.status_code}")
                print("Resposta do servidor:", resposta_export.text)

    elif resposta_login.status_code == 401:
        print("Falha no login: credenciais inválidas")
    else:
        print(f"Erro no login. Código: {resposta_login.status_code}")
        print("Resposta do servidor:", resposta_login.text)

except requests.exceptions.RequestException as e:
    print(f"Ocorreu um erro de requisição: {e}")

except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
