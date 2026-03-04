import os
import requests
from datetime import datetime, timedelta
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

USER = os.getenv("RELOGIO_USER")
PASSWORD = os.getenv("RELOGIO_PASSWORD")
TIMEZONE = os.getenv("RELOGIO_TIMEZONE", "-0300")
TIME_COMPENSATION_SECONDS = int(os.getenv("RELOGIO_COMPENSATION_SECONDS", "1"))

RELOGIOS = os.getenv("RELOGIOS").split(",")


def sincronizar_relogio(nome, ip):
    base_url = f"https://{ip}"

    print(f"\nSincronizando: {nome} ({ip})")

    try:
        # LOGIN
        r = requests.post(
            f"{base_url}/login.fcgi",
            json={"login": USER, "password": PASSWORD},
            verify=False,
            timeout=10,
        )
        r.raise_for_status()

        session = r.json()["session"]

        print(f"Sessao {nome}: {session}")

        # HORA ATUAL
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

        print(f"JSON enviado para {nome}: {payload}")

        # ATUALIZA RELOGIO
        r = requests.post(
            f"{base_url}/set_system_date_time.fcgi",
            params={"session": session, "mode": 671},
            json=payload,
            verify=False,
            timeout=10,
        )

        if r.status_code == 200:
            print(f"OK - {nome} sincronizado")
        else:
            print(f"ERRO - {nome}: {r.text}")

        # LOGOUT
        requests.post(
            f"{base_url}/logout.fcgi",
            params={"session": session},
            verify=False,
            timeout=10,
        )

    except Exception as e:
        print(f"FALHA - {nome}: {e}")


def main():
    for item in RELOGIOS:
        nome, ip = item.split("|")
        sincronizar_relogio(nome.strip(), ip.strip())


if __name__ == "__main__":
    main()