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
    """Fetch or create GitHub Gist for blast logging."""
    headers = {
        "Authorization": f"token {GITHUB_GIST_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        r = requests.get("https://api.github.com/gists", headers=headers, timeout=10)
        
        # Validate HTTP response
        if r.status_code != 200:
            print(f"⚠️  GitHub API error: {r.status_code}")
            print(f"Response: {r.text[:500]}")
            raise Exception(f"GitHub API returned {r.status_code}")
        
        # Parse JSON and validate it's a list
        data = r.json()
        if not isinstance(data, list):
            print(f"⚠️  Unexpected API response format (not a list): {type(data)}")
            raise Exception("GitHub API returned unexpected format")
        
        # Search for existing gist with our filename
        for gist in data:
            if not isinstance(gist, dict):
                print(f"⚠️  Skipping non-dict gist entry: {type(gist)}")
                continue
            
            files = gist.get("files", {})
            if isinstance(files, dict) and GIST_FILENAME in files:
                print(f"✅ Found existing gist: {gist['id']}")
                return gist["id"]
        
        # If not found, create new gist
        print("📝 Creating new gist...")
        payload = {
            "description": "Wabot Wakaf Blast Log",
            "public": False,
            "files": {GIST_FILENAME: {"content": "init"}}
        }
        r = requests.post("https://api.github.com/gists", headers=headers, json=payload, timeout=10)
        
        if r.status_code not in (200, 201):
            print(f"⚠️  Failed to create gist: {r.status_code}")
            print(f"Response: {r.text[:500]}")
            raise Exception(f"Failed to create gist: {r.status_code}")
        
        new_gist = r.json()
        if not isinstance(new_gist, dict) or "id" not in new_gist:
            print(f"⚠️  Unexpected create response: {new_gist}")
            raise Exception("Invalid gist creation response")
        
        gist_id = new_gist["id"]
        print(f"✅ Created new gist: {gist_id}")
        return gist_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        raise
    except Exception as e:
        print(f"❌ Error in get_gist_id: {e}")
        raise

def already_blasted_today():
    """Check if we already blasted today."""
    try:
        headers = {
            "Authorization": f"token {GITHUB_GIST_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        gist_id = get_gist_id()
        r = requests.get(f"https://api.github.com/gists/{gist_id}", headers=headers, timeout=10)
        
        if r.status_code != 200:
            print(f"⚠️  Failed to fetch gist content: {r.status_code}")
            return False  # Assume not blasted if we can't check
        
        gist_data = r.json()
        if not isinstance(gist_data, dict) or "files" not in gist_data:
            print(f"⚠️  Unexpected gist response format")
            return False
        
        content = gist_data["files"].get(GIST_FILENAME, {}).get("content", "")
        today = datetime.now(MYT).strftime("%Y-%m-%d")
        return today in content
        
    except Exception as e:
        print(f"⚠️  Error checking blast status: {e}")
        return False  # Assume not blasted to allow retry

def save_blast_log(gist_id):
    """Save blast timestamp to gist."""
    try:
        headers = {
            "Authorization": f"token {GITHUB_GIST_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        today = datetime.now(MYT).strftime("%Y-%m-%d %H:%M MYT")
        payload = {
            "files": {GIST_FILENAME: {"content": f"Last blast: {today}"}}
        }
        r = requests.patch(f"https://api.github.com/gists/{gist_id}", headers=headers, json=payload, timeout=10)
        
        if r.status_code != 200:
            print(f"⚠️  Failed to save log: {r.status_code}")
        else:
            print(f"✅ Log disimpan: {today}")
            
    except Exception as e:
        print(f"⚠️  Error saving blast log: {e}")

# ─── Core Functions ────────────────────────────────────────────────────────

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

# ─── Main ───────────────────────────────────────────────────────────

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

    # ── Safety check: jangan blast 2x sehari ──
    try:
        gist_id = get_gist_id()
        print("🔍 Semak log blast hari ni...")
        if already_blasted_today():
            print("⛔ BERHENTI — Blast dah dibuat hari ni. Cuba esok.")
            exit(0)
        print("✅ Belum blast hari ni. Teruskan...\n")
    except Exception as e:
        print(f"❌ Fatal error during safety check: {e}")
        exit(1)

    # ── Generate tips ──
    try:
        print("🚀 Generating tips wakaf & sedekah...")
        tips = generate_tips()
        print(f"📝 Tips hari ini:\n{tips}\n")
    except Exception as e:
        print(f"❌ Failed to generate tips: {e}")
        exit(1)

    # ── BLAST KE 18 GROUPS ──
    print(f"📤 Blasting ke {len(GROUP_IDS)} groups...")
    blast_to_groups(tips)

    # ── Save log supaya tak double-blast ──
    try:
        save_blast_log(gist_id)
    except Exception as e:
        print(f"⚠️  Warning: Could not save blast log: {e}")
