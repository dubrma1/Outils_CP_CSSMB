"""Scraper des dictées de la Fondation Paul Gérin-Lajoie (niveaux 1 à 6).

Extrait chaque dictée via les pages select/1..6 et les PDF générés
(generatePDF/<id>), puis produit un répertoire complet au format CSV.
"""

import csv
import io
import re
import time
from typing import Dict, List, Tuple

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

BASE_URL = "https://dictee.fondationpgl.ca/audio/dictee"
OUTPUT_CSV = "dictees_pgl_1a6.csv"

CYCLE_MAP = {
    1: "Cycle 1",
    2: "Cycle 1",
    3: "Cycle 2",
    4: "Cycle 2",
    5: "Cycle 3",
    6: "Cycle 3",
}

NIVEAU_FALLBACK = {
    1: "Première année",
    2: "Deuxième année",
    3: "Troisième année",
    4: "Quatrième année",
    5: "Cinquième année",
    6: "Sixième année",
}


def get_dictee_links(session: requests.Session, level: int) -> List[Tuple[str, str, str]]:
    """Retourne la liste des (id, titre, url) pour un niveau donné (1 à 6)."""
    url = f"{BASE_URL}/select/{level}"
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    seen = set()
    items = []
    for a in soup.find_all("a", href=re.compile(r"/audio/dictee/single/\d+")):
        href = a["href"]
        m = re.search(r"/single/(\d+)", href)
        if not m:
            continue
        dictee_id = m.group(1)
        if dictee_id in seen:
            continue
        seen.add(dictee_id)
        title = " ".join(a.get_text().split())
        full_url = href if href.startswith("http") else f"https://dictee.fondationpgl.ca{href}"
        items.append((dictee_id, title, full_url))
    return items


def parse_pdf_bytes(pdf_bytes: bytes) -> Dict[str, str]:
    """Extrait niveau, titre, texte et commentaire depuis le PDF PGL."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    raw_pages = [page.extract_text() or "" for page in reader.pages]
    raw_text = "\n".join(raw_pages).replace("\xa0", " ")

    # Retirer le pied de page standard de la Fondation PGL
    lines = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("La Dictée P.G.L."):
            continue
        if stripped.startswith("http://fondationpgl.ca") or stripped.startswith("https://fondationpgl.ca"):
            continue
        if "© 2013 La Fondation Paul Gérin-Lajoie" in stripped or "Tous droits réservés" in stripped:
            continue
        lines.append(stripped)

    cleaned = "\n".join(lines)

    def extract_field(pattern: str, text: str) -> str:
        m = re.search(pattern, text, flags=re.DOTALL)
        return " ".join(m.group(1).split()) if m else ""

    niveau = extract_field(r"NIVEAU\s*:\s*(.*?)(?=\nTITRE\s*:|$)", cleaned)
    titre = extract_field(r"TITRE\s*:\s*(.*?)(?=\nTEXTE\s*:|$)", cleaned)
    texte = extract_field(r"TEXTE\s*:\s*(.*?)(?=\nCOMMENTAIRE\s*:|$)", cleaned)
    commentaire = extract_field(r"COMMENTAIRE\s*:\s*(.*)$", cleaned)

    return {
        "niveau": niveau,
        "titre": titre,
        "texte": texte,
        "commentaire": commentaire,
    }


def count_sentences(text: str) -> int:
    """Compte approximativement le nombre de phrases dans un texte."""
    if not text:
        return 0
    parts = [p.strip() for p in re.split(r"[.!?]+", text) if p.strip()]
    return len(parts)


def count_words(text: str) -> int:
    """Compte le nombre de mots dans un texte."""
    if not text:
        return 0
    return len(re.findall(r"\b[\w’'-]+\b", text, flags=re.UNICODE))


def build_tags(level: int, niveau: str, titre: str, commentaire: str) -> str:
    """Construit une chaîne de tags structurés pour la dictée."""
    tags = [
        f"niveau:{level}",
        f"annee:{niveau}",
        f"cycle:{CYCLE_MAP.get(level, '')}",
        f"titre:{titre}",
        "source:Fondation PGL",
    ]
    if commentaire:
        tags.append(f"commentaire:{commentaire}")
    return " | ".join(tags)


def main() -> None:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; CartographiePrimaireScraper/1.0)"
    })

    rows: List[Dict[str, str]] = []
    for level in range(1, 7):
        links = get_dictee_links(session, level)
        print(f"Niveau {level} : {len(links)} dictées trouvées")
        for dictee_id, link_title, single_url in links:
            pdf_url = f"{BASE_URL}/generatePDF/{dictee_id}"
            resp = session.get(pdf_url, timeout=20)
            resp.raise_for_status()
            parsed = parse_pdf_bytes(resp.content)

            niveau = parsed["niveau"] or NIVEAU_FALLBACK[level]
            titre = parsed["titre"] or link_title
            texte = parsed["texte"]
            commentaire = parsed["commentaire"]
            nb_mots = count_words(texte)
            nb_phrases = count_sentences(texte)
            tags = build_tags(level, niveau, titre, commentaire)

            rows.append({
                "id": dictee_id,
                "niveau_num": str(level),
                "niveau": niveau,
                "cycle": CYCLE_MAP[level],
                "titre": titre,
                "texte": texte,
                "commentaire": commentaire,
                "nb_mots": str(nb_mots),
                "nb_phrases": str(nb_phrases),
                "tags": tags,
                "url_dictee": single_url,
                "url_pdf": pdf_url,
            })
            time.sleep(0.1)

    fieldnames = [
        "id",
        "niveau_num",
        "niveau",
        "cycle",
        "titre",
        "texte",
        "commentaire",
        "nb_mots",
        "nb_phrases",
        "tags",
        "url_dictee",
        "url_pdf",
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Terminé : {len(rows)} dictées enregistrées dans {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
