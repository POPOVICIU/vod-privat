import os
import requests

FISIER_LISTA = "doar_filme_seriale.m3u"
FISIER_NOI_2026 = "adauga_2026.txt"

def este_activ(url):
    try:
        r = requests.head(url, timeout=4, allow_redirects=True)
        return r.status_code == 200
    except:
        return False

def actualizeaza_zilnic():
    linii_salvate = ["#EXTM3U"]
    linkuri_vazute = set()

    # 1. Citeste noutatile din adauga_2026.txt si le pune primele
    if os.path.exists(FISIER_NOI_2026):
        with open(FISIER_NOI_2026, "r", encoding="utf-8", errors="ignore") as f:
            linii_noi = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
        for i in range(0, len(linii_noi) - 1, 2):
            titlu = linii_noi[i]
            url = linii_noi[i + 1]
            if url.startswith("http") and url not in linkuri_vazute and este_activ(url):
                linkuri_vazute.add(url)
                linii_salvate.append(f'#EXTINF:-1 group-title="Filme & Seriale 2026",{titlu}')
                linii_salvate.append(url)

    # 2. Pastreaza filmele/serialele existente din doar_filme_seriale.m3u
    if os.path.exists(FISIER_LISTA):
        with open(FISIER_LISTA, "r", encoding="utf-8", errors="ignore") as f:
            linii = [l.strip() for l in f.readlines() if l.strip()]
        for i in range(len(linii) - 1):
            if linii[i].startswith("#EXTINF"):
                info = linii[i]
                url = linii[i + 1]
                if url.startswith("http") and url not in linkuri_vazute:
                    linkuri_vazute.add(url)
                    linii_salvate.append(info)
                    linii_salvate.append(url)

    with open(FISIER_LISTA, "w", encoding="utf-8") as out:
        out.write("\n".join(linii_salvate))

if __name__ == "__main__":
    actualizeaza_zilnic()
