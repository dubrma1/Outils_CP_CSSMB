# -*- coding: utf-8 -*-
"""
Enrichissement de curriculum_data.json pour FPT2, FPT3 et FMS.
"""
import json

def enrich():
    with open('curriculum_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # FPT2 additions: sciences, univers_social, anglais, eps
    fpt2 = data['parcours']['FPT2']['matieres']
    if 'sciences' not in fpt2:
        fpt2['sciences'] = {
            'nom': 'Expérimentations technologiques et scientifiques (EST 2)',
            'code': 'EST-FPT2',
            'enseignant_ref': 'Programme FPT - Cycle moyen',
            'ponderation': {'etape1': '20 %', 'etape2': '20 %', 'etape3': '60 %'},
            'competences': [
                {'code': 'C1', 'titre': 'Chercher des réponses à des problèmes scientifiques/technologiques', 'desc': 'Démarche expérimentale appliquée à l\'atelier et à l\'énergie.'},
                {'code': 'C2', 'titre': 'Mettre à profit ses connaissances scientifiques et technologiques', 'desc': 'Circuits électriques, forces, matériaux et technologies durables.'},
                {'code': 'C3', 'titre': 'Communiquer en science et technologie', 'desc': 'Schémas techniques, symboles électriques et rapports d\'observation.'}
            ],
            'evaluations_desc': 'Étape 1 (20%): Électricité et sécurité des circuits. Étape 2 (20%): Énergie, isolation et habitat. Étape 3 (60%): Projet technologique d\'atelier.',
            'etapes': {
                'etape1': [
                    {'id': 'fpt2_est_1', 'titre': 'Circuits électriques en série et en parallèle', 'description': 'Comprendre la différence entre circuit en série et en parallèle, fusibles, disjoncteurs et disjoncteurs différentiels (DDFT).', 'competences': ['C1', 'C2'], 'duree_semaines': 5, 'axe_thematique': 'Technologie et habitat', 'sae_projet': 'Montage d\'un panneau de distribution miniature', 'ressources': 'Fils, interrupteurs, DELs, multimètre'},
                    {'id': 'fpt2_est_2', 'titre': 'Propriétés des matériaux de construction et d\'atelier', 'description': 'Résistance mécanique, dureté, conductivité thermique et électrique des métaux, bois traités et plastiques composites.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Monde du travail / Matériaux', 'sae_projet': 'Test de résistance et flexion de matériaux', 'ressources': 'Échantillons de matériaux variés'},
                    {'id': 'fpt2_est_3', 'titre': 'Sécurité électrique au travail et à la maison', 'description': 'Dangers d\'électrocution, surchauffe des fils, multiprises en cascade et consignes SST lors de réparations.', 'competences': ['C2', 'C3'], 'duree_semaines': 4, 'axe_thematique': 'Santé et sécurité / Habitat', 'sae_projet': 'Guide illustré des dangers électriques domestiques', 'ressources': 'Fiches CNESST / Hydro-Québec'}
                ],
                'etape2': [
                    {'id': 'fpt2_est_4', 'titre': 'Énergie, isolation thermique et consommation responsable', 'description': 'Transfert de chaleur (conduction, convection, rayonnement). Isolation d\'un bâtiment (laine, coupe-froid) et économie d\'énergie.', 'competences': ['C1', 'C2'], 'duree_semaines': 5, 'axe_thematique': 'Environnement et habitat', 'sae_projet': 'Modélisation thermique d\'une maisonnette isolée', 'ressources': 'Thermomètres numériques, matériaux isolants'},
                    {'id': 'fpt2_est_5', 'titre': 'Traitement de l\'eau potable et gestion des eaux usées', 'description': 'Le cycle de l\'eau urbain : captation, filtration, chloration, distribution et traitement des égouts municipaux.', 'competences': ['C2', 'C3'], 'duree_semaines': 5, 'axe_thematique': 'Environnement / Communauté', 'sae_projet': 'Expérience de filtration d\'eau sur colonne de sable', 'ressources': 'Sable, gravier, charbon actif, eau trouble'},
                    {'id': 'fpt2_est_6', 'titre': 'Pollution de l\'air et qualité de l\'environnement intérieur', 'description': 'Sources de pollution intérieure (moisissures, composés organiques volatils, monoxyde de carbone) et aération requise.', 'competences': ['C2'], 'duree_semaines': 4, 'axe_thematique': 'Santé et environnement', 'sae_projet': 'Audit de ventilation et avertisseurs de fumée/CO', 'ressources': 'Détecteurs et fiches de prévention'}
                ],
                'etape3': [
                    {'id': 'fpt2_est_7', 'titre': 'Mécanismes de transmission du mouvement', 'description': 'Engrenages, courroies, chaînes et roues dentées. Rapport de vitesse et sens de rotation dans les outils industriels.', 'competences': ['C1', 'C2'], 'duree_semaines': 5, 'axe_thematique': 'Technologie et atelier', 'sae_projet': 'Montage d\'un réducteur de vitesse à engrenages', 'ressources': 'Kits d\'engrenages et poulies'},
                    {'id': 'fpt2_est_8', 'titre': 'Dessin technique et schématisation normalisée', 'description': 'Lire un plan en vue de face, de dessus et de côté. Utiliser des symboles normalisés pour schématiser un objet.', 'competences': ['C3'], 'duree_semaines': 5, 'axe_thematique': 'Communication technologique', 'sae_projet': 'Schéma de fabrication d\'une pièce d\'atelier', 'ressources': 'Papier isométrique, instruments de dessin'},
                    {'id': 'fpt2_est_9', 'titre': 'Projet de prototypage écoresponsable', 'description': 'Concevoir un objet technique à partir de pièces recyclées répondant à une problématique de l\'école ou du stage.', 'competences': ['C1', 'C2', 'C3'], 'duree_semaines': 4, 'axe_thematique': 'Innovation et écoresponsabilité', 'sae_projet': 'Projet synthèse technologique FPT2', 'ressources': 'Matériaux de récupération, atelier'}
                ]
            }
        }

    if 'univers_social' not in fpt2:
        fpt2['univers_social'] = {
            'nom': 'Géographie, histoire et éducation à la citoyenneté (USO 2)',
            'code': 'USO-FPT2',
            'enseignant_ref': 'Marie-Pier Lavoie et Catherine Patry-Sauvé (Dalbé-Viau)',
            'ponderation': {'etape1': '20 %', 'etape2': '20 %', 'etape3': '60 %'},
            'competences': [
                {'code': 'C1', 'titre': 'Construire son appartenance au territoire québécois', 'desc': 'Comprendre les corridors de transport, les régions économiques et le patrimoine territorial.'},
                {'code': 'C2', 'titre': 'S\'insérer dans la société québécoise', 'desc': 'Histoire du travail, syndicalisme, droits civiques et solidarité sociale.'}
            ],
            'evaluations_desc': 'Étape 1 (20%): Réseau des transports et aménagement territorial. Étape 2 (20%): Histoire du travail et syndicalisme au Québec. Étape 3 (60%): Projet citoyen et mondialisation.',
            'etapes': {
                'etape1': [
                    {'id': 'fpt2_us_1', 'titre': 'Corridors de transport et voie maritime du Saint-Laurent', 'description': 'Le fleuve Saint-Laurent comme autoroute commerciale historique et moderne : ports, ponts, transport ferroviaire et routier de marchandises.', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Territoire et transport', 'sae_projet': 'Carte des grands réseaux de transport de marchandises', 'ressources': 'Cartes du fleuve et des voies navigables'},
                    {'id': 'fpt2_us_2', 'titre': 'L\'urbanisation et la banlieue au Québec', 'description': 'Comment Montréal et les villes québécoises se sont développées : étalement urbain, transports collectifs et préservation des terres agricoles.', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Aménagement du territoire', 'sae_projet': 'Étude comparative : Vivre en ville vs vivre en banlieue', 'ressources': 'Photos aériennes comparatives'},
                    {'id': 'fpt2_us_3', 'titre': 'Patrimoine bâti et culturel régional', 'description': 'Reconnaître les bâtiments historiques, églises de village, anciens moulins et manufactures transformées de sa région.', 'competences': ['C1'], 'duree_semaines': 4, 'axe_thematique': 'Histoire et patrimoine', 'sae_projet': 'Circuit patrimonial de ma municipalité', 'ressources': 'Répertoires du patrimoine culturel du Québec'}
                ],
                'etape2': [
                    {'id': 'fpt2_us_4', 'titre': 'Histoire du travail et révolution industrielle au Québec', 'description': 'Passage de l\'artisanat agricole aux usines textiles et fonderies. Conditions de travail d\'autrefois (enfants au travail, 60h/semaine).', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Histoire du monde du travail', 'sae_projet': 'Frise historique : Les luttes ouvrières au Québec', 'ressources': 'Archives ONF / Musée McCord'},
                    {'id': 'fpt2_us_5', 'titre': 'Naissance du syndicalisme et conquête des normes du travail', 'description': 'Pourquoi les travailleurs se sont regroupés en syndicats : création des congés payés, semaine de 40 heures, salaire minimum et santé-sécurité.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Droits et monde du travail', 'sae_projet': 'Dossier : Comment nos droits de travailleur sont nés', 'ressources': 'Documents historiques CNESST'},
                    {'id': 'fpt2_us_6', 'titre': 'Système judiciaire québécois : Cours de justice et tribunaux', 'description': 'Différence entre Cour des petites créances, Cour du Québec et Tribunal administratif du travail. Régler un litige pacifiquement.', 'competences': ['C2'], 'duree_semaines': 4, 'axe_thematique': 'Justice et citoyenneté', 'sae_projet': 'Visite virtuelle du Palais de justice et procès simulé', 'ressources': 'CliquezJustice.ca et Éducaloi'}
                ],
                'etape3': [
                    {'id': 'fpt2_us_7', 'titre': 'Mondialisation et provenance des produits de consommation', 'description': 'D\'où viennent nos vêtements, cellulaires et fruits d\'hiver ? Découvrir le commerce équitable et les conditions de travail dans le monde.', 'competences': ['C1', 'C2'], 'duree_semaines': 5, 'axe_thematique': 'Consommation et mondialisation', 'sae_projet': 'Traçabilité d\'un chandail de coton : Du champ au magasin', 'ressources': 'Cartes du commerce mondial, In-Terre-Actif'},
                    {'id': 'fpt2_us_8', 'titre': 'L\'immigration et l\'apport des nouveaux arrivants au Québec', 'description': 'Le rôle clé de l\'immigration dans l\'économie québécoise, pénurie de main-d\'œuvre et francisation.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Société et vivre-ensemble', 'sae_projet': 'Témoignages de parcours d\'immigration au travail', 'ressources': 'Vidéos de l\'ONF et du Ministère de l\'Immigration'},
                    {'id': 'fpt2_us_9', 'titre': 'Projet d\'implication citoyenne locale', 'description': 'Prendre part à une initiative concrète : corvée de nettoyage de parc, aide à un comptoir vestimentaire ou bénévolat communautaire.', 'competences': ['C2'], 'duree_semaines': 4, 'axe_thematique': 'Engagement citoyen', 'sae_projet': 'Action citoyenne FPT2 réalisée en équipe', 'ressources': 'Organismes communautaires locaux'}
                ]
            }
        }

    if 'anglais' not in fpt2:
        fpt2['anglais'] = {
            'nom': 'Anglais, langue seconde (ANG 2)',
            'code': 'ANG-FPT2',
            'enseignant_ref': 'Programme FPT - Anglais fonctionnel',
            'ponderation': {'etape1': '20 %', 'etape2': '20 %', 'etape3': '60 %'},
            'competences': [
                {'code': 'C1', 'titre': 'Interagir oralement en milieu de travail', 'desc': 'Comprendre et exécuter des instructions en anglais, servir un client anglophone de façon polie.'},
                {'code': 'C2', 'titre': 'Lire des consignes et fiches en anglais', 'desc': 'Déchiffrer des manuels d\'outils, étiquettes de livraison et horaires de transport.'},
                {'code': 'C3', 'titre': 'Rédiger des messages fonctionnels', 'desc': 'Écrire de courts courriels professionnels, fiches de coordonnées et notes de service.'}
            ],
            'evaluations_desc': 'Étape 1 (20%): Vocabulaire du travail et salutations clients. Étape 2 (20%): Commandes, livraison et appels téléphoniques. Étape 3 (60%): Bilan oral professionnel et rédaction de courriel.',
            'etapes': {
                'etape1': [
                    {'id': 'fpt2_ang_1', 'titre': 'Customer Service & Workplace Greetings', 'description': 'Can I help you find something? I will be right with you. Dealing with polite requests from English-speaking customers.', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Insertion professionnelle / Service', 'sae_projet': 'Customer service role-play in a retail store', 'ressources': 'Scénarios de magasin en anglais'},
                    {'id': 'fpt2_ang_2', 'titre': 'Reading Delivery Slips & Shipping Labels', 'description': 'Understanding terms: Fragile, Sender, Recipient, Weight, Delivery address, Tracking number, Signature required.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Monde du travail / Manutention', 'sae_projet': 'Package sorting simulation with English labels', 'ressources': 'Bons de livraison réels anonymisés'},
                    {'id': 'fpt2_ang_3', 'titre': 'Numbers, Prices & Giving Change in English', 'description': 'That will be twenty-five dollars and fifty cents. Practicing listening comprehension for numbers from 1 to 1000.', 'competences': ['C1', 'C2'], 'duree_semaines': 4, 'axe_thematique': 'Commerce et caisse', 'sae_projet': 'Cash register role-play in English', 'ressources': 'Billets factices et reçus de caisse'}
                ],
                'etape2': [
                    {'id': 'fpt2_ang_4', 'titre': 'Taking Phone Messages at Work', 'description': 'May I ask who is calling? Could you please hold? Writing down a name, phone number and brief message accurately.', 'competences': ['C1', 'C3'], 'duree_semaines': 5, 'axe_thematique': 'Communication professionnelle', 'sae_projet': 'Workplace phone message pad simulation', 'ressources': 'Bloc-notes de messages téléphoniques'},
                    {'id': 'fpt2_ang_5', 'titre': 'Understanding Technical Tool Manuals & Symbols', 'description': 'Reading safety instructions: Keep dry, Do not immerse in water, Unplug before cleaning, Wear safety glasses.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Sécurité et outillage', 'sae_projet': 'Reading an appliance user manual in English', 'ressources': 'Manuels d\'instructions bilingues'},
                    {'id': 'fpt2_ang_6', 'titre': 'Travel & Public Transit in Canada / USA', 'description': 'Buying a bus/train ticket, asking about transfers, platform numbers and delays in English.', 'competences': ['C1', 'C2'], 'duree_semaines': 4, 'axe_thematique': 'Transport / Déplacement', 'sae_projet': 'Planning a weekend bus trip to Ottawa or Plattsburgh', 'ressources': 'Horaires Via Rail / Greyhound'}
                ],
                'etape3': [
                    {'id': 'fpt2_ang_7', 'titre': 'Writing a Formal Workplace Note or Email', 'description': 'Subject: Absence notice / Equipment issue. Dear supervisor, I am writing to inform you... Best regards.', 'competences': ['C3'], 'duree_semaines': 5, 'axe_thematique': 'Communication professionnelle', 'sae_projet': 'Writing a workplace email to an English supervisor', 'ressources': 'Modèles de courriels d\'affaires simples'},
                    {'id': 'fpt2_ang_8', 'titre': 'Talking About Work Tasks & Internship Experience', 'description': 'My internship is at... I am responsible for... I really enjoy working with... Describing daily tasks orally.', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Insertion professionnelle / Stage', 'sae_projet': 'My Internship presentation in English (2 minutes)', 'ressources': 'Fiches de vocabulaire de métiers'},
                    {'id': 'fpt2_ang_9', 'titre': 'Job Search Vocabulary & Simple Interview Prep', 'description': 'Full-time, part-time, shifts, wage, experience. Answering simple interview questions: Tell me about yourself.', 'competences': ['C1', 'C2'], 'duree_semaines': 4, 'axe_thematique': 'Insertion professionnelle - PMT', 'sae_projet': 'Mini job interview in English', 'ressources': 'Grille de questions d\'entrevue de base'}
                ]
            }
        }

    if 'eps' not in fpt2:
        fpt2['eps'] = {
            'nom': 'Éducation physique et à la santé (ÉPS 2)',
            'code': 'EPS-FPT2',
            'enseignant_ref': 'M. Azurdia (Dalbé-Viau)',
            'ponderation': {'etape1': '20 %', 'etape2': '20 %', 'etape3': '60 %'},
            'competences': [
                {'code': 'C1', 'titre': 'Agir dans divers contextes d\'activités physiques', 'desc': 'Endurance aérobie, force musculaire fonctionnelle et motricité fine et globale.'},
                {'code': 'C2', 'titre': 'Interagir dans divers contextes d\'activités physiques', 'desc': 'Jeux tactiques, arbitrage et esprit d\'équipe.'},
                {'code': 'C3', 'titre': 'Adopter un mode de vie sain et actif', 'desc': 'Gestion du sommeil, prévention des blessures au travail et saine alimentation.'}
            ],
            'evaluations_desc': 'Étape 1 (20%): Condition physique générale et échauffement. Étape 2 (20%): Sports d\'équipe et endurance hivernale. Étape 3 (60%): Autonomie sportive, ergonomie de travail et bilan.',
            'etapes': {
                'etape1': [
                    {'id': 'fpt2_eps_1', 'titre': 'Entraînement fonctionnel et prévention des blessures', 'description': 'Renforcement du tronc (gainage), posture lors du port de charges lourdes (squat, soulevé de terre sécuritaire).', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Santé et ergonomie', 'sae_projet': 'Circuit d\'exercices ergonomiques pour travailleur', 'ressources': 'Tapis de gym, boîtes de simulation de charge'},
                    {'id': 'fpt2_eps_2', 'titre': 'Endurance cardiorespiratoire : Course et natation', 'description': 'Développer son souffle et son endurance pour soutenir les journées physiques de stage sans épuisement.', 'competences': ['C1', 'C3'], 'duree_semaines': 5, 'axe_thematique': 'Santé / Énergie', 'sae_projet': 'Test navette de Léger adapté et progression', 'ressources': 'Bande sonore test navette'},
                    {'id': 'fpt2_eps_3', 'titre': 'Volleyball et sports de coopération rapide', 'description': 'Touches, manchettes, rotations sur le terrain et encouragement mutuel lors des erreurs de jeu.', 'competences': ['C2'], 'duree_semaines': 4, 'axe_thematique': 'Société / Esprit sportif', 'sae_projet': 'Tournoi intra-classe de volleyball', 'ressources': 'Ballons, filets'}
                ],
                'etape2': [
                    {'id': 'fpt2_eps_4', 'titre': 'Floorball (Hockey cosom) et esprit d\'équipe', 'description': 'Maniement du bâton, passes précises, respect de la zone de sécurité (pas de bâton élevé), respect des arbitres.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Société / Règles sportives', 'sae_projet': 'Ligue amicale de hockey cosom', 'ressources': 'Bâtons de floorball, lunettes de protection'},
                    {'id': 'fpt2_eps_5', 'titre': 'Gestion du stress par la respiration et la relaxation', 'description': 'Techniques de cohérence cardiaque, yoga doux et étirements passifs pour évacuer les tensions musculaires du travail.', 'competences': ['C3'], 'duree_semaines': 5, 'axe_thematique': 'Santé mentale et bien-être', 'sae_projet': 'Séance guidée de relaxation de fin de semaine', 'ressources': 'Tapis, musique de relaxation'},
                    {'id': 'fpt2_eps_6', 'titre': 'Plein air hivernal et persévérance', 'description': 'Sortie prolongée de ski de fond, patinage ou raquette. Développer la ténacité face au vent et au froid.', 'competences': ['C1', 'C3'], 'duree_semaines': 4, 'axe_thematique': 'Plein air et résilience', 'sae_projet': 'Défi de persévérance en plein air hivernal', 'ressources': 'Parcs de conservation régionaux'}
                ],
                'etape3': [
                    {'id': 'fpt2_eps_7', 'titre': 'Ultimate frisbee et sens du fair-play', 'description': 'Sport auto-arbitré : passe en suspension, démarquage rapide et négociation respectueuse des fautes.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Société / Fair-play', 'sae_projet': 'Tournoi d\'ultimate frisbee extérieur', 'ressources': 'Disques officiels Ultimate'},
                    {'id': 'fpt2_eps_8', 'titre': 'Conditionnement physique en plein air (Calisthénie)', 'description': 'Utiliser les parcs urbains d\'entraînement (trekkfit) pour s\'entraîner gratuitement tout au long de l\'été.', 'competences': ['C1', 'C3'], 'duree_semaines': 5, 'axe_thematique': 'Loisirs et santé', 'sae_projet': 'Circuit forme dans le parc municipal', 'ressources': 'Modules d\'entraînement extérieur'},
                    {'id': 'fpt2_eps_9', 'titre': 'Bilan de santé et habitudes de vie active', 'description': 'Évaluer ses progrès physiques sur l\'année et consigner ses engagements pour rester actif à l\'âge adulte.', 'competences': ['C3'], 'duree_semaines': 4, 'axe_thematique': 'Mode de vie sain et actif', 'sae_projet': 'Mon bilan forme FPT2 et charte active', 'ressources': 'Dossier personnel d\'éducation physique'}
                ]
            }
        }

    # FPT3 additions: francais, aps
    fpt3 = data['parcours']['FPT3']['matieres']
    if 'francais' not in fpt3:
        fpt3['francais'] = {
            'nom': 'Français appliqué à la vie adulte',
            'code': 'FRA-FPT3',
            'enseignant_ref': 'Marie-Pier Lavoie et Véronique Paradis (Dalbé-Viau)',
            'ponderation': {'etape1': '20 %', 'etape2': '20 %', 'etape3': '60 %'},
            'competences': [
                {'code': 'C1', 'titre': 'Lire et comprendre des documents de la vie adulte', 'desc': 'Contrats, baux, assurances, notices de médicaments, documents juridiques simplifiés.'},
                {'code': 'C2', 'titre': 'Rédiger avec autonomie et clarté', 'desc': 'Courriels d\'embauche, réclamations, formulaires officiels et bilan d\'insertion.'},
                {'code': 'C3', 'titre': 'Communiquer oralement avec assurance', 'desc': 'Entretiens d\'embauche, démarches administratives et interactions citoyennes.'}
            ],
            'evaluations_desc': 'Étape 1 (20%): CV final et lecture de contrats. Étape 2 (20%): Correspondance administrative et impôts. Étape 3 (60%): Entrevue d\'embauche formelle et portfolio final.',
            'etapes': {
                'etape1': [
                    {'id': 'fpt3_fr_1', 'titre': 'Lecture critique de contrats et documents d\'engagement', 'description': 'Contrats de travail, forfaits cellulaires, cartes de crédit, garanties d\'appareils : repérer les petits caractères et engagements.', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Consommation et autonomie', 'sae_projet': 'Atelier Éducaloi : Lire avant de signer', 'ressources': 'Contrats réels d\'opérateurs cellulaires'},
                    {'id': 'fpt3_fr_2', 'titre': 'Dossier professionnel d\'embauche : CV et lettre percutante', 'description': 'Rédiger une candidature professionnelle sans fautes mettant en valeur 2 ans et demi d\'expérience de travail en entreprise.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Insertion professionnelle - PMT', 'sae_projet': 'Mon dossier de candidature prêt pour l\'embauche directe', 'ressources': 'Gabarits professionnels de traitement de texte'},
                    {'id': 'fpt3_fr_3', 'titre': 'Communication téléphonique et entretiens de présélection', 'description': 'Répondre à un employeur au téléphone avec professionnalisme, noter un rendez-vous et préparer ses questions.', 'competences': ['C3'], 'duree_semaines': 4, 'axe_thematique': 'Insertion professionnelle / Stage', 'sae_projet': 'Simulations d\'appels de présélection d\'embauche', 'ressources': 'Scénarios réels de recrutement'}
                ],
                'etape2': [
                    {'id': 'fpt3_fr_4', 'titre': 'Démarches administratives en ligne et sécurité numérique', 'description': 'Accéder à ClicSÉQUR, Mon dossier Services Québec, Revenu Québec. Comprendre les courriels d\'hameçonnage et fraudes.', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Citoyenneté numérique', 'sae_projet': 'Atelier Navigation sécuritaire sur les portails publics', 'ressources': 'Portails gouvernementaux québécois'},
                    {'id': 'fpt3_fr_5', 'titre': 'Lettre de réclamation et de mise en demeure simplifiée', 'description': 'Rédiger une lettre de réclamation courtoise mais ferme en cas de bris sous garantie ou de litige avec un propriétaire.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Consommation - APS / Droits', 'sae_projet': 'Rédaction guidée d\'une lettre de contestation', 'ressources': 'Modèles de mise en demeure de l\'OPC'},
                    {'id': 'fpt3_fr_6', 'titre': 'Lecture de notices médicales et fiches de santé', 'description': 'Comprendre les indications, posologies, effets secondaires et contre-indications sur des étiquettes de médicaments.', 'competences': ['C1'], 'duree_semaines': 4, 'axe_thematique': 'Santé - APS / Prévention', 'sae_projet': 'Décodage d\'étiquettes de pharmacie et premiers soins', 'ressources': 'Emballages de médicaments en vente libre'}
                ],
                'etape3': [
                    {'id': 'fpt3_fr_7', 'titre': 'Grand entretien d\'embauche final et plaidoyer pour son embauche', 'description': 'Exposer avec conviction ses compétences manuelles et relationnelles devant un jury d\'employeurs.', 'competences': ['C3'], 'duree_semaines': 5, 'axe_thematique': 'Insertion professionnelle - PMT', 'sae_projet': 'Entrevue d\'embauche officielle de sortie de formation', 'ressources': 'Grille officielle de diplomation FPT'},
                    {'id': 'fpt3_fr_8', 'titre': 'Portfolio de réalisation et lettre de projection d\'avenir', 'description': 'Rédiger une lettre à son futur soi récapitulant les victoires surmontées et fixant les buts à 2 ans dans la vie active.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Identité et accomplissement', 'sae_projet': 'Mon livre de vie FPT : De l\'école au travail', 'ressources': 'Cahier relié de fin d\'études'},
                    {'id': 'fpt3_fr_9', 'titre': 'Lecture de romans et culture générale pour le plaisir', 'description': 'Encourager la lecture autonome comme loisir permanent à l\'âge adulte (romans graphiques, bandes dessinées, revues).', 'competences': ['C1'], 'duree_semaines': 4, 'axe_thematique': 'Loisirs et culture', 'sae_projet': 'Abonnement et visite à la bibliothèque municipale', 'ressources': 'Bibliothèque de quartier'}
                ]
            }
        }

    if 'aps' not in fpt3:
        fpt3['aps'] = {
            'nom': 'Autonomie et participation sociale (APS 3 - Vie adulte)',
            'code': 'APS-FPT3',
            'enseignant_ref': 'Marie-Pier Lavoie (Dalbé-Viau)',
            'ponderation': {'etape1': '20 %', 'etape2': '20 %', 'etape3': '60 %'},
            'competences': [
                {'code': 'C1', 'titre': 'Gérer sa vie personnelle et son logement de façon autonome', 'desc': 'Bail, meubler un appartement, gestion des factures, alimentation autonome et santé.'},
                {'code': 'C2', 'titre': 'Participer pleinement à la vie citoyenne et communautaire', 'desc': 'Voter, connaître ses droits de citoyen, recourir aux services d\'aide et s\'entraider.'}
            ],
            'evaluations_desc': 'Étape 1 (20%): Préparation au logement et premier appartement. Étape 2 (20%): Finances personnelles, fiscalité et santé. Étape 3 (60%): Bilan complet de vie autonome et TEVA.',
            'etapes': {
                'etape1': [
                    {'id': 'fpt3_aps_1', 'titre': 'Projet Mon premier appartement : De la recherche à l\'emménagement', 'description': 'Calcul du budget de départ (dépôt, meubles, camion, Hydro-Québec, électroménagers). Signature du bail et état des lieux.', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Logement et autonomie', 'sae_projet': 'Dossier complet Mon premier chez-moi', 'ressources': 'Guides du Tribunal administratif du logement'},
                    {'id': 'fpt3_aps_2', 'titre': 'Alimentation autonome : Cuisiner pour une personne seule sans gaspillage', 'description': 'Gestion des restes, congélation de portions individuelles, batch cooking économique et équilibré.', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Santé - APS / Alimentation', 'sae_projet': 'Planification de menus de célibataire à faible coût', 'ressources': 'Recettes Trois fois par jour / Banques alimentaires'},
                    {'id': 'fpt3_aps_3', 'titre': 'Relations de voisinage et civisme en immeuble locatif', 'description': 'Respect des voisins, gestion du bruit nocturne, tri des déchets d\'immeuble et communication cordiale.', 'competences': ['C2'], 'duree_semaines': 4, 'axe_thematique': 'Société / Vie en communauté', 'sae_projet': 'Guide du bon locataire et voisin responsable', 'ressources': 'Règlements d\'immeubles types'}
                ],
                'etape2': [
                    {'id': 'fpt3_aps_4', 'titre': 'Système de santé québécois : Cliniques, 811 et rendez-vous', 'description': 'Comment consulter un médecin sans médecin de famille (GAP, Bonjour-santé), joindre Info-Santé 811, gérer sa carte d\'assurance-maladie (RAMQ).', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Santé - APS / Services et ressources', 'sae_projet': 'Guide pratique d\'accès aux soins de santé', 'ressources': 'Site RAMQ et portail Clic Santé'},
                    {'id': 'fpt3_aps_5', 'titre': 'Sécurité financière : Éviter les fraudes et le surendettement', 'description': 'Reconnaître les arnaques téléphoniques, textos frauduleux, prêts à taux usuraires (prêts sur salaire) et faillite.', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Autonomie financière - APS / Prévention', 'sae_projet': 'Clinique de prévention des arnaques financières', 'ressources': 'Centre antifraude du Canada / ACEF'},
                    {'id': 'fpt3_aps_6', 'titre': 'Santé mentale de l\'adulte et ressources de soutien', 'description': 'Lignes d\'écoute (Tel-Jeunes, 1-866-APPELLE), centres de crise communautaires et soutien psychosocial au CLSC.', 'competences': ['C1', 'C2'], 'duree_semaines': 4, 'axe_thematique': 'Santé mentale et bien-être', 'sae_projet': 'Mon répertoire personnel d\'urgence psychosociale', 'ressources': 'Bottin des ressources d\'aide psychosociale'}
                ],
                'etape3': [
                    {'id': 'fpt3_aps_7', 'titre': 'Dossier officiel TEVA et plan de vie adulte', 'description': 'Finaliser avec la famille et l\'équipe-école le plan de transition vers la vie active adulte (travail, loisirs, réseau social).', 'competences': ['C1', 'C2'], 'duree_semaines': 5, 'axe_thematique': 'Insertion professionnelle / TEVA', 'sae_projet': 'Plan TEVA officiel de diplomation', 'ressources': 'Dossier TEVA ministériel'},
                    {'id': 'fpt3_aps_8', 'titre': 'Citoyenneté active : Droit de vote et engagement dans sa ville', 'description': 'Vérifier son inscription sur la liste électorale permanente, assister à un conseil municipal ou s\'engager dans un club de quartier.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Société / Démocratie', 'sae_projet': 'Passeport citoyen de l\'adulte québécois', 'ressources': 'Élections Québec et conseils municipaux'},
                    {'id': 'fpt3_aps_9', 'titre': 'Bilan de sortie de scolarité : Je suis autonome !', 'description': 'Grand inventaire de toutes les compétences d\'autonomie validées au fil des 3 ans de formation.', 'competences': ['C1', 'C2'], 'duree_semaines': 4, 'axe_thematique': 'Autonomie et accomplissement', 'sae_projet': 'Certificat d\'autonomie personnelle FPT', 'ressources': 'Dossier de valorisation des acquis'}
                ]
            }
        }

    # FMS additions: anglais
    fms = data['parcours']['FMS']['matieres']
    if 'anglais' not in fms:
        fms['anglais'] = {
            'nom': 'Anglais, langue seconde (2e secondaire FMS)',
            'code': 'ANG-FMS',
            'enseignant_ref': 'Planification aux parents FMS (Baie-Saint-François)',
            'ponderation': {'etape1': '20 %', 'etape2': '20 %', 'etape3': '60 %'},
            'competences': [
                {'code': 'C1', 'titre': 'Communiquer oralement en anglais', 'desc': 'Interactions professionnelles, vocabulaire du métier, compréhension d\'instructions orales.'},
                {'code': 'C2', 'titre': 'Comprendre des textes lus et entendus', 'desc': 'Manuels de formation, consignes de sécurité, fiches techniques du métier.'},
                {'code': 'C3', 'titre': 'Écrire des textes en anglais', 'desc': 'Remplir des bons de commande, écrire des courriels courts et des rapports de travail.'}
            ],
            'evaluations_desc': 'Étape 1 (20%): Oral fonctionnel et consignes de base. Étape 2 (20%): Lecture technique et fiches de tâches. Étape 3 (60%): Évaluation de fin de 2e secondaire en anglais.',
            'etapes': {
                'etape1': [
                    {'id': 'fms_ang_1', 'titre': 'Workplace Vocabulary & Safety Instructions in English', 'description': 'Safety gear, emergency procedures, caution signs and following spoken multi-step instructions.', 'competences': ['C1', 'C2'], 'duree_semaines': 5, 'axe_thematique': 'Sécurité et milieu de travail', 'sae_projet': 'Workplace Safety Inspection in English', 'ressources': 'Fiches de sécurité industrielle en anglais'},
                    {'id': 'fms_ang_2', 'titre': 'Introducing Myself and My Semi-Skilled Trade', 'description': 'My name is... I am training as a... My daily tasks involve... Presenting one\'s trade with pride in English.', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Identité professionnelle', 'sae_projet': 'Short oral elevator pitch of my trade', 'ressources': 'Fiches de vocabulaire des 200 métiers semi-spécialisés'},
                    {'id': 'fms_ang_3', 'titre': 'Grammar & Functional Phrasing: Action Verbs', 'description': 'Action verbs on the job (clean, assemble, verify, store, repair, deliver) in the present tense.', 'competences': ['C3'], 'duree_semaines': 4, 'axe_thematique': 'Langue fonctionnelle', 'sae_projet': 'Trade action verbs flashcard set', 'ressources': 'Cartes de verbes d\'action'}
                ],
                'etape2': [
                    {'id': 'fms_ang_4', 'titre': 'Customer Service & Professional Phone Calls', 'description': 'Taking customer orders, answering questions about products, handling complaints courteously.', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Service client et communication', 'sae_projet': 'Simulated phone calls and store orders', 'ressources': 'Dialogues audio et scripts professionnels'},
                    {'id': 'fms_ang_5', 'titre': 'Reading Work Orders & Technical Specifications', 'description': 'Deciphering trade documents: item numbers, quantities, customer notes, delivery deadlines.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Lecture technique', 'sae_projet': 'Processing a customer work order in English', 'ressources': 'Bons de travail réels en anglais'},
                    {'id': 'fms_ang_6', 'titre': 'Writing Clear Workplace Notes & Emails', 'description': 'Writing a short note to a colleague: informing about a completed task or missing part.', 'competences': ['C3'], 'duree_semaines': 4, 'axe_thematique': 'Communication écrite', 'sae_projet': 'Writing shift handover notes in English', 'ressources': 'Modèles de mémos de travail'}
                ],
                'etape3': [
                    {'id': 'fms_ang_7', 'titre': 'Job Interview Simulation in English', 'description': 'Preparing answers for bilingual job interviews: Why do you want this job? What are your strengths?', 'competences': ['C1'], 'duree_semaines': 5, 'axe_thematique': 'Insertion professionnelle - PMT', 'sae_projet': 'Mock bilingual job interview', 'ressources': 'Grille de questions d\'entrevue'},
                    {'id': 'fms_ang_8', 'titre': 'Reading Articles About Youth and Careers', 'description': 'Reading comprehension of articles on modern trades, technology at work and entrepreneurship.', 'competences': ['C2'], 'duree_semaines': 5, 'axe_thematique': 'Culture et actualité professionnelle', 'sae_projet': 'Article summary and personal reaction', 'ressources': 'Magazines et articles web pour adolescents'},
                    {'id': 'fms_ang_9', 'titre': 'End of Year English Evaluation (Secondary 2)', 'description': 'Bilan des 3 compétences d\'anglais langue seconde du 1er cycle du secondaire en contexte professionnel.', 'competences': ['C1', 'C2', 'C3'], 'duree_semaines': 4, 'axe_thematique': 'Évaluation sommative', 'sae_projet': 'Examen de synthèse d\'anglais 2e secondaire', 'ressources': 'Cahier d\'examen d\'anglais'}
                ]
            }
        }

    with open('curriculum_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print('curriculum_data.json enrichi avec succès !')
    for p_k, p_v in data['parcours'].items():
        total_th = sum(sum(len(m_v['etapes'][e]) for e in ['etape1', 'etape2', 'etape3']) for m_v in p_v['matieres'].values())
        print(f"Parcours {p_k}: {len(p_v['matieres'])} matières, {total_th} thèmes au total.")

if __name__ == '__main__':
    enrich()
