import os
import requests

FOLDER_LISTE = "."
FISIER_IESIRE = "doar_filme_seriale.m3u"
FISIER_NOI_2026 = "adauga_2026.txt"

# Aici poți pune link-uri M3U de pe internet sau de la servere care se actualizează zilnic cu filme 2026
LINKURI_SURSE_EXTERNE = [
    # Exemplu: "http://server.com"
]

def este_activ(url):
    try:
        r = requests.head(url, timeout=4, allow_redirects=True)
        return r.status_code == 200
    except:
        return False

def actualizeaza_tot_vod():
    linii_salvate = ["#EXTM3U"]
    linkuri_vazute = set()
    total_active = 0

    # 0. Cream fisierul adauga_2026.txt daca nu exista inca, ca sa ai unde pune filme noi
    if not os.path.exists(FISIER_NOI_2026):
        with open(FISIER_NOI_2026, "w", encoding="utf-8") as f:
            f.write("# Scrie aici filmele noi pe 2 randuri (Nume si Link) si ruleaza scriptul:\n")
            f.write("#Exemplu Film 2026\n")
            f.write("#https://link-direct-film-2026.mp4\n")

    # 1. Citim intai filmele noi din fisierul 'adauga_2026.txt' (sa apara primele in lista)
    print("Verific filmele noi din adauga_2026.txt...")
    with open(FISIER_NOI_2026, "r", encoding="utf-8", errors="ignore") as f:
        linii_noi = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
    
    for i in range(0, len(linii_noi) - 1, 2):
        titlu = linii_noi[i]
        url = linii_noi[i + 1]
        if url.startswith("http") and url not in linkuri_vazute:
            if este_activ(url):
                linkuri_vazute.add(url)
                linii_salvate.append(f'#EXTINF:-1 group-title="Filme & Seriale 2026",{titlu}')
                linii_salvate.append(url)
                total_active += 1
                print(f"  [NOU 2026 OK] {titlu}")

    # 2. Descarcam automat noutatile din sursele externe (daca ai pus link-uri sus)
    for sursa_url in LINKURI_SURSE_EXTERNE:
        print(f"Descarc noutăți de pe server extern...")
        try:
            r = requests.get(sursa_url, timeout=15)
            linii_ext = [l.strip() for l in r.text.splitlines() if l.strip()]
            for i in range(len(linii_ext) - 1):
                if linii_ext[i].startswith("#EXTINF"):
                    info = linii_ext[i]
                    url = linii_ext[i + 1]
                    if ("/movie/" in url.lower() or "/series/" in url.lower()) and url not in linkuri_vazute:
                        linkuri_vazute.add(url)
                        linii_salvate.append(info)
                        linii_salvate.append(url)
                        total_active += 1
        except Exception as e:
            print(f"  Eroare la sursa externă: {e}")

    # 3. Scaneaza fisierele vechi din folder si pastreaza doar filmele/serialele active
    for nume_fisier in os.listdir(FOLDER_LISTE):
        if nume_fisier.endswith(".py") or nume_fisier in ["vod_curat.m3u", FISIER_IESIRE, FISIER_NOI_2026]:
            continue
        
        cale = os.path.join(FOLDER_LISTE, nume_fisier)
        if not os.path.isfile(cale):
            continue

        print(f"Scanez arhiva: {nume_fisier}...")
        try:
            with open(cale, "r", encoding="utf-8", errors="ignore") as f:
                linii = [l.strip() for l in f.readlines() if l.strip()]
        except:
            continue

        for i in range(len(linii) - 1):
            if linii[i].startswith("#EXTINF"):
                info = linii[i]
                url = linii[i + 1]

                este_strict_vod = (
                    "/movie/" in url.lower() or 
                    "/series/" in url.lower() or 
                    url.lower().endswith((".mp4", ".mkv", ".avi"))
                )

                if este_strict_vod and url.startswith("http") and url not in linkuri_vazute:
                    linkuri_vazute.add(url)
                    if este_activ(url):
                        linii_salvate.append(info)
                        linii_salvate.append(url)
                        total_active += 1
                        print(f"  [OK] {info.split(',')[-1]}")

    with open(FISIER_IESIRE, "w", encoding="utf-8") as out:
        out.write("\n".join(linii_salvate))

    print(f"\nGata! Lista '{FISIER_IESIRE}' este actualizată cu {total_active} filme și seriale active.")

if __name__ == "__main__":
    actualizeaza_tot_vod()