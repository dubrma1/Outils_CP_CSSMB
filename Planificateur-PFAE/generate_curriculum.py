# -*- coding: utf-8 -*-
"""
Script de génération de curriculum_data.json pour le Planificateur PFAE (FPT 1, 2, 3 et FMS).
Basé sur l'analyse exhaustive des documents officiels et des planifications réelles
(Dalbé-Viau, Rose-Virginie-Pelletier, Lucien-Pagé, Baie-Saint-François).
"""

import json

def get_full_curriculum():
    return {
        "parcours": {
            "FPT1": {
                "titre": "Formation préparatoire au travail - An 1 (FPT 1)",
                "description": "Première année du cycle FPT (élèves de 15 ans et plus). Accent mis sur la consolidation des apprentissages de base en français et mathématiques, la sensibilisation au monde du travail en classe-atelier (SMT), le développement de l'autonomie personnelle et sociale (APS) et la connaissance de soi (PMT).",
                "matieres": {
                    "francais": {
                        "nom": "Français, langue d'enseignement",
                        "code": "FRA-FPT1",
                        "enseignant_ref": "Marie-Pier Lavoie et Véronique Paradis (Dalbé-Viau) / Bernard Gravel (RVP)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Lire et apprécier des textes variés", "desc": "Compréhension d'éléments significatifs de textes fonctionnels, d'instructions et de récits simples. Stratégies de lecture."},
                            {"code": "C2", "titre": "Écrire des textes variés", "desc": "Production de phrases complètes, formulaires, fiches et courts textes informatifs. Orthographe d'usage et accords de base."},
                            {"code": "C3", "titre": "Communiquer oralement selon des modalités variées", "desc": "Prise de parole individuelle et en groupe, écoute active, clarté du propos et ajustement au contexte."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Situations d'apprentissage, lecture de consignes, phrases déclaratives et négatives. Étape 2 (20%): Formulaires, fiches d'instructions, annonces publicitaires, communication orale. Étape 3 (60%): Projet bilan, lecture fonctionnelle complexe, présentation orale formelle.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt1_fr_1",
                                    "titre": "Prise de parole et communication en classe",
                                    "description": "Prendre la parole individuellement et s'ajuster au besoin. Respecter le temps de parole, écouter les autres et poser des questions claires.",
                                    "competences": ["C3"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Société - APS / Habiletés sociales",
                                    "sae_projet": "Cercle de parole et présentation de soi",
                                    "ressources": "Grilles d'écoute et de prise de parole"
                                },
                                {
                                    "id": "fpt1_fr_2",
                                    "titre": "Lecture fonctionnelle : Formulaires et fiches d'accueil",
                                    "description": "Lire et repérer les rubriques d'un formulaire simple (nom, coordonnées, date, case à cocher). Comprendre les pictogrammes.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail / Formalités",
                                    "sae_projet": "Remplir ma fiche d'inscription et profil élève",
                                    "ressources": "Formulaires scolaires et modèles administratifs"
                                },
                                {
                                    "id": "fpt1_fr_3",
                                    "titre": "Classes de mots et accords dans le groupe nominal",
                                    "description": "Distinguer le nom, le déterminant, l'adjectif et le pronom. Accords en genre et en nombre. Homophones on/ont et a/à/as.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Consolidation linguistique",
                                    "sae_projet": "Ateliers de grammaire ciblée et mini-dictées",
                                    "ressources": "Cahier maison de grammaire FPT"
                                },
                                {
                                    "id": "fpt1_fr_4",
                                    "titre": "SAE L'hygiène et la santé corporelle",
                                    "description": "Lecture d'un document informatif sur l'hygiène au quotidien et au travail. Questions de compréhension et rédaction de conseils.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 3,
                                    "axe_thematique": "Santé - APS / État de santé",
                                    "sae_projet": "SAE Hygiène corporelle, vestimentaire et buccale",
                                    "ressources": "Brochures de santé publique, capsules vidéo"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt1_fr_5",
                                    "titre": "Fiches d'entretien, de travail et fiches d'instructions",
                                    "description": "Lire et cocher les étapes effectuées pour mieux se situer. Rédiger des phrases complètes pour signaler un bris ou une demande d'aide.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail / Atelier",
                                    "sae_projet": "Manuel d'instructions et bon de travail d'atelier",
                                    "ressources": "Guides techniques simples et fiches d'atelier"
                                },
                                {
                                    "id": "fpt1_fr_6",
                                    "titre": "Lecture et réalisation d'une recette santé",
                                    "description": "Lire une recette, ressortir les ingrédients et le matériel. Travailler le lexique de cuisine et rédiger une appréciation.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Santé - APS / Alimentation",
                                    "sae_projet": "Projet Recette santé et lexique culinaire",
                                    "ressources": "Recettes simples, Guide alimentaire canadien"
                                },
                                {
                                    "id": "fpt1_fr_7",
                                    "titre": "Publicités, dépliants et jugement critique",
                                    "description": "Visionnement et lecture de publicités. Identifier à qui s'adresse le message. Rédiger une affiche publicitaire pour un magasin scolaire.",
                                    "competences": ["C1", "C2", "C3"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Consommation - APS / Facteurs d'influence",
                                    "sae_projet": "Élaboration d'une affiche publicitaire de classe",
                                    "ressources": "Circulaires, publicités imprimées et web"
                                },
                                {
                                    "id": "fpt1_fr_8",
                                    "titre": "Conjugaison au présent et verbes du 2e groupe",
                                    "description": "Conjugaison des verbes du 1er et 2e groupe. Types et formes de phrases (affirmative, négative, interrogative). Homophones ses/ces/c'est.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Consolidation linguistique",
                                    "sae_projet": "Fiches de révision et exercices autocorrectifs",
                                    "ressources": "Jeux de cartes de conjugaison"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt1_fr_9",
                                    "titre": "SAE Mon portrait personnel et professionnel",
                                    "description": "Conception d'une affiche présentant ses forces, qualités et intérêts. Présentation orale dynamique devant la classe avec support visuel.",
                                    "competences": ["C2", "C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Identité personnelle et professionnelle - PMT",
                                    "sae_projet": "Affiche Mon Portrait et exposé oral C3",
                                    "ressources": "Photos, fiches de qualités et valeurs"
                                },
                                {
                                    "id": "fpt1_fr_10",
                                    "titre": "Consignes de sécurité et protocoles en entreprise",
                                    "description": "Lire et comprendre des règlements d'entreprise et des protocoles de sécurité. Synthétiser l'information avec des phrases claires.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail / Sécurité",
                                    "sae_projet": "Protocole SST et charte de classe-atelier",
                                    "ressources": "Règlements scolaires, fiches CNESST simplifiées"
                                },
                                {
                                    "id": "fpt1_fr_11",
                                    "titre": "Articles de presse jeunesse et club de lecture",
                                    "description": "Lire des articles d'actualité adaptés, des petites annonces et courts récits. Donner son appréciation critique et échanger en groupe.",
                                    "competences": ["C1", "C3"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Santé - APS / Loisirs culturels",
                                    "sae_projet": "Club de lecture et fiches d'appréciation",
                                    "ressources": "Magazines jeunesse, livres audio, romans faciles"
                                },
                                {
                                    "id": "fpt1_fr_12",
                                    "titre": "Bilan d'écriture et stratégies d'auto-correction",
                                    "description": "Réviser un texte avec un code de correction (PONS). Utiliser un traitement de texte et un dictionnaire pour peaufiner ses écrits.",
                                    "competences": ["C2"],
                                    "duree_semaines": 3,
                                    "axe_thematique": "Consolidation linguistique",
                                    "sae_projet": "Portfolio de textes révisés",
                                    "ressources": "Grille de correction PONS, correcteur informatique"
                                }
                            ]
                        }
                    },
                    "mathematiques": {
                        "nom": "Mathématiques FPT1",
                        "code": "MAT-FPT1",
                        "enseignant_ref": "Catherine Patry-Sauvé (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Résoudre une situation-problème", "desc": "Comprendre la situation concrète, mobiliser les concepts mathématiques pertinents et communiquer une solution claire."},
                            {"code": "C2", "titre": "Déployer un raisonnement mathématique", "desc": "Appliquer les opérations arithmétiques, proportionnalité, géométrie et statistiques en contexte de vie courante et d'atelier."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Sens du nombre, 4 opérations, lecture de l'heure et horaires. Étape 2 (20%): Proportions, SAE Le Marchand, géométrie plane, rabais et taxes. Étape 3 (60%): Situation-problème bilan C1, budget personnel, mesures et statistiques.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt1_mat_1",
                                    "titre": "Sens du nombre et opérations de base sur les entiers",
                                    "description": "Valeur de position, droite numérique, comparaison des nombres. Addition et soustraction en contexte de gestion d'objets et d'argent.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Autonomie financière / Bases",
                                    "sae_projet": "Inventaire d'objets de classe et calculs de stocks",
                                    "ressources": "Matériel de manipulation, droite numérique"
                                },
                                {
                                    "id": "fpt1_mat_2",
                                    "titre": "Lecture de l'heure, durées et horaires de travail",
                                    "description": "Horloges analogiques et numériques, formats 12h et 24h. Conversion de secondes, minutes et heures. Calcul de durées et de retards.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail / Ponctualité",
                                    "sae_projet": "Feuille de temps d'atelier et horaire hebdomadaire",
                                    "ressources": "Horloges modèles, feuilles d'heures réelles"
                                },
                                {
                                    "id": "fpt1_mat_3",
                                    "titre": "Propriétés des opérations et calcul mental d'appoint",
                                    "description": "Commutativité, associativité et distributivité. Stratégies d'arrondissement et utilisation fonctionnelle de la calculatrice.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Bases mathématiques",
                                    "sae_projet": "Défi calculatrice et estimation rapide de prix",
                                    "ressources": "Calculatrice, fiches de calcul mental"
                                },
                                {
                                    "id": "fpt1_mat_4",
                                    "titre": "SAE Sommeil : Calcul de l'horaire 10-3-2-1-0",
                                    "description": "Calculer les paliers horaires à rebours à partir de l'heure du coucher pour planifier son sommeil réparateur.",
                                    "competences": ["C1"],
                                    "duree_semaines": 3,
                                    "axe_thematique": "Santé - APS / Sommeil",
                                    "sae_projet": "Grille horaire personnalisée du sommeil",
                                    "ressources": "Protocole de sommeil 10-3-2-1-0"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt1_mat_5",
                                    "titre": "Sens de la proportionnalité : Ratios et taux unitaires",
                                    "description": "Rapport et taux, taux unitaire (prix au 100g ou à l'unité). Stratégies ministérielles : retour à l'unité, facteur de changement.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Consommation / Rapport qualité-prix",
                                    "sae_projet": "Comparaison de circulaires et meilleur achat",
                                    "ressources": "Circulaires d'épicerie, capsules vidéo"
                                },
                                {
                                    "id": "fpt1_mat_6",
                                    "titre": "SAE Le Marchand : Manipulation d'argent et caisse",
                                    "description": "Calcul du montant total d'achats, calcul des rabais simples, encaissement et rendu de la monnaie exacte.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail - PMT / Tâches de travail",
                                    "sae_projet": "Simulation de boutique scolaire (Le Marchand)",
                                    "ressources": "Tiroir-caisse, faux billets, étiquettes de prix"
                                },
                                {
                                    "id": "fpt1_mat_7",
                                    "titre": "Figures géométriques planes et aménagement d'espace",
                                    "description": "Polygones réguliers et irréguliers. Reconnaissance des formes, estimation d'espace et plan d'agencement de pièces.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Logement / Aménagement",
                                    "sae_projet": "Plan à l'échelle de la classe-atelier",
                                    "ressources": "Papier quadrillé, règles, gabarits"
                                },
                                {
                                    "id": "fpt1_mat_8",
                                    "titre": "Mathématiques culinaires : Proportions en cuisine",
                                    "description": "Ajustement des quantités d'ingrédients selon le nombre de convives. Conversion des mesures (tasses, cuillères, grammes, millilitres).",
                                    "competences": ["C1"],
                                    "duree_semaines": 3,
                                    "axe_thematique": "Santé - APS / Alimentation",
                                    "sae_projet": "Calcul des portions pour la collation de groupe",
                                    "ressources": "Tasses et cuillères à mesurer, balances"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt1_mat_9",
                                    "titre": "Nombres décimaux et gestion financière du quotidien",
                                    "description": "Opérations sur les nombres décimaux en contexte monétaire. Vérification d'un reçu de caisse et calcul d'un total avec pourboire.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Autonomie financière - APS",
                                    "sae_projet": "Analyse de factures réelles et reçus",
                                    "ressources": "Factures et reçus anonymisés"
                                },
                                {
                                    "id": "fpt1_mat_10",
                                    "titre": "Mesures de longueur et utilisation du ruban à mesurer",
                                    "description": "Système métrique (mm, cm, m) et système impérial (pouces, pieds). Mesures de planches et périmètre d'objets techniques.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail / Atelier",
                                    "sae_projet": "Mesurage et débitage de bois en atelier",
                                    "ressources": "Rubans à mesurer métrique/impérial, règles en acier"
                                },
                                {
                                    "id": "fpt1_mat_11",
                                    "titre": "Statistique : Tableaux de données et diagrammes",
                                    "description": "Lire et tracer des diagrammes à bandes simples à partir d'un sondage de classe. Dégager la valeur la plus fréquente.",
                                    "competences": ["C2"],
                                    "duree_semaines": 3,
                                    "axe_thematique": "Société / Médias",
                                    "sae_projet": "Sondage sur les habitudes de transport des élèves",
                                    "ressources": "Feuilles quadrillées, grilles de sondage"
                                },
                                {
                                    "id": "fpt1_mat_12",
                                    "titre": "SAE Sortie culturelle : Budget et itinéraire",
                                    "description": "Calcul du coût total d'une sortie : billets d'entrée, titres de transport en commun, collations et temps total de déplacement.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Transport - APS / Déplacement",
                                    "sae_projet": "Planification budgétaire de la sortie de fin d'année",
                                    "ressources": "Tarifs de transport public, grilles de budget"
                                }
                            ]
                        }
                    },
                    "pmt": {
                        "nom": "Préparation au marché du travail 1 (PMT)",
                        "code": "PMT-FPT1",
                        "enseignant_ref": "Véronique Paradis (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Cerner son profil personnel et professionnel", "desc": "Examiner son histoire personnelle, ses intérêts, aptitudes, valeurs et son potentiel d'employabilité."},
                            {"code": "C2", "titre": "Se donner une représentation du marché du travail", "desc": "Explorer les milieux de travail, les métiers accessibles, les exigences d'embauche et les réalités du marché."},
                            {"code": "C3", "titre": "Réaliser une démarche d'insertion socioprofessionnelle", "desc": "S'engager dans des actions concrètes : CV, préparation d'entrevues, visites d'entreprises."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Connaissance de soi C1 (tests d'intérêts, ligne du temps). Étape 2 (20%): Exploration de métiers C2 (dossier métier de rêve, salaire). Étape 3 (60%): Bilan profil, pré-CV, simulation d'entrevue C3.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt1_pmt_1",
                                    "titre": "Regard sur son histoire personnelle et scolaire",
                                    "description": "Faire le bilan de son parcours, identifier ses réussites, passions, défis surmontés et ses personnes ressources.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Identité personnelle et professionnelle - PMT",
                                    "sae_projet": "Ligne du temps personnelle illustrée",
                                    "ressources": "Cahier de cheminement personnel"
                                },
                                {
                                    "id": "fpt1_pmt_2",
                                    "titre": "Inventaires d'intérêts : Typologie RIASEC",
                                    "description": "Découverte des profils professionnels (Réaliste, Investigateur, Artistique, Social, Entreprenant, Conventionnel). Identifier ses 2 lettres dominantes.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Identité personnelle et professionnelle - PMT",
                                    "sae_projet": "Passation et analyse du questionnaire RIASEC adapté",
                                    "ressources": "Test RIASEC jeunesse / IVIP"
                                },
                                {
                                    "id": "fpt1_pmt_3",
                                    "titre": "Projet Mon portrait professionnel",
                                    "description": "Créer une affiche synthétisant ses qualités d'employabilité, ses compétences manuelles ou relationnelles et ses objectifs.",
                                    "competences": ["C1", "C3"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Identité personnelle et professionnelle - PMT",
                                    "sae_projet": "Affiche Mon Portrait et partage en cercle",
                                    "ressources": "Cartons, grilles de traits de personnalité"
                                },
                                {
                                    "id": "fpt1_pmt_4",
                                    "titre": "Savoir-être et attitudes au travail",
                                    "description": "Les comportements incontournables : ponctualité, politesse, fiabilité, respect des collègues et du superviseur, gestion du téléphone cellulaire.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail - PMT / Savoir-être",
                                    "sae_projet": "Mises en situation et jeu de rôle en milieu de travail",
                                    "ressources": "Scénarios d'attitudes professionnelles"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt1_pmt_5",
                                    "titre": "SAE Un métier de rêve : Exploration en profondeur",
                                    "description": "Recherche documentaire sur un métier visé : tâches concrètes, milieu physique, équipement, formation requise et débouchés.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail - PMT / Métiers",
                                    "sae_projet": "Dossier de recherche Un métier de rêve",
                                    "ressources": "Sites Repères, Découvre les métiers, vidéos Carrières"
                                },
                                {
                                    "id": "fpt1_pmt_6",
                                    "titre": "Salaire, pouvoir d'achat et coût de la vie",
                                    "description": "Calculer le salaire brut et net pour 35h/semaine au salaire minimum. Comparer avec le coût d'un logement, épicerie et transport.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail - PMT / Autonomie financière",
                                    "sae_projet": "Calcul de mon futur budget de travailleur autonome",
                                    "ressources": "Calculateurs de salaire québécois, petites annonces"
                                },
                                {
                                    "id": "fpt1_pmt_7",
                                    "titre": "Exploration des tâches professionnelles d'exécution",
                                    "description": "Analyser les tâches types en atelier et entreprise : manutention, nettoyage industriel, préparation de commandes, service au comptoir.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail - PMT / Tâches",
                                    "sae_projet": "Grille d'observation des tâches de travail de Lucien-Pagé",
                                    "ressources": "Grilles de tâches PFAE"
                                },
                                {
                                    "id": "fpt1_pmt_8",
                                    "titre": "Évolution technologique dans les métiers",
                                    "description": "Comprendre comment les outils numériques transforment les métiers semi-spécialisés (terminaux de commande, caisses tactiles, scans d'entrepôt).",
                                    "competences": ["C2"],
                                    "duree_semaines": 3,
                                    "axe_thematique": "Monde du travail - PMT / Évolution techno",
                                    "sae_projet": "Capsule d'observation sur les technologies au travail",
                                    "ressources": "Vidéos industrielles actuelles"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt1_pmt_9",
                                    "titre": "Élaboration de son premier curriculum vitae (CV)",
                                    "description": "Identifier ses expériences de bénévolat, d'aide familiale et d'ateliers scolaires. Structurer un CV clair et sans faute.",
                                    "competences": ["C1", "C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle - PMT",
                                    "sae_projet": "Rédaction assistée de mon premier CV FPT",
                                    "ressources": "Modèles de CV simplifiés, traitement de texte"
                                },
                                {
                                    "id": "fpt1_pmt_10",
                                    "titre": "Simulation d'entrevue d'embauche",
                                    "description": "Se préparer aux questions d'embauche fréquentes. Travailler le contact visuel, la poignée de main et la clarté des réponses.",
                                    "competences": ["C3"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Insertion professionnelle - PMT",
                                    "sae_projet": "Atelier pratique d'entrevues filmées avec débriefing",
                                    "ressources": "Grilles d'entrevue, questions types"
                                },
                                {
                                    "id": "fpt1_pmt_11",
                                    "titre": "Droits du travail et santé-sécurité (CNESST)",
                                    "description": "Connaître ses droits de base : salaire minimum, pauses, droit de refuser un travail dangereux et responsabilités SST.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail / SST",
                                    "sae_projet": "Atelier Jeunes au travail de la CNESST",
                                    "ressources": "Guides CNESST et Éducaloi"
                                },
                                {
                                    "id": "fpt1_pmt_12",
                                    "titre": "Bilan de fin d'année et préparation aux stages FPT2",
                                    "description": "Évaluer ses progrès en employabilité, cibler 3 domaines de stage d'intérêt pour l'année 2 et fixer ses objectifs personnels.",
                                    "competences": ["C1", "C3"],
                                    "duree_semaines": 3,
                                    "axe_thematique": "Identité personnelle et professionnelle - PMT",
                                    "sae_projet": "Bilan d'employabilité et fiche de vœux de stages FPT2",
                                    "ressources": "Dossier de transition vers les stages"
                                }
                            ]
                        }
                    },
                    "smt": {
                        "nom": "Sensibilisation au monde du travail (SMT)",
                        "code": "SMT-FPT1",
                        "enseignant_ref": "Catherine Patry-Sauvé (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Se représenter les exigences propres à différentes situations de travail", "desc": "Expérimenter une diversité de situations de travail en classe-atelier, identifier matières premières, procédés et équipements, et fournir une prestation de qualité."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Respect des règles de sécurité en atelier et assiduité. Étape 2 (20%): Qualité du travail manuel et esprit d'équipe. Étape 3 (60%): Autonomie sur les postes de travail, respect des cadences et bilan d'atelier.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt1_smt_1",
                                    "titre": "Accueil en classe-atelier et protocoles de sécurité",
                                    "description": "Découverte des aires de travail, règles de circulation, port systématique des lunettes et gants de protection. Signalement des risques.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / SST atelier",
                                    "sae_projet": "Obtention du Brevet de sécurité de l'atelier",
                                    "ressources": "Affiches SST, équipements EPI"
                                },
                                {
                                    "id": "fpt1_smt_2",
                                    "titre": "Identification des matières premières et outillage à main",
                                    "description": "Reconnaître les matériaux (bois, métal, carton rigide, visserie) et manipuler sécuritairement scies, tournevis, pinces et marteaux.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Matières et outillage",
                                    "sae_projet": "Coffret d'outillage personnel et inventaire imagé",
                                    "ressources": "Outils à main, échantillons de matériaux"
                                },
                                {
                                    "id": "fpt1_smt_3",
                                    "titre": "Attitudes de travail en équipe et entretien du poste",
                                    "description": "Collaborer avec un partenaire, respecter les consignes verbales de fabrication, nettoyer et ranger son poste avant la fin du cours.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Société / Collaboration",
                                    "sae_projet": "Routine de fermeture et de propreté d'atelier",
                                    "ressources": "Grille d'inspection du poste de travail"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt1_smt_4",
                                    "titre": "Séquences de fabrication et respect des gabarits",
                                    "description": "Exécuter des étapes ordonnées : mesure, traçage au crayon, découpe guidée, ponçage, pré-perçage et assemblage vissé.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Procédés de fabrication",
                                    "sae_projet": "Fabrication d'un nichoir ou porte-crayons en bois",
                                    "ressources": "Gabarits de coupe, feuilles d'instructions illustrées"
                                },
                                {
                                    "id": "fpt1_smt_5",
                                    "titre": "Adaptation aux imprévus et contrôle des erreurs",
                                    "description": "Apprendre à identifier une pièce défectueuse, ne pas forcer sur un outil coincé et trouver une solution de rattrapage avec l'enseignant.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Résolution de problèmes",
                                    "sae_projet": "Atelier Diagnostic et réparation de pièces",
                                    "ressources": "Exemples d'erreurs d'usinage et solutions"
                                },
                                {
                                    "id": "fpt1_smt_6",
                                    "titre": "Travail à la chaîne et régularité d'exécution",
                                    "description": "Expérimenter la répartition des tâches sur une chaîne de production. Comprendre l'impact de son rythme sur les collègues.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Productivité",
                                    "sae_projet": "Production en série de blocs-notes ou sous-verres",
                                    "ressources": "Postes de travail disposés en ligne"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt1_smt_7",
                                    "titre": "Grand projet de classe-atelier intégrateur",
                                    "description": "Projet d'envergure mobilisant toutes les compétences d'atelier (ex. bacs à fleurs pour la cour d'école, rénovation de mobilier).",
                                    "competences": ["C1"],
                                    "duree_semaines": 6,
                                    "axe_thematique": "Monde du travail / Projet intégré",
                                    "sae_projet": "Projet de fabrication collective de fin d'année",
                                    "ressources": "Matériaux de projet, machines-outils supervisées"
                                },
                                {
                                    "id": "fpt1_smt_8",
                                    "titre": "Contrôle qualité et tolérances dimensionnelles",
                                    "description": "Utiliser des piges et équerres pour vérifier la précision des pièces finies. Remplir une fiche d'inspection qualité.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail / Qualité",
                                    "sae_projet": "Poste d'agrément et d'emballage final",
                                    "ressources": "Équerres de précision, calibres"
                                },
                                {
                                    "id": "fpt1_smt_9",
                                    "titre": "Carnet d'habiletés d'atelier et transition vers le stage",
                                    "description": "Valider la liste des compétences acquises en atelier pour son dossier de présentation en stage d'entreprise FPT2.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Insertion professionnelle - PMT",
                                    "sae_projet": "Bilan d'attestation d'habiletés pratiques",
                                    "ressources": "Carnet d'habiletés pratiques FPT"
                                }
                            ]
                        }
                    },
                    "aps": {
                        "nom": "Autonomie et participation sociale (APS)",
                        "code": "APS-FPT1",
                        "enseignant_ref": "Catherine Patry-Sauvé (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Agir avec autonomie dans son milieu de vie", "desc": "Prendre en charge sa santé, son alimentation, ses déplacements et ses routines de vie."},
                            {"code": "C2", "titre": "Participer à la vie en société", "desc": "Établir des relations positives, communiquer respectueusement et s'engager dans son milieu."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Habitudes d'hygiène de vie et écoute en groupe. Étape 2 (20%): Nutrition, transport en commun et budget module 1. Étape 3 (60%): Projet d'autonomie personnelle et ressources communautaires.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt1_aps_1",
                                    "titre": "Hygiène personnelle et soin de son image",
                                    "description": "Routines d'hygiène corporelle, soins dentaires, propreté des vêtements et présentation soignée dans la vie scolaire et au travail.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Santé - APS / État de santé",
                                    "sae_projet": "Ma trousse d'hygiène et ma routine quotidienne",
                                    "ressources": "Fiches conseils de santé publique"
                                },
                                {
                                    "id": "fpt1_aps_2",
                                    "titre": "Habiletés sociales et relations interpersonnelles",
                                    "description": "La politesse, le respect des limites personnelles d'autrui, savoir dire non respectueusement et gérer la colère sans violence.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Société - APS / Habiletés sociales",
                                    "sae_projet": "Jeux de rôles : Communication assertive",
                                    "ressources": "Scénarios sociaux, fiches d'habiletés"
                                },
                                {
                                    "id": "fpt1_aps_3",
                                    "titre": "Besoins fondamentaux vs désirs superflus",
                                    "description": "Identifier la faim réelle, le besoin de sécurité et d'amitié, et les séparer des désirs d'achats impulsifs de gadgets ou vêtements de marque.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Consommation - APS / Besoins",
                                    "sae_projet": "La pyramide de mes besoins essentiels",
                                    "ressources": "Pyramide de Maslow simplifiée"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt1_aps_4",
                                    "titre": "Saine alimentation et décodage d'étiquettes",
                                    "description": "Composer une assiette équilibrée. Décoder le tableau de valeur nutritive (calories, sucres, sodium). Préparer des collations santé.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Santé - APS / Alimentation",
                                    "sae_projet": "Atelier nutrition et collations d'énergie",
                                    "ressources": "Guide alimentaire canadien, emballages réels"
                                },
                                {
                                    "id": "fpt1_aps_5",
                                    "titre": "Autonomie financière : Ateliers MFMC (Module 1)",
                                    "description": "Programme 'Mes finances, mes choix' (Desjardins) : Module 1 sur le budget, distinguer revenus réguliers et dépenses incompressibles.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Autonomie financière - APS / Budget",
                                    "sae_projet": "Atelier MFMC Module 1 - Mon premier budget",
                                    "ressources": "Cahier de formation MFMC Desjardins"
                                },
                                {
                                    "id": "fpt1_aps_6",
                                    "titre": "Déplacements et transport en commun",
                                    "description": "Repérer les trajets de bus et métro sur plan ou application (Chrono/Google Maps). Gérer sa carte OPUS et voyager en sécurité.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Transport - APS / Déplacement",
                                    "sae_projet": "Planification de trajets autonomes dans ma ville",
                                    "ressources": "Cartes de transport, applications mobiles"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt1_aps_7",
                                    "titre": "Ressources communautaires et services du quartier",
                                    "description": "Situer et savoir solliciter les ressources utiles : CLSC, maison des jeunes, bibliothèque, carrefour jeunesse, banque alimentaire.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Société - APS / Services et ressources",
                                    "sae_projet": "Répertoire pratique des services de mon quartier",
                                    "ressources": "Bottin des organismes communautaires"
                                },
                                {
                                    "id": "fpt1_aps_8",
                                    "titre": "Loisirs sains et gestion équilibrée du temps d'écran",
                                    "description": "Identifier des loisirs stimulants, activités de plein air, s'inscrire à une maison des jeunes, limiter la dépendance aux téléphones/écrans.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Santé - APS / Loisirs",
                                    "sae_projet": "Plan de loisirs équilibré pour la semaine",
                                    "ressources": "Guides de loisirs municipaux"
                                },
                                {
                                    "id": "fpt1_aps_9",
                                    "titre": "Sécurité dans la communauté et gestes d'urgence",
                                    "description": "Savoir composer le 911 en donnant des indications claires. Prévenir les risques de rue et savoir réagir en situation d'imprévu.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Transport et sécurité - APS",
                                    "sae_projet": "Mises en situation d'appel 911 et plan d'urgence",
                                    "ressources": "Fiches Croix-Rouge / Police communautaire"
                                }
                            ]
                        }
                    },
                    "sciences": {
                        "nom": "Expérimentations technologiques et scientifiques (EST)",
                        "code": "EST-FPT1",
                        "enseignant_ref": "Catherine Patry-Sauvé (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Chercher des réponses à des problèmes scientifiques/technologiques", "desc": "Mettre en œuvre une démarche expérimentale guidée, manipuler le matériel de façon sécuritaire et observer méthodiquement."},
                            {"code": "C2", "titre": "Mettre à profit ses connaissances scientifiques et technologiques", "desc": "Relier les concepts de science à la vie quotidienne, à la santé, aux matériaux et au fonctionnement des objets techniques."},
                            {"code": "C3", "titre": "Communiquer à l'aide des langages de la science et de la technologie", "desc": "Utiliser le vocabulaire scientifique approprié, les schémas, les pictogrammes et les unités de mesure conventionnelles."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Manipulation sécuritaire et compréhension du SIMDUT. Étape 2 (20%): Transformations de la matière, digestion et écologie. Étape 3 (60%): Projet technologique bilan et compte-rendu d'expérimentation.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt1_est_1",
                                    "titre": "Univers matériel : Pictogrammes SIMDUT et sécurité",
                                    "description": "Identifier les symboles de danger sur les produits d'entretien ménager et industriel. Précautions de stockage et ventilation.",
                                    "competences": ["C2", "C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Santé et sécurité / Environnement",
                                    "sae_projet": "Audit des produits chimiques de la classe",
                                    "ressources": "Fiches SIMDUT 2015, contenants sécurisés"
                                },
                                {
                                    "id": "fpt1_est_2",
                                    "titre": "Matériaux recyclables et tri sélectif",
                                    "description": "Distinguer plastiques (codes 1 à 7), verre, métaux et cartons. Comprendre le cycle du recyclage et le principe des 3R (Réduire, Réutiliser, Recycler).",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Environnement et consommation",
                                    "sae_projet": "Brigade verte : Amélioration du tri à l'école",
                                    "ressources": "Guides Recyc-Québec, bacs de tri"
                                },
                                {
                                    "id": "fpt1_est_3",
                                    "titre": "L'échelle de pH : Acides et bases courants",
                                    "description": "Utiliser du papier tournesol pour mesurer le pH de produits domestiques (vinaigre, savon, eau, jus). Notion de neutralisation.",
                                    "competences": ["C1", "C3"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Matière et procédés",
                                    "sae_projet": "Laboratoire d'expérimentation du pH",
                                    "ressources": "Papier pH, indicateurs colorés naturels (chou rouge)"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt1_est_4",
                                    "titre": "Transformations physiques vs transformations chimiques",
                                    "description": "Observer des changements d'état (fusion de la glace, évaporation) et des réactions chimiques (oxydation du fer, vinaigre + bicarbonate).",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Matière et procédés",
                                    "sae_projet": "Laboratoire d'indices de réaction chimique",
                                    "ressources": "Matériel de chimie douce"
                                },
                                {
                                    "id": "fpt1_est_5",
                                    "titre": "Univers vivant : Digestion des aliments et nutriments",
                                    "description": "Comprendre les étapes de la digestion (mécanique et chimique). Rôle des protéines, glucides, lipides et vitamines pour le corps.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Santé - APS / Alimentation",
                                    "sae_projet": "Maquette du système digestif et fiches nutriments",
                                    "ressources": "Modèles anatomiques, fiches de nutrition"
                                },
                                {
                                    "id": "fpt1_est_6",
                                    "titre": "Compostage et décomposition de la matière organique",
                                    "description": "Le rôle des décomposeurs et vers de terre. Équilibre carbone/azote (matières brunes/vertes). Réaliser un lombricomposteur.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Environnement / Écologie",
                                    "sae_projet": "Lombricomposteur de classe actif",
                                    "ressources": "Bac de compost, terreau, restes de légumes"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt1_est_7",
                                    "titre": "Machines simples et démultiplication de la force",
                                    "description": "Étudier le levier, la poulie, la roue et le plan incliné. Expérimenter l'avantage mécanique pour déplacer des charges lourdes.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Atelier",
                                    "sae_projet": "Défi technologique : Système de levage sécuritaire",
                                    "ressources": "Kits de machines simples, pesons"
                                },
                                {
                                    "id": "fpt1_est_8",
                                    "titre": "Électricité de base et circuits simples",
                                    "description": "Circuits en boucle fermée (pile, interrupteur, ampoule/moteur). Notion de conducteur et isolant. Précautions avec le courant du secteur.",
                                    "competences": ["C1", "C3"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Technologie et habitat",
                                    "sae_projet": "Fabrication d'une veilleuse portative",
                                    "ressources": "Fils avec pinces crocodiles, DELs, piles 9V"
                                },
                                {
                                    "id": "fpt1_est_9",
                                    "titre": "Projet de conception technologique synthèse",
                                    "description": "Concevoir et fabriquer un objet technique répondant à un cahier des charges simple. Tester, ajuster et présenter son fonctionnement.",
                                    "competences": ["C1", "C2", "C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Innovation",
                                    "sae_projet": "Projet scientifique et technologique annuel",
                                    "ressources": "Matériaux d'atelier, pistolet à colle, outils"
                                }
                            ]
                        }
                    },
                    "univers_social": {
                        "nom": "Géographie, histoire et éducation à la citoyenneté",
                        "code": "USO-FPT1",
                        "enseignant_ref": "Marie-Pier Lavoie et Catherine Patry-Sauvé (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Construire son appartenance au territoire", "desc": "Situer les espaces de vie, comprendre l'organisation du quartier et les réalités régionales du Québec."},
                            {"code": "C2", "titre": "S'insérer dans la société québécoise et démocratique", "desc": "Comprendre les règles civiques, les institutions publiques, le droit de vote et les valeurs citoyennes."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Cartographie du quartier et règles civiques. Étape 2 (20%): Démocratie, droit de vote et diversité culturelle. Étape 3 (60%): Projet citoyen et aménagement du territoire québécois.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt1_us_1",
                                    "titre": "Repérage spatial : Mon quartier et ses repères majeurs",
                                    "description": "Lire un plan de ville avec légende et échelle. Situer son école, les artères principales, parcs, hôpitaux et mairies d'arrondissement.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Territoire et communauté",
                                    "sae_projet": "Plan grand format annoté de mon quartier",
                                    "ressources": "Plans municipaux, Google Maps satellite"
                                },
                                {
                                    "id": "fpt1_us_2",
                                    "titre": "Règles civiques et lois fondamentales",
                                    "description": "Comprendre pourquoi la société a besoin de règles. Différence entre règlements d'école, règlements municipaux et Code civil/criminel.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Société / Citoyenneté",
                                    "sae_projet": "Charte des droits et responsabilités du citoyen",
                                    "ressources": "Fiches Éducaloi jeunesse"
                                },
                                {
                                    "id": "fpt1_us_3",
                                    "titre": "Histoire des moyens de transport au Québec",
                                    "description": "L'évolution des modes de déplacement : canot autochtone, train à vapeur, tramway, métro de Montréal, réseau routier actuel.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Transport / Histoire locale",
                                    "sae_projet": "Frise historique des transports québécois",
                                    "ressources": "Archives photos BAnQ"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt1_us_4",
                                    "titre": "La démocratie municipale et provinciale",
                                    "description": "Comprendre le rôle du maire, des députés à l'Assemblée nationale et du gouvernement. Pourquoi et comment vote-t-on ?",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Société / Démocratie",
                                    "sae_projet": "Simulation d'élection scolaire avec isoloir et urne",
                                    "ressources": "Matériel officiel Élections Québec"
                                },
                                {
                                    "id": "fpt1_us_5",
                                    "titre": "Premiers Peuples et mosaïque culturelle",
                                    "description": "Découvrir les 11 nations autochtones du Québec et la contribution des communautés culturelles à la vitalité québécoise.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Culture et vivre-ensemble",
                                    "sae_projet": "Exposition sur la diversité culturelle et autochtone",
                                    "ressources": "Documents ONF, site In-Terre-Actif"
                                },
                                {
                                    "id": "fpt1_us_6",
                                    "titre": "Droits humains et égalité hommes-femmes",
                                    "description": "Charte québécoise des droits et libertés. L'égalité des genres, la lutte contre l'intimidation et les discriminations.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Droits et justice",
                                    "sae_projet": "Capsule de sensibilisation aux droits de la personne",
                                    "ressources": "CliquezJustice.ca, Commission des droits"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt1_us_7",
                                    "titre": "Les grandes régions du Québec et leurs ressources",
                                    "description": "Explorer les régions ressources : forêt boréale, hydroélectricité dans le Nord, agriculture en Montérégie, industries urbaines.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Territoire et économie",
                                    "sae_projet": "Guide touristique et géographique d'une région québécoise",
                                    "ressources": "Cartes régionales du Québec"
                                },
                                {
                                    "id": "fpt1_us_8",
                                    "titre": "Défis environnementaux et aménagement urbain",
                                    "description": "Les parcs de conservation, le traitement de l'eau, les pistes cyclables et la lutte contre les changements climatiques.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Environnement / Territoire",
                                    "sae_projet": "Proposition d'amélioration écologique pour notre école",
                                    "ressources": "Plans d'aménagement urbain durable"
                                },
                                {
                                    "id": "fpt1_us_9",
                                    "titre": "Engagement citoyen et bénévolat",
                                    "description": "Comprendre comment s'impliquer dans un organisme communautaire pour améliorer la vie collective.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Société / Engagement",
                                    "sae_projet": "Journée d'action bénévole d'équipe",
                                    "ressources": "Centres d'action bénévole du Québec"
                                }
                            ]
                        }
                    },
                    "anglais": {
                        "nom": "Anglais, langue seconde",
                        "code": "ANG-FPT1",
                        "enseignant_ref": "Programme FPT - Enseignement fonctionnel",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Interagir oralement en anglais", "desc": "Participer à des échanges simples, saluer, demander des informations et exprimer ses besoins."},
                            {"code": "C2", "titre": "Comprendre des textes lus et entendus", "desc": "Comprendre des panneaux, menus, affiches et consignes simples du quotidien et du travail."},
                            {"code": "C3", "titre": "Écrire des textes fonctionnels courts", "desc": "Remplir une fiche de renseignements, écrire un message court ou une note courtoise."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Échanges oraux simples et salutations. Étape 2 (20%): Menus, commandes et panneaux de sécurité. Étape 3 (60%): Bilan oral fonctionnel et court courriel/formulaire.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt1_ang_1",
                                    "titre": "Basic Oral Communication: Greetings & Introductions",
                                    "description": "Role-play: Greetings, introducing oneself (name, age, city), asking polite questions (How are you?).",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Habiletés sociales / Langues",
                                    "sae_projet": "Speed-meeting in English: Getting to know classmates",
                                    "ressources": "Cartes de conversation, dialogues audio"
                                },
                                {
                                    "id": "fpt1_ang_2",
                                    "titre": "Everyday Objects & Classroom Vocabulary",
                                    "description": "Identifying tools, stationery, furniture and common items. Asking for help: Can you help me, please?",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Quotidien",
                                    "sae_projet": "Classroom visual dictionary",
                                    "ressources": "Flashcards illustrées"
                                },
                                {
                                    "id": "fpt1_ang_3",
                                    "titre": "Safety Signs & Public Notices",
                                    "description": "Recognizing essential signs: Danger, Exit, Push/Pull, Employees only, Slippery floor, No smoking.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Sécurité / Quotidien",
                                    "sae_projet": "Safety Sign Treasure Hunt",
                                    "ressources": "Photos réelles de panneaux publics"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt1_ang_4",
                                    "titre": "Functional Language: Ordering Food and Drinks",
                                    "description": "Reading a fast-food or cafe menu, placing an order, asking for the bill and understanding change.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Consommation / Alimentation",
                                    "sae_projet": "Restaurant role-play with menus",
                                    "ressources": "Menus bilingues, accessoires de restaurant"
                                },
                                {
                                    "id": "fpt1_ang_5",
                                    "titre": "Personal Information Cards & Contact Forms",
                                    "description": "Filling out basic English forms: First name, Last name, Date of birth, Phone number, Postal code.",
                                    "competences": ["C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Identité / Formalités",
                                    "sae_projet": "Membership Card Application in English",
                                    "ressources": "Modèles de formulaires en anglais"
                                },
                                {
                                    "id": "fpt1_ang_6",
                                    "titre": "English in Technology & Video Games",
                                    "description": "Understanding common interface terms: Settings, Save, Loading, Log in, Start, Next, Cancel.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Médias / Loisirs",
                                    "sae_projet": "Tech words glossary for gaming and social media",
                                    "ressources": "Captures d'écrans d'applications"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt1_ang_7",
                                    "titre": "Talking About Hobbies, Sports and Music",
                                    "description": "Expressing likes and dislikes: I like playing hockey, I love listening to music. Short presentation of a hobby.",
                                    "competences": ["C1", "C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Santé - APS / Loisirs",
                                    "sae_projet": "My Favorite Hobby poster and speech",
                                    "ressources": "Vidéos de musique avec sous-titres"
                                },
                                {
                                    "id": "fpt1_ang_8",
                                    "titre": "Asking for and Giving Directions",
                                    "description": "Where is the bus stop? Turn left, turn right, go straight. Reading a simple transit schedule or city map.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Transport / Déplacement",
                                    "sae_projet": "Finding your way in a shopping mall",
                                    "ressources": "Cartes de centres commerciaux et réseaux de bus"
                                },
                                {
                                    "id": "fpt1_ang_9",
                                    "titre": "Writing Short Courteous Messages & Notes",
                                    "description": "Writing a short thank-you card or a brief message to report being sick or running late.",
                                    "competences": ["C3"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Communication professionnelle",
                                    "sae_projet": "Writing a courteous postcard or short message",
                                    "ressources": "Modèles de cartes de vœux et courriels courts"
                                }
                            ]
                        }
                    },
                    "eps": {
                        "nom": "Éducation physique et à la santé",
                        "code": "EPS-FPT1",
                        "enseignant_ref": "M. Azurdia (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Agir dans divers contextes d'activités physiques", "desc": "Développer ses capacités motrices, son endurance et sa posture de sécurité."},
                            {"code": "C2", "titre": "Interagir dans divers contextes d'activités physiques", "desc": "Coopérer dans les jeux collectifs et sports d'équipe avec esprit sportif."},
                            {"code": "C3", "titre": "Adopter un mode de vie sain et actif", "desc": "Planifier une pratique régulière d'activité physique et comprendre l'impact sur le bien-être."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Échauffement, condition physique de base et sécurité. Étape 2 (20%): Sports collectifs et plein air d'hiver. Étape 3 (60%): Endurance globale, autonomie sportive et posture ergonomique.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt1_eps_1",
                                    "titre": "Connaissance du corps et routine d'échauffement",
                                    "description": "Le système musculo-squelettique, les étirements dynamiques, prise du pouls cardiaque au repos et après l'effort.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Santé - APS / État de santé",
                                    "sae_projet": "Fiche personnalisée d'échauffement sécuritaire",
                                    "ressources": "Gymnase, fiches anatomiques"
                                },
                                {
                                    "id": "fpt1_eps_2",
                                    "titre": "Endurance aérobie et gestion du rythme cardiaque",
                                    "description": "Course et marche rapide par intervalles. Comprendre sa zone d'effort aérobie et persévérer dans l'effort continu.",
                                    "competences": ["C1", "C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Santé / Mode de vie actif",
                                    "sae_projet": "Défi kilomètres cumulés de classe",
                                    "ressources": "Chronomètres, piste extérieure"
                                },
                                {
                                    "id": "fpt1_eps_3",
                                    "titre": "Jeux coopératifs et esprit d'équipe",
                                    "description": "Activités sans élimination demandant l'aide mutuelle de tous les élèves (parachute, transport d'objets en duo).",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Société / Esprit d'équipe",
                                    "sae_projet": "Jeux coopératifs d'inclusion",
                                    "ressources": "Matériel varié de gymnase"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt1_eps_4",
                                    "titre": "Sports collectifs : Kin-Ball et Volleyball adapté",
                                    "description": "Règles simples, communication entre coéquipiers, passes, positionnement défensif et fair-play.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Société / Coopération",
                                    "sae_projet": "Tournoi amical de Kin-Ball en équipes mixtes",
                                    "ressources": "Ballon géant Kin-Ball, sifflets"
                                },
                                {
                                    "id": "fpt1_eps_5",
                                    "titre": "Activités de plein air hivernales et habillage multicouche",
                                    "description": "Marche rapide hivernale, patinage ou raquette. Comprendre l'évacuation de la transpiration par temps froid.",
                                    "competences": ["C1", "C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Plein air et santé",
                                    "sae_projet": "Sortie plein air active en parc municipal",
                                    "ressources": "Parc municipal, raquettes de neige"
                                },
                                {
                                    "id": "fpt1_eps_6",
                                    "titre": "Hydratation et alimentation du sportif",
                                    "description": "Les effets néfastes des boissons énergisantes sur le cœur et le sommeil. L'eau comme boisson d'hydratation idéale.",
                                    "competences": ["C3"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Santé - APS / Prévention",
                                    "sae_projet": "Journal d'hydratation sportive de 2 semaines",
                                    "ressources": "Gourdes réutilisables, fiches comparatives"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt1_eps_7",
                                    "titre": "Sports de raquette : Badminton et Pickleball",
                                    "description": "Coordination oeil-main, déplacement latéral, service réglementaire et échanges soutenus en simple et en double.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Coordination et agilité",
                                    "sae_projet": "Tournoi amical de badminton en ronde",
                                    "ressources": "Filets, raquettes, volants"
                                },
                                {
                                    "id": "fpt1_eps_8",
                                    "titre": "Ergonomie, posture et prévention des maux de dos",
                                    "description": "Renforcement de la sangle abdominale et lombaire. Techniques pour soulever une charge sans blesser la colonne.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Ergonomie",
                                    "sae_projet": "Circuit d'exercices posturaux pour le travailleur",
                                    "ressources": "Tapis, bandes élastiques, caisses de charge"
                                },
                                {
                                    "id": "fpt1_eps_9",
                                    "titre": "Mon plan personnel de condition physique estival",
                                    "description": "Choisir 3 activités physiques accessibles à pratiquer durant l'été (vélo, marche, natation, soccer).",
                                    "competences": ["C3"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Mode de vie sain et actif",
                                    "sae_projet": "Calendrier forme pour la saison estivale",
                                    "ressources": "Guide d'activités physiques locales"
                                }
                            ]
                        }
                    }
                }
            },
            "FPT2": {
                "titre": "Formation préparatoire au travail - An 2 (FPT 2)",
                "description": "Deuxième année du cycle FPT. Introduction des stages en entreprise (1 à 2 jours par semaine), consolidation des compétences appliquées en mathématiques (fractions, pourcentages, mesures) et français professionnel, autonomie financière accrue (budget, logement).",
                "matieres": {
                    "francais": {
                        "nom": "Français, langue d'enseignement",
                        "code": "FRA-FPT2",
                        "enseignant_ref": "Marie-Pier Lavoie et Véronique Paradis (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Lire des textes fonctionnels et professionnels", "desc": "Comprendre manuels d'entretien, courriels de superviseurs, fiches de sécurité et consignes de stage."},
                            {"code": "C2", "titre": "Écrire des textes professionnels et administratifs", "desc": "Rédiger des comptes-rendus de stage, courriels de courtoisie, CV actualisé et formulaires."},
                            {"code": "C3", "titre": "Communiquer oralement en milieu de travail", "desc": "Interagir avec un patron, poser des questions techniques et échanger avec les clients et collègues."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Textes de préparation de stage et révision orthographique. Étape 2 (20%): Correspondance professionnelle (courriels, formulaires) et communication orale. Étape 3 (60%): Rapport bilan de stage, CV professionnel et lecture appliquée.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt2_fr_1",
                                    "titre": "Communication professionnelle : Accueillir et renseigner",
                                    "description": "Vocabulaire courtois au téléphone et face-à-face en entreprise. Poser des questions ouvertes pour clarifier une commande ou consigne.",
                                    "competences": ["C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle / Stage",
                                    "sae_projet": "Jeux de rôle : Accueil client et appel au superviseur",
                                    "ressources": "Scénarios téléphoniques en entreprise"
                                },
                                {
                                    "id": "fpt2_fr_2",
                                    "titre": "Lecture de fiches de poste et contrats d'embauche/stage",
                                    "description": "Repérer l'horaire, les tâches obligatoires, les personnes responsables et les règles de confidentialité.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Cadre légal",
                                    "sae_projet": "Décryptage de ma convention de stage",
                                    "ressources": "Conventions de stage réelles anonymisées"
                                },
                                {
                                    "id": "fpt2_fr_3",
                                    "titre": "Homophones grammaticaux fréquents et accords participes",
                                    "description": "Homophones ou/où, la/l'a/là, ces/ses/c'est. Accord du participe passé avec l'auxiliaire être et avoir simple.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Consolidation linguistique",
                                    "sae_projet": "Fiches d'exercices ciblées pour écrits de travail",
                                    "ressources": "Cahier d'exercices adaptés FPT2"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt2_fr_4",
                                    "titre": "Rdaction de courriels professionnels",
                                    "description": "Objet précis, formules de salutation et politesse, structure claire du message (justifier un retard, demander une information).",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Communication professionnelle",
                                    "sae_projet": "Envoi simulé d'un courriel à son tuteur de stage",
                                    "ressources": "Modèles de courriels d'entreprise"
                                },
                                {
                                    "id": "fpt2_fr_5",
                                    "titre": "Lecture de baux de logement et formulaires administratifs",
                                    "description": "Comprendre les sections d'un bail de logement du Tribunal administratif du logement (loyer, responsabilités, règlements).",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Logement et autonomie",
                                    "sae_projet": "Analyse d'un bail type du TAL",
                                    "ressources": "Formulaire officiel du TAL"
                                },
                                {
                                    "id": "fpt2_fr_6",
                                    "titre": "Journal de bord et carnet de réflexion de stage",
                                    "description": "Rédiger des notes hebdomadaires sur ses réussites en stage, les défis rencontrés et les habiletés déployées.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Insertion professionnelle / Stage",
                                    "sae_projet": "Carnet de bord hebdomadaire de stage",
                                    "ressources": "Cahier de stage FPT"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt2_fr_7",
                                    "titre": "Actualisation du Curriculum Vitae et lettre d'intérêt",
                                    "description": "Ajouter ses compétences de stage au CV. Rédiger une courte lettre de motivation pour postuler à un emploi d'été.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle - PMT",
                                    "sae_projet": "Dossier de candidature complet (CV actualisé + lettre)",
                                    "ressources": "Modèles de CV enrichis avec expériences de stage"
                                },
                                {
                                    "id": "fpt2_fr_8",
                                    "titre": "Rapport et exposé oral de bilan de stage",
                                    "description": "Présentation orale structurée devant la classe avec photos ou objets de son entreprise de stage.",
                                    "competences": ["C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle / Stage",
                                    "sae_projet": "Exposé bilan Mon expérience en entreprise",
                                    "ressources": "Support visuel (PowerPoint / Affiche), grille d'évaluation"
                                },
                                {
                                    "id": "fpt2_fr_9",
                                    "titre": "Lecture critique d'articles sur les droits du consommateur",
                                    "description": "Comprendre les garanties légales, politiques d'échange et recours en cas de litige avec un commerçant.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Consommation - APS / Droits",
                                    "sae_projet": "Fiches pratiques de l'Office de la protection du consommateur",
                                    "ressources": "Guides de l'OPC, cas réels"
                                }
                            ]
                        }
                    },
                    "mathematiques": {
                        "nom": "Mathématiques FPT2",
                        "code": "MAT-FPT2",
                        "enseignant_ref": "Marie-Pier Lavoie (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Résoudre une situation-problème", "desc": "Résoudre des problèmes complexes du quotidien : salaires, pourcentages, fractions appliquées et budget autonome."},
                            {"code": "C2", "titre": "Déployer un raisonnement mathématique", "desc": "Maîtriser les opérations sur les fractions, nombres décimaux, pourcentages, conversion d'unités et probabilités."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Mesures temporelles, décalages, estimation de prix et mesures. Étape 2 (20%): Fractions, droite numérique, cadrans et opérations. Étape 3 (60%): Pourcentages, rabais/taxes, diagrammes, situation-problème synthèse.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt2_mat_1",
                                    "titre": "Mesures temporelles avancées et décalages horaires",
                                    "description": "Opérations complexes liées au temps, calcul d'heures supplémentaires, horaires de nuit et décalages horaires pour les transports.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Temps",
                                    "sae_projet": "Gestion des feuilles de temps et calcul des heures de stage",
                                    "ressources": "Feuilles de temps réelles, calendriers annuels"
                                },
                                {
                                    "id": "fpt2_mat_2",
                                    "titre": "Estimation rapide de mesures et de prix",
                                    "description": "Développer des trucs d'estimation mentale pour évaluer des coûts d'épicerie et des dimensions sans calculatrice.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Consommation / Budget",
                                    "sae_projet": "Jeu du juste prix et estimation de panier d'épicerie",
                                    "ressources": "Paniers de produits réels, circulaires"
                                },
                                {
                                    "id": "fpt2_mat_3",
                                    "titre": "SAE Gestion des frais de transport au travail",
                                    "description": "Calculer et comparer les coûts entre transport en commun, covoiturage, vélo ou possession d'une voiture (essence, assurance, entretien).",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Transport - APS / Coûts",
                                    "sae_projet": "Comparatif budgétaire des options de transport",
                                    "ressources": "Grilles CAA Québec, tarifs transport collectif"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt2_mat_4",
                                    "titre": "Fractions appliquées : Relation fraction et décimal",
                                    "description": "Comprendre les fractions usuelles (1/2, 1/4, 3/4, 1/3, 1/8). Passage de la fraction au nombre décimal et pourcentage.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Mathématiques appliquées",
                                    "sae_projet": "Droites numériques et graduation d'outils de mesure",
                                    "ressources": "Rubans à mesurer impériaux (1/16, 1/8, 1/4 pouce)"
                                },
                                {
                                    "id": "fpt2_mat_5",
                                    "titre": "Opérations sur les fractions et réduction",
                                    "description": "Addition et soustraction de fractions de même dénominateur. Réduction à sa plus simple expression en contexte de travail.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Atelier",
                                    "sae_projet": "Calcul de longueurs de coupes avec fractions de pouce",
                                    "ressources": "Fiches d'atelier bois/métal"
                                },
                                {
                                    "id": "fpt2_mat_6",
                                    "titre": "Lecture de cadrans, jauges et instruments de précision",
                                    "description": "Lire des thermomètres, manomètres, balances industrielles et cadrans analogiques sur des équipements techniques.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail / Équipement",
                                    "sae_projet": "Relevé de cadrans industriels et fiches de contrôle",
                                    "ressources": "Manomètres et jauges d'apprentissage"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt2_mat_7",
                                    "titre": "Pourcentages : Rabais, taxes (TPS/TVQ) et pourboires",
                                    "description": "Calculer 15% (taxes québécoises ou pourboire), 10%, 20%, 50% de rabais. Calculer le coût final d'un achat important.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Consommation et finances",
                                    "sae_projet": "Simulateur d'achats avec taxes combinées",
                                    "ressources": "Factures et simulateurs de taxes"
                                },
                                {
                                    "id": "fpt2_mat_8",
                                    "titre": "Analyse de données statistiques et graphiques",
                                    "description": "Interpréter des diagrammes circulaires (répartition des dépenses d'un ménage) et des histogrammes d'évolution.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Société / Données",
                                    "sae_projet": "Graphique de répartition de mon budget mensuel",
                                    "ressources": "Rapports de cartes de crédit simplifiés"
                                },
                                {
                                    "id": "fpt2_mat_9",
                                    "titre": "Situation-problème bilan C1 : Budget de vie en appartement",
                                    "description": "Équilibrer un budget mensuel complet pour un travailleur à temps partiel : loyer, électricité, nourriture, internet, loisirs.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Autonomie financière - APS / Logement",
                                    "sae_projet": "Situation-problème de synthèse FPT2",
                                    "ressources": "Dossier d'évaluation synthèse ministériel"
                                }
                            ]
                        }
                    },
                    "stage": {
                        "nom": "Insertion professionnelle en stage (IP)",
                        "code": "STG-FPT2",
                        "enseignant_ref": "Marie-Pier Lavoie et Véronique Paradis (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "S'approprier les compétences et comportements en milieu de travail", "desc": "S'adapter à la culture d'entreprise, respecter les consignes de santé-sécurité et accomplir les tâches confiées avec rigueur."},
                            {"code": "C2", "titre": "Évaluer son niveau de développement professionnel", "desc": "Analyser son rendement avec son tuteur et son enseignant, reconnaître ses forces et corriger ses faiblesses."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Intégration en stage, ponctualité, tenue et sécurité. Étape 2 (20%): Réalisation des tâches de stage et assiduité. Étape 3 (60%): Évaluation bilan du tuteur d'entreprise et carnet de compétences.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt2_stg_1",
                                    "titre": "Intégration en milieu de travail et accueil en entreprise",
                                    "description": "Premières journées de stage : visite des lieux, rencontre du tuteur et des collègues, repérage des vestiaires et pause-repas.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle / Stage",
                                    "sae_projet": "Passeport d'intégration en entreprise",
                                    "ressources": "Guide d'accueil en milieu de stage"
                                },
                                {
                                    "id": "fpt2_stg_2",
                                    "titre": "Respect des règles SST spécifiques au milieu de stage",
                                    "description": "Port des équipements spécifiques (bottes à cap d'acier, charlotte, tablier, lunettes). Signalement immédiat d'un incident.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / SST",
                                    "sae_projet": "Fiche de sécurité de mon poste de stage",
                                    "ressources": "Consignes de sécurité propres à l'entreprise"
                                },
                                {
                                    "id": "fpt2_stg_3",
                                    "titre": "Ponctualité rigoureuse et gestion des présences",
                                    "description": "Arriver 10 minutes avant le début du quart de travail. Aviser l'entreprise ET l'école en cas d'absence motivée ou imprévue.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Insertion professionnelle / Assiduité",
                                    "sae_projet": "Protocole de communication en cas d'absence",
                                    "ressources": "Feuille de présence officielle signée par le tuteur"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt2_stg_4",
                                    "titre": "Exécution conforme des tâches de base du métier",
                                    "description": "Réalisation méthodique des tâches assignées par le superviseur : rangement de marchandise, préparation de commandes, nettoyage.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle / Compétences",
                                    "sae_projet": "Fiche de tâches de travail validée par le tuteur",
                                    "ressources": "Grille d'évaluation des tâches FPT"
                                },
                                {
                                    "id": "fpt2_stg_5",
                                    "titre": "Communication avec les collègues et réaction aux commentaires",
                                    "description": "Recevoir les remarques constructives sans se fâcher, corriger son geste immédiatement et remercier pour le conseil.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Société / Habiletés professionnelles",
                                    "sae_projet": "Entretien de mi-stage avec l'enseignant et le tuteur",
                                    "ressources": "Grille d'évaluation mi-parcours"
                                },
                                {
                                    "id": "fpt2_stg_6",
                                    "titre": "Endurance physique et gestion de la fatigue au travail",
                                    "description": "S'adapter au travail debout prolongé ou aux mouvements répétés. Adopter une bonne hygiène de vie les veilles de stage.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Santé / Travail",
                                    "sae_projet": "Bilan d'énergie et plan de récupération",
                                    "ressources": "Conseils d'ergonomie et de repos"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt2_stg_7",
                                    "titre": "Autonomie dans le poste et prise d'initiative adaptée",
                                    "description": "Anticiper la prochaine tâche lorsque la précédente est terminée (nettoyer le poste, demander la suite au patron).",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle / Autonomie",
                                    "sae_projet": "Défi autonomie en milieu de travail",
                                    "ressources": "Observations de l'enseignant superviseur"
                                },
                                {
                                    "id": "fpt2_stg_8",
                                    "titre": "Évaluation sommative finale en entreprise",
                                    "description": "Rencontre tripartite (élève, enseignant, superviseur en entreprise) pour faire le bilan complet des compétences atteintes.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle / Bilan",
                                    "sae_projet": "Évaluation sommative du superviseur de stage",
                                    "ressources": "Formulaire ministériel d'évaluation de stage"
                                },
                                {
                                    "id": "fpt2_stg_9",
                                    "titre": "Bilan de stage et attestation de participation",
                                    "description": "Réception de l'attestation de stage, remerciement officiel à l'employeur et choix du type de stage pour FPT3.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Insertion professionnelle / TEVA",
                                    "sae_projet": "Lettre de remerciement au tuteur et bilan personnel",
                                    "ressources": "Lettre type de remerciement"
                                }
                            ]
                        }
                    },
                    "pmt": {
                        "nom": "Préparation au marché du travail 2 (PMT)",
                        "code": "PMT-FPT2",
                        "enseignant_ref": "Véronique Paradis (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Cerner son profil personnel et professionnel", "desc": "Analyser ses progrès en stage, ses forces professionnelles confirmées et ses champs d'intérêt affinés."},
                            {"code": "C2", "titre": "Se donner une représentation du marché du travail", "desc": "Comprendre les normes du travail (CNESST), les types de contrats, les syndicats et les passerelles de formation."},
                            {"code": "C3", "titre": "Réaliser une démarche d'insertion socioprofessionnelle", "desc": "Rechercher des offres d'emploi, simuler des entrevues de sélection et bâtir son dossier d'employabilité."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Auto-évaluation en stage et analyse des intérêts C1. Étape 2 (20%): Normes du travail et droits C2. Étape 3 (60%): Dossier de recherche d'emploi et simulations C3.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt2_pmt_1",
                                    "titre": "Profil professionnel enrichi par l'expérience de stage",
                                    "description": "Faire le lien entre ce qu'on aime faire à l'école et ce qu'on expérimente en vrai milieu de travail. Mettre à jour ses aptitudes.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Identité professionnelle - PMT",
                                    "sae_projet": "Mon bilan de compétences après 2 mois de stage",
                                    "ressources": "Grille d'auto-évaluation PMT2"
                                },
                                {
                                    "id": "fpt2_pmt_2",
                                    "titre": "Les secteurs d'activité économique au Québec",
                                    "description": "Comprendre les secteurs : primaire (nature), secondaire (manufacturier/construction), tertiaire (commerce et services).",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Économie",
                                    "sae_projet": "Panorama des secteurs économiques de ma région",
                                    "ressources": "Fiches Industrie Canada / Emploi-Québec"
                                },
                                {
                                    "id": "fpt2_pmt_3",
                                    "titre": "Relation avec l'autorité et communication hiérarchique",
                                    "description": "Comprendre le rôle du contremaître, gérant, propriétaire. Comment exprimer un besoin ou poser une question sans confrontation.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Société / Savoir-être",
                                    "sae_projet": "Mises en situation : Dialoguer avec son supérieur",
                                    "ressources": "Vidéos de situations au travail"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt2_pmt_4",
                                    "titre": "Normes du travail au Québec (CNESST)",
                                    "description": "Les règles de la Loi sur les normes du travail : salaire minimum, heures de travail, paiement des heures supplémentaires, congés fériés.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Droits",
                                    "sae_projet": "Guide pratique de mes droits de travailleur",
                                    "ressources": "Site CNESST et capsules Éducaloi"
                                },
                                {
                                    "id": "fpt2_pmt_5",
                                    "titre": "Recherche d'emploi : Réseautage et marché caché",
                                    "description": "Comment les gens trouvent du travail : bouche-à-oreille, réseau personnel, démarches directes en personne vs sites d'offres d'emploi.",
                                    "competences": ["C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle - PMT",
                                    "sae_projet": "Cartographie de mon réseau d'aide à l'emploi",
                                    "ressources": "Guide de recherche d'emploi pour jeunes"
                                },
                                {
                                    "id": "fpt2_pmt_6",
                                    "titre": "Fiche de paie et retenues à la source",
                                    "description": "Comprendre son talon de paie : salaire brut vs net, déductions (RRQ, RQAP, assurance-emploi, impôts fédéral/provincial).",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Autonomie financière / Salaires",
                                    "sae_projet": "Décryptage d'un talon de paie réel",
                                    "ressources": "Talons de paie modèles anonymisés"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt2_pmt_7",
                                    "titre": "Simulation d'entrevues d'embauche approfondies",
                                    "description": "Entrevues de sélection avec des questions sur des situations réelles de travail (Ex: Racontez une fois où vous avez résolu un problème).",
                                    "competences": ["C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle - PMT",
                                    "sae_projet": "Entrevue de recrutement simulée avec intervenant externe",
                                    "ressources": "Grilles d'entrevue comportementale"
                                },
                                {
                                    "id": "fpt2_pmt_8",
                                    "titre": "Santé mentale et gestion du stress en emploi",
                                    "description": "Reconnaître l'épuisement, la surcharge de travail, savoir demander de l'aide et équilibrer travail et vie personnelle.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Santé et bien-être / Travail",
                                    "sae_projet": "Trousse antistress pour le travailleur",
                                    "ressources": "Guides de santé mentale au travail"
                                },
                                {
                                    "id": "fpt2_pmt_9",
                                    "titre": "Planification de la transition vers FPT3 et TEVA",
                                    "description": "Initier la démarche TEVA (Transition école-vie active) : planifier le passage à 3 jours de stage par semaine pour l'an 3.",
                                    "competences": ["C1", "C3"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Insertion professionnelle / TEVA",
                                    "sae_projet": "Mon plan TEVA pour l'an 3 de FPT",
                                    "ressources": "Cahier de planification TEVA FPT_1_2_3"
                                }
                            ]
                        }
                    },
                    "aps": {
                        "nom": "Autonomie et participation sociale (APS)",
                        "code": "APS-FPT2",
                        "enseignant_ref": "Marie-Pier Lavoie (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Agir avec autonomie dans son milieu de vie", "desc": "Gérer son budget, organiser son logement, faire ses courses et cuisiner de manière autonome."},
                            {"code": "C2", "titre": "Participer à la vie en société", "desc": "Exercer ses droits de citoyen, prévenir les dépendances et entretenir des relations saines."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Alimentation autonome et gestion du stress. Étape 2 (20%): Prévention des dépendances, sexualité et budget avancé. Étape 3 (60%): Projet de vie autonome en appartement et droits du citoyen.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt2_aps_1",
                                    "titre": "Alimentation autonome : Planifier et cuisiner pour une semaine",
                                    "description": "Établir un menu de semaine, faire la liste d'épicerie en respectant un budget fixe, cuisiner des repas simples et sains.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Santé - APS / Alimentation",
                                    "sae_projet": "Mon panier d'épicerie hebdomadaire à 75$",
                                    "ressources": "Circulaires d'épicerie, recettes économiques"
                                },
                                {
                                    "id": "fpt2_aps_2",
                                    "titre": "Prévention : Alcool, drogues, vapotage et écrans",
                                    "description": "Comprendre les effets de la consommation sur la santé physique, le cerveau, le rendement au travail et le portefeuille.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Santé - APS / Prévention",
                                    "sae_projet": "Campagne de sensibilisation aux méfaits des substances",
                                    "ressources": "Vidéos de prévention, fiches Éduc'alcool"
                                },
                                {
                                    "id": "fpt2_aps_3",
                                    "titre": "Entretien ménager autonome et sécurité des produits",
                                    "description": "Techniques de lavage du linge (symboles d'étiquettes de lavage), ménage sécuritaire de la cuisine et de la salle de bain.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Vie quotidienne / Salubrité",
                                    "sae_projet": "Atelier pratique de lessive et ménage écologique",
                                    "ressources": "Pictogrammes d'entretien des textiles"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt2_aps_4",
                                    "titre": "Relations amoureuses saines, consentement et sexualité",
                                    "description": "Le respect dans le couple, reconnaître les relations toxiques, le consentement libre et éclairé, contraception et ITSS.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Santé - APS / Sexualité",
                                    "sae_projet": "Atelier Éducaloi : Le consentement et la loi",
                                    "ressources": "Guides Éducaloi, film Franchir la ligne (ONF)"
                                },
                                {
                                    "id": "fpt2_aps_5",
                                    "titre": "Autonomie financière : Ateliers MFMC (Modules 4 et 12)",
                                    "description": "Modules Desjardins : Dépenses imprévues (Module 4) et revenus/crédit (Module 12). Comprendre les pièges des cartes de crédit.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Autonomie financière - APS / Crédit",
                                    "sae_projet": "Atelier MFMC : Le crédit et les dettes",
                                    "ressources": "Cahiers MFMC Desjardins"
                                },
                                {
                                    "id": "fpt2_aps_6",
                                    "titre": "Logement : Recherche d'appartement et formulaire 31",
                                    "description": "Comment chercher un loyer, lire une annonce, visiter un logement, comprendre le relevé 31 pour les impôts et les frais annexes (Hydro-Québec).",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Logement et autonomie",
                                    "sae_projet": "Simulation de recherche d'appartement et visite",
                                    "ressources": "Sites Kijiji/Marketplace, guides TAL"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt2_aps_7",
                                    "titre": "Sécurité routière et préparation au permis de conduire",
                                    "description": "Code de la sécurité routière, règles pour piétons, cyclistes et futurs conducteurs. Conséquences de la conduite avec facultés affaiblies.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Transport - APS / Sécurité au volant",
                                    "sae_projet": "Quiz sécurité routière SAAQ",
                                    "ressources": "Documentation éducative SAAQ"
                                },
                                {
                                    "id": "fpt2_aps_8",
                                    "titre": "Droits du consommateur et gestion des litiges",
                                    "description": "Que faire si un appareil acheté est brisé ? Connaître ses droits de garantie légale auprès de l'Office de la protection du consommateur.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Consommation - APS / Prévention",
                                    "sae_projet": "Simulation de réclamation au service à la clientèle",
                                    "ressources": "Guides OPC, lettres types de mise en demeure"
                                },
                                {
                                    "id": "fpt2_aps_9",
                                    "titre": "Bilan d'autonomie personnelle globale FPT2",
                                    "description": "Évaluer son niveau de préparation à la vie autonome : cuisine, budget, transport, santé et gestion de ses documents personnels.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Autonomie et citoyenneté",
                                    "sae_projet": "Grille bilan Mon autonomie en route vers l'an 3",
                                    "ressources": "Dossier d'autonomie personnelle"
                                }
                            ]
                        }
                    }
                }
            },
            "FPT3": {
                "titre": "Formation préparatoire au travail - An 3 (FPT 3)",
                "description": "Troisième et dernière année du cycle FPT. Année de diplomation et de transition vers la vie active (TEVA). Les stages en entreprise occupent 3 jours par semaine. L'élève consolide son autonomie adulte (appartement, impôts, employabilité réelle).",
                "matieres": {
                    "stage": {
                        "nom": "Insertion professionnelle en stage intensif (IP)",
                        "code": "STG-FPT3",
                        "enseignant_ref": "Marie-Pier Lavoie et Véronique Paradis (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Exercer un rôle de travailleur qualifié en milieu de travail", "desc": "Accomplir avec constance, précision et rapidité l'ensemble des tâches reliées au poste en entreprise."},
                            {"code": "C2", "titre": "Démontrer des habiletés d'intégration et de maintien en emploi", "desc": "Résoudre les problèmes au poste, s'adapter aux changements de consignes et maintenir des relations professionnelles solides."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Intégration sur le poste intensif de 3 jours/semaine. Étape 2 (20%): Constante du rendement et autonomie. Étape 3 (60%): Évaluation sommative finale en vue de l'attestation ministérielle de formation préparatoire au travail.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt3_stg_1",
                                    "titre": "Intégration au stage intensif (3 jours par semaine)",
                                    "description": "Adopter un rythme de travail adulte. Maîtriser immédiatement les consignes de sécurité et l'organisation de son horaire de travail.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle / Stage intensif",
                                    "sae_projet": "Objectifs de performance du premier mois",
                                    "ressources": "Contrat de stage intensif FPT3"
                                },
                                {
                                    "id": "fpt3_stg_2",
                                    "titre": "Maîtrise des gestes professionnels et des cadences",
                                    "description": "Exécuter les tâches sans supervision constante, atteindre un niveau de qualité professionnel et respecter les temps de production.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle / Productivité",
                                    "sae_projet": "Suivi hebdomadaire de rendement avec le tuteur",
                                    "ressources": "Grille critériée de compétences FPT"
                                },
                                {
                                    "id": "fpt3_stg_3",
                                    "titre": "Communication efficace avec l'équipe de travail",
                                    "description": "Collaborer harmonieusement avec des travailleurs de tous âges et origines, faire part des difficultés avec professionnalisme.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Société / Relations de travail",
                                    "sae_projet": "Observation des dynamiques d'équipe en entreprise",
                                    "ressources": "Fiches de communication interpersonnelle"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt3_stg_4",
                                    "titre": "Polyvalence et adaptation à différents postes",
                                    "description": "Démontrer sa capacité à remplacer un collègue sur une autre tâche ou à s'adapter à une nouvelle consigne sans déstabilisation.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle / Polyvalence",
                                    "sae_projet": "Défi polyvalence sur plusieurs postes en entreprise",
                                    "ressources": "Fiches de postes multiples"
                                },
                                {
                                    "id": "fpt3_stg_5",
                                    "titre": "Résolution d'imprévus et initiative sur le plancher",
                                    "description": "Savoir intervenir calmement en cas de rupture de stock, de bris matériel ou de consigne inhabituelle.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Résolution de problèmes",
                                    "sae_projet": "Étude de cas réels vécus sur le lieu de stage",
                                    "ressources": "Cahier de bord de stage"
                                },
                                {
                                    "id": "fpt3_stg_6",
                                    "titre": "Préparation du bilan TEVA avec les intervenants",
                                    "description": "Rencontre avec les conseillers en orientation et le milieu de travail pour envisager l'embauche directe post-diplôme.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Insertion professionnelle / TEVA",
                                    "sae_projet": "Rencontre de plan d'action TEVA",
                                    "ressources": "Calendrier actions TEVA FPT"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt3_stg_7",
                                    "titre": "Évaluation sommative ministérielle en entreprise",
                                    "description": "Évaluation officielle des compétences requises en entreprise pour l'obtention du certificat officiel de la FPT.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle / Qualification",
                                    "sae_projet": "Bilan de compétences officiel ministériel",
                                    "ressources": "Grille officielle d'évaluation sommative"
                                },
                                {
                                    "id": "fpt3_stg_8",
                                    "titre": "Possibilité d'embauche ou transition vers le marché régulier",
                                    "description": "Négocier une offre d'emploi étudiant ou temps plein avec son entreprise de stage ou préparer ses candidatures externes.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle / Emploi",
                                    "sae_projet": "Démarche de signature de contrat d'embauche",
                                    "ressources": "Contrats d'embauche types"
                                },
                                {
                                    "id": "fpt3_stg_9",
                                    "titre": "Passation du certificat et célébration de fin de cycle",
                                    "description": "Clôture du parcours de 3 ans de formation préparatoire au travail et bilan des apprentissages de vie.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Identité et accomplissement",
                                    "sae_projet": "Cérémonie de remise des attestations FPT",
                                    "ressources": "Portfolio final de l'élève"
                                }
                            ]
                        }
                    },
                    "pmt": {
                        "nom": "Préparation au marché du travail 3 (PMT)",
                        "code": "PMT-FPT3",
                        "enseignant_ref": "Véronique Paradis (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Consolider son identité de travailleur adulte", "desc": "Reconnaître ses compétences, assumer ses choix de carrière et planifier son avenir avec réalisme."},
                            {"code": "C2", "titre": "Naviguer sur le marché du travail québécois", "desc": "Connaître les ressources d'aide à l'emploi (CJE, Services Québec), la fiscalité et le droit du travail."},
                            {"code": "C3", "titre": "Réaliser sa démarche complète d'insertion socioprofessionnelle", "desc": "Postuler de façon autonome, réussir ses entrevues et maintenir son emploi."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): CV final et lettre de présentation. Étape 2 (20%): Fiscalité et démarches CJE. Étape 3 (60%): Dossier complet TEVA et simulation d'embauche réelle.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt3_pmt_1",
                                    "titre": "Portfolio professionnel final et CV d'adulte",
                                    "description": "Finaliser un CV impeccable valorisant 2 ans d'expérience de stage en entreprise. Préparer une lettre de motivation ciblée.",
                                    "competences": ["C1", "C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle - PMT",
                                    "sae_projet": "Mon dossier professionnel d'adulte prêt à postuler",
                                    "ressources": "Traitement de texte, gabarits professionnels"
                                },
                                {
                                    "id": "fpt3_pmt_2",
                                    "titre": "Les partenaires de l'emploi : Carrefour jeunesse-emploi (CJE)",
                                    "description": "Visite du CJE local et de Services Québec. Comprendre les services gratuits offerts aux jeunes chercheurs d'emploi.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Société / Services d'emploi",
                                    "sae_projet": "Visite guidée et ouverture de dossier au CJE",
                                    "ressources": "Intervenants CJE / Services Québec"
                                },
                                {
                                    "id": "fpt3_pmt_3",
                                    "titre": "Maintien en emploi et périodes d'essai",
                                    "description": "Comprendre les 3 premiers mois d'embauche (période de probation), l'importance de la constance et de la diplomatie.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail / Pérennité d'emploi",
                                    "sae_projet": "Guide pour réussir sa période de probation",
                                    "ressources": "Témoignages d'anciens diplômés FPT"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt3_pmt_4",
                                    "titre": "Impôts, déclaration de revenus et crédits de solidarité",
                                    "description": "Comprendre pourquoi on fait ses impôts (retour de taxes, crédit TPS, crédit de solidarité). Déclaration simplifiée pour travailleur.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Autonomie financière / Fiscalité",
                                    "sae_projet": "Atelier clinique d'impôt simplifié",
                                    "ressources": "Formulaires Revenu Québec et ARC simplifiés"
                                },
                                {
                                    "id": "fpt3_pmt_5",
                                    "titre": "Formation continue et qualifications d'avenir",
                                    "description": "Explorer les possibilités futures : passerelle vers la FMS, attestations d'études professionnelles (AEP), DEP ou formation en entreprise.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Cheminement",
                                    "sae_projet": "Plan de formation à 5 ans",
                                    "ressources": "Répertoire des centres de formation professionnelle (CFP)"
                                },
                                {
                                    "id": "fpt3_pmt_6",
                                    "titre": "Gestion des conflits et harcèlement au travail",
                                    "description": "Reconnaître le harcèlement psychologique ou sexuel au travail. Savoir à qui s'adresser pour porter plainte et faire respecter ses droits.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail / SST et éthique",
                                    "sae_projet": "Étude de cas : Harcèlement et recours CNESST",
                                    "ressources": "Brochures CNESST sur le harcèlement"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt3_pmt_7",
                                    "titre": "Plan d'action TEVA final pour la vie adulte",
                                    "description": "Consigner les contacts de son tuteur, son conseiller CJE, son budget d'entrée dans la vie autonome et ses objectifs à 1 an.",
                                    "competences": ["C1", "C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle / TEVA",
                                    "sae_projet": "Passeport TEVA de sortie de scolarité",
                                    "ressources": "Dossier TEVA officiel"
                                },
                                {
                                    "id": "fpt3_pmt_8",
                                    "titre": "Simulation d'embauche réelle avec jury externe",
                                    "description": "Entrevue formelle devant des employeurs réels ou membres de la communauté scolaire pour valider son employabilité.",
                                    "competences": ["C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle - PMT",
                                    "sae_projet": "Grand jury d'employabilité de fin d'études",
                                    "ressources": "Grille critériée de jury"
                                },
                                {
                                    "id": "fpt3_pmt_9",
                                    "titre": "Fierté du parcours accompli et projection citoyenne",
                                    "description": "Regard rétrospectif sur les 3 années de formation, célébration de l'autonomie conquise et engagement citoyen.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Identité et accomplissement",
                                    "sae_projet": "Bilan d'accomplissement personnel",
                                    "ressources": "Capsule vidéo souvenir ou album de promotion"
                                }
                            ]
                        }
                    },
                    "mathematiques": {
                        "nom": "Mathématiques appliquées à la vie autonome",
                        "code": "MAT-FPT3",
                        "enseignant_ref": "Marie-Pier Lavoie (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Résoudre une situation-problème de la vie financière", "desc": "Calculer l'ensemble des frais réels de la vie en appartement et d'un salaire réel de travailleur."},
                            {"code": "C2", "titre": "Déployer un raisonnement mathématique", "desc": "Calculs de pourcentages, intérêts, amortissement, conversion et lecture de plans techniques."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Calculs de salaires et déductions. Étape 2 (20%): Intérêts d'emprunt, crédit et assurances. Étape 3 (60%): Situation-problème finale : Budget annuel équilibré d'un ménage.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fpt3_mat_1",
                                    "titre": "Calcul du salaire net réel et des retenues fiscales",
                                    "description": "Formule de calcul des cotisations RRQ, RQAP, AE et impôts selon les tables de retenue simplifiées.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Autonomie financière / Salaires",
                                    "sae_projet": "Simulateur de calcul de paie nette québécoise",
                                    "ressources": "Tables de retenues à la source"
                                },
                                {
                                    "id": "fpt3_mat_2",
                                    "titre": "Factures d'énergie et de télécommunications",
                                    "description": "Décoder une facture d'électricité (kWh, tarif de base) et un forfait cellulaire/internet (taxes, dépassement de données).",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Logement et services",
                                    "sae_projet": "Analyse comparée de forfaits cellulaires",
                                    "ressources": "Factures Hydro-Québec et forfaits mobiles"
                                },
                                {
                                    "id": "fpt3_mat_3",
                                    "titre": "Rapports qualité-prix et achats en gros format",
                                    "description": "Calcul du coût unitaire dans les magasins grande surface (Costco) vs épicerie standard : est-ce vraiment rentable ?",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Consommation - APS",
                                    "sae_projet": "Étude mathématique de rentabilité des achats en vrac",
                                    "ressources": "Circulaires de magasins grandes surfaces"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fpt3_mat_4",
                                    "titre": "Le coût du crédit : Taux d'intérêt et paiement minimum",
                                    "description": "Calculer ce que coûte réellement un achat de 1000$ sur une carte de crédit à 20% si l'on ne paie que le minimum chaque mois.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Autonomie financière / Crédit",
                                    "sae_projet": "Simulateur du piège des paiements minimums",
                                    "ressources": "Calculateurs de crédit en ligne (OPC/Desjardins)"
                                },
                                {
                                    "id": "fpt3_mat_5",
                                    "titre": "Mesures de surfaces et rénovation simple",
                                    "description": "Calculer l'aire d'un mur (longueur x hauteur) pour déterminer le nombre de gallons de peinture nécessaires. Coût total.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Logement / Aménagement",
                                    "sae_projet": "Estimation des coûts pour repeindre une pièce",
                                    "ressources": "Galons à mesurer, fiches de rendement de peinture"
                                },
                                {
                                    "id": "fpt3_mat_6",
                                    "titre": "Assurances de base : Habitation et auto",
                                    "description": "Comprendre les notions de prime, franchise et déductible. Calculer le coût mensuel et annuel d'une assurance locataire.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Sécurité financière / Logement",
                                    "sae_projet": "Comparaison de soumissions d'assurance habitation",
                                    "ressources": "Exemples de polices d'assurance"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fpt3_mat_7",
                                    "titre": "Situation-problème finale : Budget annuel autonome",
                                    "description": "Intégrer toutes les dépenses d'une année (loyer, nourriture, électricité, transport, vêtements, urgences, loisirs) avec son salaire réel.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Autonomie financière / Synthèse",
                                    "sae_projet": "Grand budget d'autonomie financière pour la vie adulte",
                                    "ressources": "Grilles budgétaires Excel / papier officielles"
                                },
                                {
                                    "id": "fpt3_mat_8",
                                    "titre": "Épargne et fonds d'urgence de base",
                                    "description": "Pourquoi et comment mettre de côté 25$ à 50$ par paie pour faire face aux bris, retards ou pertes d'emploi temporaires.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Sécurité financière",
                                    "sae_projet": "Plan d'épargne d'urgence sur 12 mois",
                                    "ressources": "Tableaux d'intérêts composés simples"
                                },
                                {
                                    "id": "fpt3_mat_9",
                                    "titre": "Bilan des compétences mathématiques pratiques",
                                    "description": "Consolidation de l'utilisation de la calculatrice, du téléphone et des outils numériques pour ne jamais se faire avoir.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Autonomie au quotidien",
                                    "sae_projet": "Quiz pratique de calculs du quotidien",
                                    "ressources": "Fiches de mise en situation concrète"
                                }
                            ]
                        }
                    }
                }
            },
            "FMS": {
                "titre": "Formation menant à l'exercice d'un métier semi-spécialisé (FMS)",
                "description": "Parcours d'un an axé sur l'apprentissage d'un métier semi-spécialisé officiel du répertoire ministériel (minimum 375 heures de stage en entreprise). Matières générales de 2e secondaire adaptées (Français, Mathématiques, Anglais) et préparation au marché du travail (PMT).",
                "matieres": {
                    "francais": {
                        "nom": "Français, langue d'enseignement (2e secondaire)",
                        "code": "FRA-FMS",
                        "enseignant_ref": "Célia Tereso (Dalbé-Viau / 132208) & Laila Bissonnette (RVP)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Lire et apprécier des textes variés (40 %)", "desc": "Comprendre des textes courants descriptifs, justificatifs et narratifs de 2e secondaire. Inférer le sens et repérer l'essentiel."},
                            {"code": "C2", "titre": "Écrire des textes variés (40 %)", "desc": "Rédiger des séquences descriptives et justificatives cohérentes. Respecter la syntaxe, la ponctuation et l'orthographe."},
                            {"code": "C3", "titre": "Communiquer oralement selon des modalités variées (20 %)", "desc": "Interagir efficacement, présenter des comptes-rendus oraux et justifier son point de vue avec clarté."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Texte courant à séquence descriptive, classes de mots variables, projet littéraire. Étape 2 (20%): Texte justificatif, accords du participe passé, inférences, lecture de roman. Étape 3 (60%): Épreuve de synthèse en écriture et lecture (40% Lire, 40% Écrire, 20% Oral).",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fms_fr_1",
                                    "titre": "Texte courant : Séquence descriptive et plan thématique",
                                    "description": "Comprendre la structure d'un texte descriptif : introduction, aspects et sous-aspects, intertitres, photographies et légendes.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Genres textuels / Métiers",
                                    "sae_projet": "Lecture de fiches descriptives de métiers semi-spécialisés",
                                    "ressources": "Textes descriptifs avec et sans intertitres"
                                },
                                {
                                    "id": "fms_fr_2",
                                    "titre": "Rédaction d'un texte descriptif complet",
                                    "description": "Rédiger un texte descriptif respectant la cohérence textuelle, les marqueurs de relation et un vocabulaire précis.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Écriture fonctionnelle",
                                    "sae_projet": "Fiche descriptive illustrée sur son métier de stage",
                                    "ressources": "Grille de planification et plan d'écriture"
                                },
                                {
                                    "id": "fms_fr_3",
                                    "titre": "Classes de mots variables et phrase de base",
                                    "description": "Nom, déterminant, adjectif, verbe et pronom. Accord dans le groupe nominal et fonctions syntaxiques de base (sujet, prédicat).",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Grammaire et syntaxe",
                                    "sae_projet": "Ateliers de révision grammaticale ciblée",
                                    "ressources": "Cahier maison de français FMS"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fms_fr_4",
                                    "titre": "Texte justificatif et formulation d'arguments",
                                    "description": "Identifier la question, formuler une prise de position claire et étayer avec des critères et preuves tirées du texte.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Genres textuels / Argumentation",
                                    "sae_projet": "Rédiger un paragraphe de justification d'opinion",
                                    "ressources": "Textes d'opinion pour jeunes, grille de justification"
                                },
                                {
                                    "id": "fms_fr_5",
                                    "titre": "Stratégies de lecture : Inférences et lecture entre les lignes",
                                    "description": "Dégager les informations implicites dans un texte littéraire ou informatif. Relever des indices textuels probants.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Stratégies de lecture",
                                    "sae_projet": "Lecture guidée d'un roman jeunesse adapté",
                                    "ressources": "Roman jeunesse (ex: La fille d'en face ou Le passage)"
                                },
                                {
                                    "id": "fms_fr_6",
                                    "titre": "Accord du participe passé et classes invariables",
                                    "description": "Accord du participe passé avec être vs avoir. Reconnaissance des adverbes, prépositions et conjonctions de coordination.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Grammaire et syntaxe",
                                    "sae_projet": "Ateliers de justification grammaticale",
                                    "ressources": "Cahier de règles d'accord"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fms_fr_7",
                                    "titre": "Communication orale formelle : Présentation de son métier",
                                    "description": "Exposé oral structuré de 5 minutes sur son métier semi-spécialisé : tâches du carnet d'apprentissage, outils et défis.",
                                    "competences": ["C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Communication professionnelle",
                                    "sae_projet": "Exposé oral avec diaporama sur son métier FMS",
                                    "ressources": "Grille d'évaluation sommative orale (20%)"
                                },
                                {
                                    "id": "fms_fr_8",
                                    "titre": "Épreuve d'écriture de fin d'année (40%)",
                                    "description": "Rédaction d'un texte complet de 200 à 250 mots (descriptif ou justificatif) à partir d'un dossier documentaire fourni.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Évaluation sommative ministérielle",
                                    "sae_projet": "Épreuve bilan d'écriture de 2e secondaire",
                                    "ressources": "Dossier documentaire et cahier de rédaction"
                                },
                                {
                                    "id": "fms_fr_9",
                                    "titre": "Épreuve de lecture de fin d'année (40%)",
                                    "description": "Questions de compréhension, d'interprétation, de réaction et de jugement critique sur des textes variés.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Évaluation sommative ministérielle",
                                    "sae_projet": "Épreuve bilan de lecture de 2e secondaire",
                                    "ressources": "Cahier de textes et questionnaire d'examen"
                                }
                            ]
                        }
                    },
                    "mathematiques": {
                        "nom": "Mathématiques (2e secondaire)",
                        "code": "MAT-FMS",
                        "enseignant_ref": "Marie-Claude Bergeron (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Résoudre une situation-problème (30 %)", "desc": "Mobiliser plusieurs concepts mathématiques pour résoudre une situation complexe inédite et justifier sa démarche."},
                            {"code": "C2", "titre": "Déployer un raisonnement mathématique (70 %)", "desc": "Maîtriser les savoirs prescrits : arithmétique, proportionnalité, algèbre de base, géométrie et statistiques."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Nombres entiers et rationnels, proportions et pourcentages. Étape 2 (20%): Algèbre (équations du 1er degré), figures planes et cercles. Étape 3 (60%): Aire des solides décomposables, volume, statistiques et CD1 bilan.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fms_mat_1",
                                    "titre": "Nombres entiers et rationnels (fractions et décimaux)",
                                    "description": "Chaîne d'opérations avec respect des priorités d'opérations (PEMDAS), fractions positives et négatives, notation scientifique.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Arithmétique",
                                    "sae_projet": "Résolution de chaînes d'opérations en contexte réel",
                                    "ressources": "Cahier de mathématiques 2e secondaire FMS"
                                },
                                {
                                    "id": "fms_mat_2",
                                    "titre": "Rapports, taux et situations de proportionnalité",
                                    "description": "Reconnaître une situation directement proportionnelle, calculer le coefficient de proportionnalité, produit croisé si approprié.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Proportions",
                                    "sae_projet": "Calcul de rendements, mélanges de produits et échelles",
                                    "ressources": "Problèmes de proportions appliquées aux métiers"
                                },
                                {
                                    "id": "fms_mat_3",
                                    "titre": "Pourcentages et calculs commerciaux",
                                    "description": "Calcul de taxes, rabais successifs, commissions et marges bénéficiaires simples.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Commerce et métiers",
                                    "sae_projet": "Facturation commerciale et calculs de prix de vente",
                                    "ressources": "Factures et grilles tarifaires"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fms_mat_4",
                                    "titre": "Introduction à l'algèbre : Expressions algébriques",
                                    "description": "Variables, termes semblables, réduction d'expressions algébriques simples (addition et soustraction de monômes).",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Algèbre",
                                    "sae_projet": "Traduction de situations de la vie en expressions algébriques",
                                    "ressources": "Fiches d'exercices d'algèbre concrète"
                                },
                                {
                                    "id": "fms_mat_5",
                                    "titre": "Résolution d'équations du premier degré à une inconnue",
                                    "description": "Méthode de la balance pour isoler la variable (ex: 3x + 12 = 45). Vérification de la solution.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Algèbre",
                                    "sae_projet": "Résolution de devinettes et problèmes appliqués par équation",
                                    "ressources": "Balances algébriques, exercices progressifs"
                                },
                                {
                                    "id": "fms_mat_6",
                                    "titre": "Géométrie plane : Cercle, disque et polygones",
                                    "description": "Circonférence du cercle (pi x d), aire du disque (pi x r^2), périmètre et aire des figures planes usuelles.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Géométrie",
                                    "sae_projet": "Calculs de surface de découpe pour atelier",
                                    "ressources": "Formulaires de géométrie et compas"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fms_mat_7",
                                    "titre": "Aire des solides décomposables et calcul de volume",
                                    "description": "Prismes droits, cylindres et solides composés. Calcul de l'aire totale extérieure et du volume intérieur (capacité en litres).",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Géométrie de l'espace",
                                    "sae_projet": "Calcul de contenance et d'emballage industriel",
                                    "ressources": "Solides en bois ou plastique, formules d'aires"
                                },
                                {
                                    "id": "fms_mat_8",
                                    "titre": "Statistiques et probabilités",
                                    "description": "Moyenne arithmétique, médiane, diagrammes circulaires et à bandes. Probabilités simples et événements certains/impossibles.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Statistiques",
                                    "sae_projet": "Analyse statistique de résultats de production",
                                    "ressources": "Données réelles et tableaux statistiques"
                                },
                                {
                                    "id": "fms_mat_9",
                                    "titre": "Épreuve synthèse CD1 : Situation-problème de 2e secondaire",
                                    "description": "Situation-problème complexe mobilisant géométrie, proportions et coûts pour répondre à un mandat d'entreprise.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Évaluation sommative ministérielle",
                                    "sae_projet": "Épreuve de situation-problème CD1 bilan (30%)",
                                    "ressources": "Cahier officiel d'examen CD1"
                                }
                            ]
                        }
                    },
                    "stage": {
                        "nom": "Préparation à l'exercice d'un métier semi-spécialisé (Stage)",
                        "code": "STG-FMS",
                        "enseignant_ref": "Marie-Claude Bergeron (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Prendre connaissance du contexte du métier", "desc": "Explorer les exigences du métier choisi dans le répertoire ministériel, les installations et les équipements."},
                            {"code": "C2", "titre": "Exécuter les compétences spécifiques du métier semi-spécialisé", "desc": "Réaliser en entreprise les tâches prescrites au carnet officiel d'apprentissage (minimum 375 heures)."},
                            {"code": "C3", "titre": "Évaluer son niveau de maîtrise en vue de la qualification", "desc": "Faire le bilan des compétences obligatoires et facultatives validées par l'employeur."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Intégration en stage, attitudes et SST. Étape 2 (20%): Maîtrise des premières compétences du carnet ministériel. Étape 3 (60%): Évaluation sommative en entreprise pour l'obtention du certificat officiel de qualification professionnelle.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fms_stg_1",
                                    "titre": "Appropriation du carnet d'apprentissage du métier",
                                    "description": "Découverte des compétences obligatoires et facultatives inscrites au répertoire officiel du Ministère pour le métier visé.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Métier officiel ministériel",
                                    "sae_projet": "Mon carnet d'apprentissage du métier semi-spécialisé",
                                    "ressources": "Carnet officiel du MEQ (ex: Aide-cuisinier, Préposé à l'entretien)"
                                },
                                {
                                    "id": "fms_stg_2",
                                    "titre": "Intégration en entreprise et règles de sécurité spécifiques",
                                    "description": "Entrée en stage (3 jours par semaine), consignes d'hygiène (MAPAQ si alimentation) et sécurité (EPI, fiches de données de sécurité).",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Santé et sécurité en entreprise",
                                    "sae_projet": "Audit de sécurité de mon poste de stage",
                                    "ressources": "Normes MAPAQ / CNESST"
                                },
                                {
                                    "id": "fms_stg_3",
                                    "titre": "Assiduité, ponctualité et feuille de temps",
                                    "description": "Cumuler rigoureusement les heures pour atteindre le seuil obligatoire des 375 heures de stage. Signature hebdomadaire de l'employeur.",
                                    "competences": ["C1"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Rigueur et cadre professionnel",
                                    "sae_projet": "Suivi hebdomadaire de la banque des 375 heures",
                                    "ressources": "Feuille officielle de cumul des heures"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fms_stg_4",
                                    "titre": "Validation des compétences obligatoires du carnet",
                                    "description": "Entraînement et validation progressive des gestes techniques sous supervision directe du tuteur d'entreprise.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Compétences de métier",
                                    "sae_projet": "Validation des compétences obligatoires 1 à 3 du carnet",
                                    "ressources": "Fiches de critères du MEQ"
                                },
                                {
                                    "id": "fms_stg_5",
                                    "titre": "Rythme de travail et qualité d'exécution commerciale",
                                    "description": "Atteindre la vitesse d'exécution requise pour satisfaire les clients tout en maintenant un standard zéro défaut.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Productivité et excellence",
                                    "sae_projet": "Évaluation formative à mi-stage avec l'enseignant",
                                    "ressources": "Grille d'évaluation mi-parcours MEQ"
                                },
                                {
                                    "id": "fms_stg_6",
                                    "titre": "Communication avec l'équipe et les clients",
                                    "description": "Utiliser le vocabulaire technique approprié, transmettre un message clairement et faire preuve d'un excellent service client.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Service client et collaboration",
                                    "sae_projet": "Observation de situations de contact client",
                                    "ressources": "Grilles de savoir-être professionnel"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fms_stg_7",
                                    "titre": "Validation des compétences complémentaires et facultatives",
                                    "description": "Démontrer sa polyvalence sur l'ensemble des compétences inscrites au carnet de qualification.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Qualification professionnelle",
                                    "sae_projet": "Validation complète des compétences du carnet",
                                    "ressources": "Carnet de qualification ministériel"
                                },
                                {
                                    "id": "fms_stg_8",
                                    "titre": "Épreuve pratique sommative en entreprise",
                                    "description": "Évaluation officielle de qualification en milieu de travail menée conjointement par le patron et l'enseignant de la FMS.",
                                    "competences": ["C2", "C3"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Qualification officielle du MEQ",
                                    "sae_projet": "Examen pratique de qualification professionnelle",
                                    "ressources": "Formulaire ministériel de sanction des études FMS"
                                },
                                {
                                    "id": "fms_stg_9",
                                    "titre": "Obtention du certificat de qualification et plan d'emploi",
                                    "description": "Transition vers un emploi régulier ou poursuite en formation professionnelle (DEP) grâce aux acquis de 2e secondaire.",
                                    "competences": ["C3"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Diplomation et avenir",
                                    "sae_projet": "Plan de carrière et embauche post-FMS",
                                    "ressources": "Certificat officiel de formation à un métier semi-spécialisé"
                                }
                            ]
                        }
                    },
                    "pmt": {
                        "nom": "Préparation au marché du travail (PMT - FMS)",
                        "code": "PMT-FMS",
                        "enseignant_ref": "Marie-Claude Bergeron (Dalbé-Viau)",
                        "ponderation": {"etape1": "20 %", "etape2": "20 %", "etape3": "60 %"},
                        "competences": [
                            {"code": "C1", "titre": "Connaissance de soi et profil d'employabilité", "desc": "Évaluer ses aptitudes, ses traits de personnalité et sa motivation envers le métier semi-spécialisé choisi."},
                            {"code": "C2", "titre": "Comportement pendant la recherche d'emploi et en stage", "desc": "Maîtriser les démarches d'embauche, les entrevues de sélection et les exigences déontologiques du travail."}
                        ],
                        "evaluations_desc": "Étape 1 (20%): Connaissance de soi, choix de métier et CV. Étape 2 (20%): Entrevues, formulaires et normes du travail. Étape 3 (60%): Bilan d'employabilité, dossier de recherche d'emploi et diplomation.",
                        "etapes": {
                            "etape1": [
                                {
                                    "id": "fms_pmt_1",
                                    "titre": "Connaissance de soi et choix du métier semi-spécialisé",
                                    "description": "Explorer le répertoire des métiers semi-spécialisés (plus de 200 métiers classés par secteurs). Aligner ses intérêts avec son choix de stage.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Orientation et identité",
                                    "sae_projet": "Fiche de motivation et de sélection du métier visé",
                                    "ressources": "Répertoire ministériel des métiers semi-spécialisés"
                                },
                                {
                                    "id": "fms_pmt_2",
                                    "titre": "Rédaction d'un CV de qualification professionnelle",
                                    "description": "Structurer son CV en mettant en valeur les compétences manuelles, l'expérience pratique et les aptitudes au travail d'équipe.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle - PMT",
                                    "sae_projet": "CV professionnel prêt pour les employeurs",
                                    "ressources": "Modèles de CV adaptés FMS"
                                },
                                {
                                    "id": "fms_pmt_3",
                                    "titre": "Les attentes des employeurs québécois",
                                    "description": "Comprendre les priorités des patrons : assiduité, attitude positive, honnêteté, capacité à recevoir les critiques et rapidité.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Monde du travail / Savoir-être",
                                    "sae_projet": "Panel ou témoignages d'employeurs partenaires",
                                    "ressources": "Vidéos de recruteurs québécois"
                                }
                            ],
                            "etape2": [
                                {
                                    "id": "fms_pmt_4",
                                    "titre": "Simulations intensives d'entrevue d'embauche",
                                    "description": "Pratiquer les réponses aux questions difficiles : Pourquoi ce métier ? Quelles sont vos faiblesses ? Comment gérez-vous la pression ?",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Insertion professionnelle - PMT",
                                    "sae_projet": "Atelier de simulations d'entrevues avec grilles d'évaluation",
                                    "ressources": "Grille d'évaluation d'entrevue FMS"
                                },
                                {
                                    "id": "fms_pmt_5",
                                    "titre": "Lois du travail, CNESST et santé-sécurité",
                                    "description": "Étudier les droits des travailleurs : salaire minimum, heures supplémentaires, indemnités en cas d'accident de travail, recours.",
                                    "competences": ["C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Monde du travail / Cadre légal",
                                    "sae_projet": "Quiz CNESST et analyse de contrats de travail",
                                    "ressources": "Documentation CNESST"
                                },
                                {
                                    "id": "fms_pmt_6",
                                    "titre": "Compléter des formulaires d'embauche réels",
                                    "description": "Remplir avec exactitude les formulaires administratifs : formulaires fiscaux TD1 et TP-1015, spécimen de chèque pour dépôt direct.",
                                    "competences": ["C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Formalités d'embauche",
                                    "sae_projet": "Trousse administrative du nouvel employé",
                                    "ressources": "Formulaires réels d'embauche"
                                }
                            ],
                            "etape3": [
                                {
                                    "id": "fms_pmt_7",
                                    "titre": "Stratégie de maintien d'emploi et progression salariale",
                                    "description": "Comment se démarquer positivement, demander une augmentation ou des responsabilités accrues après l'embauche.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Progression professionnelle",
                                    "sae_projet": "Plan d'intégration et de progression professionnelle",
                                    "ressources": "Guides de cheminement professionnel"
                                },
                                {
                                    "id": "fms_pmt_8",
                                    "titre": "Passerelles vers le DEP et la formation professionnelle",
                                    "description": "Explorer comment les unités de 2e secondaire obtenues en FMS permettent d'accéder à certains DEP en formation professionnelle.",
                                    "competences": ["C1"],
                                    "duree_semaines": 5,
                                    "axe_thematique": "Poursuite d'études et DEP",
                                    "sae_projet": "Guide d'admission aux CFP (InforouteFPT)",
                                    "ressources": "Site InforouteFPT.org"
                                },
                                {
                                    "id": "fms_pmt_9",
                                    "titre": "Bilan d'employabilité final et certification FMS",
                                    "description": "Clôture du dossier professionnel, bilan des acquis et préparation de la transition vers la diplomation.",
                                    "competences": ["C1", "C2"],
                                    "duree_semaines": 4,
                                    "axe_thematique": "Diplomation et avenir",
                                    "sae_projet": "Portfolio de diplomation FMS",
                                    "ressources": "Dossier d'employabilité complet"
                                }
                            ]
                        }
                    }
                }
            }
        },
        "themes_integres": [
            {
                "id": "axe_sante",
                "nom": "Santé - APS & ÉPS",
                "sous_themes": ["État de santé et hygiène", "Alimentation et nutrition", "Sommeil réparateur", "Loisirs sains", "Prévention des dépendances"]
            },
            {
                "id": "axe_societe",
                "nom": "Société & Citoyenneté",
                "sous_themes": ["Habiletés sociales", "Vivre-ensemble et diversité", "Démocratie et vote", "Justice et droits", "Engagement bénévole"]
            },
            {
                "id": "axe_consommation",
                "nom": "Consommation & Publicité",
                "sous_themes": ["Besoins vs désirs", "Influence publicitaire", "Rapport qualité-prix", "Droits du consommateur"]
            },
            {
                "id": "axe_finances",
                "nom": "Autonomie financière",
                "sous_themes": ["Budget personnel (MFMC)", "Salaires et retenues", "Crédit et dettes", "Fiscalité et impôts"]
            },
            {
                "id": "axe_transport",
                "nom": "Transport & Déplacements",
                "sous_themes": ["Transport en commun", "Repérage et cartes", "Sécurité routière", "Coûts de transport"]
            },
            {
                "id": "axe_identite",
                "nom": "Identité personnelle et professionnelle",
                "sous_themes": ["Histoire de vie", "Intérêts RIASEC", "Forces et valeurs", "Mon portrait professionnel"]
            },
            {
                "id": "axe_travail",
                "nom": "Monde du travail & Sécurité",
                "sous_themes": ["Savoir-être au travail", "Santé-sécurité (CNESST / SIMDUT)", "Métiers et tâches", "Outils et outillage"]
            },
            {
                "id": "axe_insertion",
                "nom": "Insertion professionnelle & Stage",
                "sous_themes": ["Curriculum vitae", "Entrevue d'embauche", "Stage en entreprise", "Carnet d'apprentissage", "Démarche TEVA"]
            }
        ]
    }

if __name__ == '__main__':
    data = get_full_curriculum()
    with open('curriculum_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"curriculum_data.json généré avec succès. Parcours inclus: {list(data['parcours'].keys())}")
