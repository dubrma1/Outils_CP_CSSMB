/**
 * Base de données des métiers semi-spécialisés (PFAE - FPT / FMS)
 * Centre de services scolaire Marguerite-Bourgeoys / MEQ
 * Conforme au format de la grille d'observation
 */

const METIERS_PFAE = {
  "aide-concierge": {
    nom: "Aide-concierge",
    code: "8332 / M332",
    secteur: "07 - Bâtiment et travaux publics",
    centre: "Centre de services scolaire Marguerite-Bourgeoys",
    sousTitre: "Outil de reconnaissance des compétences et de suivi de l’évolution professionnelle à partir du plan de formation fourni.",
    echelle: "1 = À développer | 2 = En progression | 3 = Atteint | 4 = Dépasse les attentes",
    competences: [
      {
        id: "comp-501",
        code: "501",
        titre: "Nettoyer les aires publiques",
        complexite: "2",
        taches: [
          "Replacer les tables, fauteuils, chaises et présentoirs.",
          "Épousseter le mobilier et les cadres.",
          "Passer l’aspirateur ou balayer les planchers.",
          "Passer la vadrouille ou la serpillière.",
          "Laver vitres et miroirs.",
          "Laver les rampes et mains courantes.",
          "Essuyer comptoirs, portes et poignées.",
          "Enlever les taches sur plinthes et murs.",
          "Astiquer les accessoires métalliques.",
          "Vider les poubelles et bacs.",
          "Remettre les objets perdus au service approprié.",
          "Signaler les problèmes observés."
        ],
        criteres: [
          "Respect des règles SST",
          "Respect des règles d’hygiène",
          "Respect des directives",
          "Application correcte des techniques",
          "Utilisation appropriée de l’équipement et des produits",
          "Ordre et propreté"
        ]
      },
      {
        id: "comp-503",
        code: "503",
        titre: "Gestion des matières résiduelles",
        complexite: "2",
        taches: [
          "Transporter les sacs poubelles au conteneur.",
          "Vider les bacs de récupération.",
          "Transvider et transporter les matières compostables.",
          "Déposer les résidus domestiques dangereux au bon endroit.",
          "Laver les bacs."
        ],
        criteres: [
          "Respect des règles SST",
          "Respect des règles d’hygiène",
          "Respect des directives",
          "Respect des lois environnementales",
          "Application correcte des techniques",
          "Souci de la protection de l’environnement"
        ]
      },
      {
        id: "comp-833203",
        code: "833203",
        titre: "Répondre à la clientèle",
        complexite: "2",
        taches: [
          "Saluer les personnes.",
          "Répondre aux questions.",
          "Transmettre les messages.",
          "Signaler les problèmes observés."
        ],
        criteres: [
          "Service courtois",
          "Pertinence, exactitude et clarté de l'information",
          "Souci de la satisfaction de la clientèle"
        ]
      }
    ]
  },

  "aide-cuisinier": {
    nom: "Aide-cuisinier",
    code: "8312 / M312",
    secteur: "03 - Alimentation et tourisme",
    centre: "Centre de services scolaire Marguerite-Bourgeoys",
    sousTitre: "Outil de reconnaissance des compétences et de suivi de l’évolution professionnelle à partir du plan de formation fourni.",
    echelle: "1 = À développer | 2 = En progression | 3 = Atteint | 4 = Dépasse les attentes",
    competences: [
      {
        id: "comp-831201",
        code: "831201",
        titre: "Préparer le poste de travail et les matières premières",
        complexite: "2",
        taches: [
          "Laver et désinfecter le plan de travail et les planches à découper.",
          "Revêtir la tenue de travail complète (tablier, filet, chaussures fermées).",
          "Sélectionner et rassembler les ustensiles nécessaires à la tâche.",
          "Sortir les denrées requises de la chambre froide ou de la réserve.",
          "Vérifier la fraîcheur des ingrédients avant utilisation."
        ],
        criteres: [
          "Respect rigoureux des règles d’hygiène et salubrité (MAPAQ)",
          "Respect des règles de santé et de sécurité du travail (SST)",
          "Respect des directives du chef d’équipe",
          "Ordre et propreté du poste de travail"
        ]
      },
      {
        id: "comp-831202",
        code: "831202",
        titre: "Laver, éplucher et tailler les fruits et légumes",
        complexite: "2",
        taches: [
          "Laver soigneusement les fruits et légumes à l'eau claire.",
          "Éplucher les légumes racines avec l'économe.",
          "Couper et trancher selon les consignes (dés, julienne, rondelles).",
          "Déposer les denrées taillées dans des bacs hermétiques étiquetés.",
          "Éliminer les retailles et résidus au compostage."
        ],
        criteres: [
          "Maniement sécuritaire des couteaux et outils tranchants",
          "Régularité des coupes et respect des calibres demandés",
          "Application des bonnes techniques d'épluchage et de découpe",
          "Minimisation du gaspillage alimentaire"
        ]
      },
      {
        id: "comp-831203",
        code: "831203",
        titre: "Assurer la plonge et le nettoyage de la batterie de cuisine",
        complexite: "2",
        taches: [
          "Râcler et débarrasser les restes alimentaires dans les poubelles.",
          "Remplir et doser les bacs de lavage, rinçage et assainissement.",
          "Frotter et dégraisser les casseroles et chaudrons.",
          "Charger et actionner la machine à laver la vaisselle.",
          "Ranger la vaisselle sèche aux endroits désignés."
        ],
        criteres: [
          "Utilisation sécuritaire des détergents et produits chimiques",
          "Propreté impeccable et absence de résidus graisseux",
          "Respect des températures de lavage et d'assainissement",
          "Cadence régulière et méthode organisée"
        ]
      }
    ]
  },

  "commis-epicerie": {
    nom: "Commis d'épicerie / Magasinier",
    code: "8321 / M321",
    secteur: "02 - Commerce et administration",
    centre: "Centre de services scolaire Marguerite-Bourgeoys",
    sousTitre: "Outil de reconnaissance des compétences et de suivi de l’évolution professionnelle à partir du plan de formation fourni.",
    echelle: "1 = À développer | 2 = En progression | 3 = Atteint | 4 = Dépasse les attentes",
    competences: [
      {
        id: "comp-832101",
        code: "832101",
        titre: "Réceptionner et déballer la marchandise",
        complexite: "2",
        taches: [
          "Vérifier l’état extérieur des boîtes et des palettes livrées.",
          "Découper les rubans adhésifs et emballages à l'aide d'un couteau de sécurité rétractable.",
          "Trier les articles par allée et par rayon.",
          "Transporter les marchandises sur les chariots de manutention.",
          "Déposer les boîtes vides dans le compacteur à carton."
        ],
        criteres: [
          "Application des principes ergonomiques de manutention de charges (SST)",
          "Utilisation sécuritaire du couteau à déballer",
          "Respect de l'intégrité de la marchandise (zéro bris)",
          "Respect des directives d'entreposage"
        ]
      },
      {
        id: "comp-832102",
        code: "832102",
        titre: "Garnir les étalages et effectuer la rotation des produits",
        complexite: "2",
        taches: [
          "Appliquer le principe de rotation PEPS (premier entré, premier sorti).",
          "Placer les nouveaux articles derrière les plus anciens.",
          "Aligner les étiquettes et logos vers l'avant (façonnage / facing).",
          "Vérifier la concordance du code de produit avec l'étiquette de prix.",
          "Retirer les produits périmés ou abîmés de la vente."
        ],
        criteres: [
          "Rigueur dans la vérification des dates de péremption",
          "Esthétique et régularité du façonnage des tablettes",
          "Exactitude de la disposition des produits selon le planogramme",
          "Maintien d'un espace de circulation dégagé pour les clients"
        ]
      },
      {
        id: "comp-832103",
        code: "832103",
        titre: "Entretenir la propreté des allées et renseigner les clients",
        complexite: "2",
        taches: [
          "Balayer et nettoyer les allées en cas de déversement ou bris.",
          "Placer immédiatement une affiche d'avertissement de plancher mouillé.",
          "Saluer poliment les clients qui circulent dans le rayon.",
          "Orienter un client vers le bon rayon ou appeler un commis spécialisé."
        ],
        criteres: [
          "Réactivité immédiate face aux risques de chute ou déversement",
          "Attitude courtoise et professionnelle avec la clientèle",
          "Clarté des indications fournies",
          "Maintien de la propreté générale de l'environnement"
        ]
      }
    ]
  },

  "entretien-paysager": {
    nom: "Préposé à l'entretien paysager et horticole",
    code: "8342 / M342",
    secteur: "01 - Agriculture et pêches",
    centre: "Centre de services scolaire Marguerite-Bourgeoys",
    sousTitre: "Outil de reconnaissance des compétences et de suivi de l’évolution professionnelle à partir du plan de formation fourni.",
    echelle: "1 = À développer | 2 = En progression | 3 = Atteint | 4 = Dépasse les attentes",
    competences: [
      {
        id: "comp-834201",
        code: "834201",
        titre: "Entretenir les pelouses et les surfaces gazonnées",
        complexite: "2",
        taches: [
          "Inspecter le terrain et ramasser les débris (branches, pierres, déchets).",
          "Enfiler les ÉPI appropriés (lunettes, protecteurs auditifs, bottes de sécurité).",
          "Tondre la pelouse en suivant des bandes rectilignes régulières.",
          "Passer le coupe-bordure le long des trottoirs, clôtures et murets.",
          "Râteler et souffler les résidus de tonte pour libérer les passages piétons."
        ],
        criteres: [
          "Respect scrupuleux des consignes SST avec les équipements motorisés",
          "Régularité de la hauteur de coupe",
          "Précision du découpage des bordures",
          "Nettoyage complet des zones asphaltées ou pavées"
        ]
      },
      {
        id: "comp-834202",
        code: "834202",
        titre: "Entretenir les massifs fleuris et arbustes",
        complexite: "2",
        taches: [
          "Arracher manuellement les mauvaises herbes avec leur système racinaire.",
          "Biner la terre autour des végétaux pour aérer le sol.",
          "Tailler les fleurs fanées et les tiges sèches à l'aide d'un sécateur.",
          "Épandre du paillis de manière uniforme au pied des massifs.",
          "Arroser les plantations en respectant les besoins en eau indiqués."
        ],
        criteres: [
          "Identification correcte des végétaux et des mauvaises herbes",
          "Maniement soigné et sécuritaire des outils de coupe (sécateur)",
          "Protection de l'intégrité des racines et des plants sains",
          "Dosage adéquat de l'arrosage sans gaspillage"
        ]
      }
    ]
  }
};
