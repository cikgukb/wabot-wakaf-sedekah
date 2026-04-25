import anthropic
import requests
import os
import time
import random
from datetime import datetime, timezone

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
WABOT_ACCESS_TOKEN = os.environ["WABOT_ACCESS_TOKEN"]
WABOT_INSTANCE_ID = os.environ["WABOT_INSTANCE_ID"]
GITHUB_GIST_TOKEN = os.environ["GIST_TOKEN"]

GIST_FILENAME = "wabot_wakaf_blast_log.txt"

GROUP_IDS = [
    '120363203611848994@g.us',
    '120363026955429508@g.us',
    '60122205282-1350012583@g.us',
    '120363199008198609@g.us',
    '60108488568-1539924585@g.us',
    '60133815817-1567820351@g.us',
    '60163106500-1378443859@g.us',
    '60123447769-1384737660@g.us',
    '120363171196600561@g.us',
    '60193223737-1383964878@g.us',
    '601132027474-1622551043@g.us',
    '120363169842769179@g.us',
    '60122077410-1412868614@g.us',
    '120363202533005418@g.us',
    '120363045131155813@g.us',
    '120363023179117022@g.us',
    '120363293170597545@g.us',
    '120363027369738197@g.us',
]

# ─── GitHub Gist Safety Check ────────────────────────────────────────────────

def get_gist_id():
    headers = {
        "Authorization": f"token {GITHUB_GIST_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    r = requests.get("https://api.github.com/gists", headers=headers)
    for gist in r.json():
        if GIST_FILENAME in gist.get("files", {}):
            return gist["id"]
    payload = {
        "description": "Wabot Wakaf Blast Log",
        "public": False,
        "files": {GIST_FILENAME: {"content": "init"}}
    }
    r = requests.post("https://api.github.com/gists", headers=headers, json=payload)
    return r.json()["id"]

def already_blasted_today():
    headers = {
        "Authorization": f"token {GITHUB_GIST_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    gist_id = get_gist_id()
    r = requests.get(f"https://api.github.com/gists/{gist_id}", headers=headers)
    content = r.json()["files"][GIST_FILENAME]["content"]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return today in content

def save_blast_log(gist_id):
    headers = {
        "Authorization": f"token {GITHUB_GIST_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    payload = {
        "files": {GIST_FILENAME: {"content": f"Last blast: {today}"}}
    }
    requests.patch(f"https://api.github.com/gists/{gist_id}", headers=headers, json=payload)
    print(f"✅ Log disimpan: {today}")

# ─── Core Functions ───────────────────────────────────────────────────────────

TOPICS = [
    "kelebihan berwakaf dalam Islam",
    "cara wakaf tunai untuk orang biasa",
    "wakaf produktif dan manfaatnya",
    "wakaf ilmu dan pendidikan",
    "sedekah jariah yang berterusan",
    "cara sedekah yang betul mengikut sunnah",
    "sedekah kepada anak yatim",
    "kelebihan sedekah di waktu subuh",
    "infaq fi sabilillah",
    "perbezaan zakat dan sedekah",
    "wakaf digital dan platform online",
    "sedekah rahsia dan ganjarannya",
    "sedekah kepada ibu bapa",
    "wakaf tanah dan hartanah",
    "sedekah makanan kepada yang memerlukan",
    "wakaf saham dan instrumen kewangan Islam",
    "cara niatkan sedekah dengan betul",
    "sedekah dalam keadaan susah",
    "manfaat wakaf kepada masyarakat",
    "kisah inspirasi orang yang berwakaf",
    "fadilat sedekah khusus untuk golongan peniaga",
]

def generate_tips():
    today_str = datetime.now(timezone.utc).strftime("%A, %d %B %Y")
    topic = random.choice(TOPICS)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""Kau adalah penasihat wakaf dan sedekah untuk masyarakat Muslim Malaysia.

Hari ini: {today_str}
Topik wajib: {topic}

Tulis SATU tips atau perkongsian ilmu tentang topik di atas dalam Bahasa Melayu.
Format:
- Mulakan dengan emoji yang sesuai (contoh: 🌙 💎 🤲 ✨)
- Tajuk tips (bold dengan *teks*)
- 3-4 baris penjelasan ringkas berdasarkan Al-Quran atau Hadis jika sesuai
- 1 ayat penutup yang memberi semangat untuk beramal
- Gaya: lembut, penuh hikmah, bukan menghukum
- Jangan guna perkataan: unlock, delve, realm, harness
- Pastikan perkongsian ini PRAKTIKAL dan boleh diamalkan hari ini"""
        }]
    )
    return message.content[0].text

def blast_to_groups(message):
    url = "https://app.wabot.my/api/send_group"
    success = 0
    failed = 0
    total = len(GROUP_IDS)

    for i, group_id in enumerate(GROUP_IDS, 1):
        payload = {
            "group_id": group_id,
            "type": "text",
            "message": message,
            "instance_id": WABOT_INSTANCE_ID,
            "access_token": WABOT_ACCESS_TOKEN
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                success += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Error group {group_id}: {e}")
            failed += 1

        print(f"[{i}/{total}] ✅ {success} berjaya | ❌ {failed} gagal")

        if i < total:
            delay = random.randint(15, 20)
            time.sleep(delay)

    print(f"\n🎯 SELESAI — Berjaya: {success} | Gagal: {failed} | Total: {total}")

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("🔍 Semak log blast hari ni...")
    gist_id = get_gist_id()

    if already_blasted_today():
        print("⛔ BERHENTI — Blast dah dibuat hari ni. Cuba esok.")
        exit(0)

    print("✅ Belum blast hari ni. Teruskan...\n")

    print("🚀 Generating tips wakaf & sedekah...")
    tips = generate_tips()
    print(f"📝 Tips hari ini:\n{tips}\n")

    print(f"📤 Blasting ke {len(GROUP_IDS)} groups...")
    blast_to_groups(tips)

    save_blast_log(gist_id)
