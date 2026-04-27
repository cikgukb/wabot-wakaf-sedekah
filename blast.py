import anthropic
import requests
import os
import time
import random
from datetime import datetime, timezone, timedelta

MYT = timezone(timedelta(hours=8))  # Malaysia Time UTC+8

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
    today = datetime.now(MYT).strftime("%Y-%m-%d")
    return today in content

def save_blast_log(gist_id):
    headers = {
        "Authorization": f"token {GITHUB_GIST_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    today = datetime.now(MYT).strftime("%Y-%m-%d %H:%M MYT")
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
    "wakaf perniagaan untuk keberkatan rezeki",
    "sedekah dari keuntungan perniagaan setiap hari",
    "cara peniaga Islam urus zakat perniagaan dengan betul",
    "infaq untuk pekerja dan kakitangan yang susah",
    "wakaf peralatan perniagaan untuk manfaat komuniti",
    "amalan peniaga soleh sebelum buka kedai pagi hari",
    "berkat perniagaan melalui sedekah jariah yang konsisten",
    "wakaf sebagai perancangan kewangan jangka panjang peniaga",
    "sedekah produk atau perkhidmatan kepada yang memerlukan",
    "kisah peniaga berjaya kerana amalkan sedekah dan wakaf",
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
            print(f"  HTTP {response.status_code} | {response.text[:200]}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") in ("success", True, 1) or data.get("error") == False:
                        success += 1
                    else:
                        print(f"  ⚠️ API error: {data}")
                        failed += 1
                except Exception:
                    success += 1  # fallback: assume 200 = ok
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

def test_send_to_number(message, number="60133700200"):
    url = "https://app.wabot.my/api/send"
    payload = {
        "number": number,
        "type": "text",
        "message": message,
        "instance_id": WABOT_INSTANCE_ID,
        "access_token": WABOT_ACCESS_TOKEN
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":

    # ── DIAGNOSTIC: test hantar ke nombor + 1 group ──
    print("🚀 Generating tips wakaf & sedekah...")
    tips = generate_tips()
    print(f"📝 Tips hari ini:\n{tips}\n")

    print("📤 DIAG 1: Test hantar ke nombor 0133700200...")
    result = test_send_to_number(tips)
    print(f"{'✅ Berjaya!' if result else '❌ Gagal!'}\n")

    print("📤 DIAG 2: Test hantar ke group pertama...")
    test_send_to_number.__doc__  # no-op
    url = "https://app.wabot.my/api/send_group"
    import requests as _req
    payload = {
        "group_id": GROUP_IDS[0],
        "type": "text",
        "message": "[TEST DIAGNOSTIK] " + tips[:100],
        "instance_id": WABOT_INSTANCE_ID,
        "access_token": WABOT_ACCESS_TOKEN
    }
    r = _req.post(url, json=payload, timeout=10)
    print(f"HTTP Status: {r.status_code}")
    print(f"Response body: {r.text}")

    # ── GROUP BLAST (disabled sementara diagnostic) ──
    # gist_id = get_gist_id()
    # if already_blasted_today():
    #     print("⛔ BERHENTI — Blast dah dibuat hari ni.")
    #     exit(0)
    # blast_to_groups(tips)
    # save_blast_log(gist_id)
