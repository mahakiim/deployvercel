import requests
from datetime import datetime
from zoneinfo import ZoneInfo

ADM_CODES = {
    "32.04.12.2002": "bojongsoang",
    "32.04.12.2003": "dayeuhkolot"
}

def get_next_weather(adm_code: str):
    url = f'https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={adm_code}'
    res = requests.get(url)
    if res.status_code != 200:
        return None

    payload = res.json().get("data", [])
    if not payload:
        return None

    for cuaca in payload[0].get("cuaca", []):
        for item in cuaca:
            waktu_utc = datetime.strptime(item["datetime"], "%Y-%m-%dT%H:%M:%SZ") \
                              .replace(tzinfo=ZoneInfo("UTC"))
            waktu_wib = waktu_utc.astimezone(ZoneInfo("Asia/Jakarta"))
            if waktu_wib > datetime.now(ZoneInfo("Asia/Jakarta")):
                key = waktu_wib.strftime("%Y-%m-%d-%H_%M_%S")
                return {key: item["tp"]}
    return None

def fetch_all_locations():
    hasil = {}
    for code, nama in ADM_CODES.items():
        data = get_next_weather(code)
        hasil[nama] = data if data else {"error": "Data tidak ditemukan"}
    return hasil
