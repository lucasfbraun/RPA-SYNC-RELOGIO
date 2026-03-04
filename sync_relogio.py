import requests
from datetime import datetime, timedelta
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

IP = "10.1.1.212"
USER = "admin"
PASSWORD = "admin"
TIMEZONE = "-0300"
TIME_COMPENSATION_SECONDS = 1  # compensa pequeno atraso

BASE_URL = f"https://{IP}"

def main():
    # 1) Login
    r = requests.post(
        f"{BASE_URL}/login.fcgi",
        json={"login": USER, "password": PASSWORD},
        verify=False,
        timeout=10,
    )
    r.raise_for_status()
    session = r.json()["session"]
    print("Sessao:", session)

    try:
        # 2) Hora atual do PC (+ compensacao)
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

        # 3) Ajustar data/hora (mode=671)
        r = requests.post(
            f"{BASE_URL}/set_system_date_time.fcgi",
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
        # 4) Logout
        try:
            requests.post(
                f"{BASE_URL}/logout.fcgi",
                params={"session": session},
                verify=False,
                timeout=10,
            )
        except Exception:
            pass
        print("Sessao encerrada")

if __name__ == "__main__":
    main()