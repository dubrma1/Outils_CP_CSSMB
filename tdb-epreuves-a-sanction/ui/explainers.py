# -*- coding: utf-8 -*-
"""
ui/explainers.py - Composants pédagogiques d'explication des concepts statistiques (LAD P3 & P8).
Permet de décharger la vue principale du jargon statistique complexe (d de Cohen, Gini, OLS, Wilson)
en le plaçant dans des expanders standardisés et bienveillants.
"""

from typing import List, Optional
import streamlit as st


EXPLAINERS_REGISTRY = {
    "cohen_d": {
        "title": "Comprendre cet indicateur : Taille d'effet (d de Cohen)",
        "content": r"""
        * **Qu'est-ce que c'est ?** Le $d$ de Cohen mesure l'écart entre la moyenne accordée par l'école ($NEB$) et la moyenne ministérielle ($NMC$), ramené à l'échelle de l'écart-type.
        * **Seuils d'interprétation :**
          * $|d| < 0.2$ : Écart négligeable (évaluation école parfaitement alignée sur l'épreuve).
          * $|d| \ge 0.5$ : Écart modéré.
          * $|d| \ge 0.8$ : Écart important justifiant un échange docimologique.
        * **Orientation :** Un $d > +0.8$ signale une notation école nettement plus indulgente que l'épreuve. Un $d < -0.8$ signale une sévérité locale ou des conditions particulières lors de l'épreuve.
        * **Prudence :** Ce diagnostic est un indicateur de calibrage collectif, en aucun cas un blâme individuel.
        """
    },
    "moderation_rq": {
        "title": "Comprendre cet indicateur : Facteurs de modération R et Q",
        "content": r"""
        * **Facteur R (Étalement des notes) :** Rapport entre la dispersion des notes de l'épreuve et celle de l'école ($R = \sigma_{min} / \sigma_{école}$). Un $R < 1$ indique que l'école a des notes plus étalées que l'épreuve, tandis qu'un $R > 1$ indique que l'épreuve a davantage discriminé les élèves.
        * **Facteur Q (Niveau moyen relatif) :** Décalage de la moyenne après modération.
        * **Points de bascule (NEB pour NEM = 60) :** Note minimale requise en classe pour obtenir la note de passage (60%) après application de la modération ministérielle.
        """
    },
    "ecrasement": {
        "title": "Comprendre cet indicateur : Notes écrasées par le Ministère",
        "content": r"""
        * **Règle de sanction ministérielle :** Si la note de l'élève à l'épreuve ministérielle convertie ($NMC$) est supérieure à sa note école modérée ($NEM$), la note ministérielle remplace intégralement la note école ($NMC \ge NEM$). La note école est alors « écrasée ».
        * **Interprétation :** Une forte proportion de notes écrasées indique que les élèves ont nettement surperformé à l'examen par rapport à l'évaluation annuelle de leur enseignant, ou que la note école a subi une forte pénalité statistique due à l'hétérogénéité du groupe.
        """
    },
    "quadrants": {
        "title": "Comprendre cet indicateur : Matrice d'arbitrage 4 Quadrants",
        "content": r"""
        * **Objectif :** Croiser le biais théorique de modération ($d$ de Cohen ou écart de moyenne) avec la sévérité pratique vécue par les élèves (% d'écrasement ou décote).
        * **Quadrant 1 (Alerte prioritaire) :** Fort biais d'évaluation et forte sévérité pratique -> Groupes à accompagner en priorité par les conseillers pédagogiques.
        * **Quadrant 2 :** Risque docimologique latent -> À surveiller pour les sessions futures.
        * **Quadrant 3 (Conforme) :** Évaluation équilibrée et modération stable.
        * **Quadrant 4 (Surperformance) :** Pratiques d'évaluation rigoureuses ayant préparé efficacement les élèves à l'épreuve.
        """
    },
    "gini_lorenz": {
        "title": "Comprendre cet indicateur : Indice de Gini et Courbe de Lorenz (Laboratoire)",
        "content": r"""
        * **Indice de Gini ($0.0$ à $1.0$) :** Mesure la dispersion et la concentration des notes au sein d'une école ou d'une discipline. Un Gini proche de $0$ indique une égalité parfaite (notes identiques).
        * **Interprétation prudente :** L'égalité n'est pas synonyme d'excellence pédagogique (un groupe où tous les élèves obtiennent 50% a un Gini nul, mais un fort taux d'échec). Un Gini élevé traduit une forte polarisation (élèves très forts côtoyant des élèves en grande difficulté).
        * **Usage :** Indicateur d'hétérogénéité pour adapter les ressources et les stratégies de différenciation pédagogique.
        """
    },
    "compression": {
        "title": "Comprendre cet indicateur : Compression des notes (Anomalie de variance)",
        "content": r"""
        * **En quoi est-ce une anomalie docimologique ?** Lorsque le ratio de dispersion est inférieur à 0.6 ($R = \sigma_{école} / \sigma_{min} < 0.6$), les notes attribuées par l'école sont anormalement resserrées autour de la moyenne.
        * **Conséquences pour les élèves :**
          * **Plafond artificiel :** Les élèves très performants se voient attribuer des notes moyennes (ex: 75% au lieu de 90%), ce qui bride leur dossier scolaire.
          * **Illusion de réussite :** Les élèves en difficulté reçoivent des notes plus élevées que leur maîtrise réelle, masquant des lacunes conceptuelles.
          * **Pénalité en modération :** Lors de l'épreuve unique, le Ministère applique un étalement statistique qui peut créer une forte instabilité des résultats finaux.
        """
    },
    "regression": {
        "title": "Comprendre cet indicateur : Régression OLS et Outliers Résiduels",
        "content": r"""
        * **Modèle linéaire :** Modélise la trajectoire attendue à l'épreuve du Ministère ($\widehat{NMC}$) à partir de la note école brute ($NEB$).
        * **Résidu ($e = NMC - \widehat{NMC}$) :** Écart par rapport à la tendance moyenne du réseau scolaire.
        * **Surperformance ($e > +k\sigma$) :** Groupes dont les résultats à l'épreuve dépassent très largement les prédictions. **Attention :** Une surperformance n'est pas toujours saine car une notation scolaire anormalement sévère au cours de l'année engendre un stress de performance inutile et de l'anxiété scolaire chez les élèves.
        * **Indulgence critique ($e < -k\sigma$) :** Groupes où la note école a créé une illusion de maîtrise infirmée par l'épreuve ministérielle.
        """
    }
}


