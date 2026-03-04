import os
import requests
from datetime import datetime, timedelta
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

IP = os.getenv("RELOGIO_IP")
USER = os.getenv("RELOGIO_USER")
PASSWORD = os.getenv("RELOGIO_PASSWORD")

TIMEZONE = os.getenv("RELOGIO_TIMEZONE", "-0300")
TIME_COMPENSATION_SECONDS = int(os.getenv("RELOGIO_COMPENSATION_SECONDS", "1"))

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variavel obrigatoria ausente: {name}. Configure no .env.")
    return value

def main():
    ip = require_env("RELOGIO_IP")
    user = require_env("RELOGIO_USER")
    password = require_env("RELOGIO_PASSWORD")

    base_url = f"https://{ip}"

    r = requests.post(
        f"{base_url}/login.fcgi",
        json={"login": user, "password": password},
        verify=False,
        timeout=10,
    )
    r.raise_for_status()
    session = r.json()["session"]
    print("Sessao:", session)

    try:
        now = datetime.now() + timedelta(seconds=TIME_COMPENSATION_SECONDS)
        payload = {
            "day": now.day,
            "month": now.month,
            "year": now.year,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
            "timezone": TIMEZONE,
        }

        r = requests.post(
            f"{base_url}/set_system_date_time.fcgi",
            params={"session": session, "mode": 671},
            json=payload,
            verify=False,
            timeout=10,
        )

        if r.status_code == 200:
            print("OK: Data e hora atualizadas com sucesso.")
            print("Enviado:", payload)
        else:
            print("ERRO: Falha ao atualizar. Status:", r.status_code)
            print("Resposta:", r.text)

    finally:
        try:
            requests.post(
                f"{base_url}/logout.fcgi",
                params={"session": session},
                verify=False,
                timeout=10,
            )
        except Exception:
            pass
        print("Sessao encerrada")

if __name__ == "__main__":
    main()