# -*- coding: utf-8 -*-
"""
Tableau_de_bord.py - Point d'entrée historique et redirection vers Accueil_&_Cadre_Opérationnel.py
"""

import os
import sys

app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

target_script = os.path.join(app_dir, "Accueil_&_Cadre_Opérationnel.py")
with open(target_script, "r", encoding="utf-8") as f:
    code = compile(f.read(), target_script, "exec")
    exec(code, globals())
