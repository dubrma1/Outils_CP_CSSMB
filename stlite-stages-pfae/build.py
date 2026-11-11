"""
build.py
Assemble et génère l'application autonome index.html (Stlite / Pyodide / WebAssembly)
à partir des modules sources locaux :
  - app/app.py
  - app/data_manager.py
  - data/Listes_profs_élèves_FMS-FPT_26-27.csv (version anonymisée)
  - data/repertoire_metiers_semi_specialises_meq.csv (référentiel officiel MEQ)
"""

import json
import base64
import os

def build():
    # Lecture des sources Python
    with open("app/app.py", "r", encoding="utf-8") as f:
        app_py_code = f.read()

    with open("app/data_manager.py", "r", encoding="utf-8") as f:
        dm_py_code = f.read()

    # Lecture des fichiers CSV
    with open("data/Listes_profs_élèves_FMS-FPT_26-27.csv", "rb") as f:
        master_csv_bytes = f.read()
    master_csv_b64 = base64.b64encode(master_csv_bytes).decode("ascii")

    with open("data/repertoire_metiers_semi_specialises_meq.csv", "rb") as f:
        rms_csv_bytes = f.read()
    rms_csv_b64 = base64.b64encode(rms_csv_bytes).decode("ascii")

    # Lecture du template index.html (ou index.html.orig.bak)
    template_file = "index.html.orig.bak" if os.path.exists("index.html.orig.bak") else "index.html"
    with open(template_file, "r", encoding="utf-8") as f:
        html = f.read()

    mc_start = html.find("const mountConfig =")
    html_head = html[:mc_start]

    # Personnalisation du titre et du splash screen
    html_head = html_head.replace(
        "<title>TdB Stages PFAE 2026-2027 | CSSMB</title>",
        "<title>TdB Stages PFAE 2026-2027 | Version Anonymisée CSSMB</title>"
    )
    html_head = html_head.replace(
        "🎓 Plateforme PFAE — Suivi des Stages",
        "🎓 Plateforme PFAE — Suivi des Stages (Version Anonymisée)"
    )
    html_head = html_head.replace(
        "<span>Données chiffrées en mémoire</span>",
        "<span>Données anonymisées (Loi 25)</span>"
    )

    next_section = html.find("function fixFormAndAccessibilityIssues", mc_start)
    html_tail = html[next_section:]

    app_py_json = json.dumps(app_py_code)
    dm_py_json = json.dumps(dm_py_code)

    mount_config_js = f"""const mountConfig = {{
      entrypoint: "app/app.py",
      requirements: ["streamlit", "pandas", "openpyxl"],
      files: {{
        "app/app.py": {app_py_json},
        "app.py": {app_py_json},
        "app/data_manager.py": {dm_py_json},
        "data_manager.py": {dm_py_json},
        "data/Listes_profs_élèves_FMS-FPT_26-27.csv": base64ToUint8Array("{master_csv_b64}"),
        "app/data/Listes_profs_élèves_FMS-FPT_26-27.csv": base64ToUint8Array("{master_csv_b64}"),
        "data/repertoire_metiers_semi_specialises_meq.csv": base64ToUint8Array("{rms_csv_b64}"),
        "app/data/repertoire_metiers_semi_specialises_meq.csv": base64ToUint8Array("{rms_csv_b64}")
      }}
    }};

    // =========================================================================
    // PERSISTANCE LOCALE SUR ORDINATEUR PORTABLE (LOCALSTORAGE & MEMFS)
    // =========================================================================
    const STORAGE_KEY = "pfae_stages_saved_csv";
    const LAST_SAVE_KEY = "pfae_stages_last_save";

    window.pfaeSaveToLaptopStorage = function(csvText) {{
      try {{
        if (csvText && csvText.length > 50) {{
          localStorage.setItem(STORAGE_KEY, csvText);
          localStorage.setItem(LAST_SAVE_KEY, new Date().toLocaleString());
          console.log("[PFAE] Données enregistrées dans le stockage local du portable.");
          return true;
        }}
      }} catch(e) {{
        console.warn("[PFAE] Échec d'enregistrement localStorage:", e);
      }}
      return false;
    }};

    window.pfaeLoadFromLaptopStorage = function() {{
      return localStorage.getItem(STORAGE_KEY);
    }};

    window.pfaeClearLaptopStorage = function() {{
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(LAST_SAVE_KEY);
      console.log("[PFAE] Stockage local réinitialisé.");
    }};

    window.pfaeGetLastSaveDate = function() {{
      return localStorage.getItem(LAST_SAVE_KEY) || "";
    }};

    // Restauration automatique des données sauvegardées sur ce portable au démarrage
    try {{
      const existingSavedCsv = localStorage.getItem(STORAGE_KEY);
      if (existingSavedCsv && existingSavedCsv.trim().length > 100) {{
        console.log("[PFAE] Restauration automatique des données sauvegardées sur ce portable...");
        mountConfig.files["data/Listes_profs_élèves_FMS-FPT_26-27.csv"] = existingSavedCsv;
        mountConfig.files["app/data/Listes_profs_élèves_FMS-FPT_26-27.csv"] = existingSavedCsv;
      }}
    }} catch(e) {{
      console.warn("[PFAE] Erreur lors de la lecture du localStorage:", e);
    }}

    """

    new_html = html_head + mount_config_js + html_tail
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"Compilation réussie ! index.html généré ({len(new_html)} octets).")

if __name__ == "__main__":
    build()