def render_explainer(indicator_key: str, expanded: bool = False) -> None:
    """Rend un expander d'explication pédagogique pour un indicateur donné."""
    data = EXPLAINERS_REGISTRY.get(indicator_key)
    if not data:
        return
    with st.expander(data["title"], expanded=expanded):
        st.markdown(data["content"])


def render_about_data(
    source_name: str,
    date_chargement: Optional[str] = None,
    limits: Optional[List[str]] = None
) -> None:
    """
    Rend le bloc standardisé « À propos de ces données » (LAD P8 : Transparence et éthique).
    """
    date_txt = f" • Date d'extraction : {date_chargement}" if date_chargement else ""
    limits_html = ""
    if limits:
        items = "".join([f"<li>{item}</li>" for item in limits])
        limits_html = f"<div style='margin-top:6px;'><strong>Limites docimologiques :</strong><ul style='margin-left:20px; padding-left:0;'>{items}</ul></div>"

    with st.expander("À propos de ces données, conformité et limites d'usage", expanded=False):
        st.markdown(f"""
        * **Source des données :** {source_name}{date_txt}
        * **Conformité Loi 25 (Québec) :** Le traitement des données est opéré à 100 % dans la mémoire vive de votre navigateur via WebAssembly (Pyodide). Aucune donnée ne quitte votre appareil.
        * **Règle des petites cellules :** Les effectifs ou groupes de moins de 5 élèves sont systématiquement agrégés ou masqués pour protéger l'anonymat des apprenants.
        * **Éthique et posture d'accompagnement :** Les indicateurs présentés sont des outils d'analyse réflexive d'équipe. Ils visent à soutenir l'amélioration continue des pratiques d'enseignement et d'évaluation, non à porter un jugement de valeur individuel.
        """)
        if limits_html:
            st.markdown(limits_html, unsafe_allow_html=True)

