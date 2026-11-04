import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_concierge_evaluation_grid():
    doc = Document()
    
    # Page setup
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # Helper to set cell shading
    def set_cell_shading(cell, color_hex):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shading)
        
    # Helper for cell margins
    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{margin_name}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    # Document Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title_p.add_run("GRILLE D'OBSERVATION ET D'ÉVALUATION DES COMPÉTENCES\nProgramme : Aide-concierge (8332 / M332)")
    run_title.font.name = 'Calibri'
    run_title.font.size = Pt(16)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(31, 78, 121) # Navy
    
    # Subtitle / Metadata box
    meta_p = doc.add_paragraph()
    meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_meta = meta_p.add_run("Secteur : 07 - Bâtiment et travaux publics | Centre de services scolaire Marguerite-Bourgeoys")
    run_meta.font.name = 'Calibri'
    run_meta.font.size = Pt(10)
    run_meta.font.italic = True
    run_meta.font.color.rgb = RGBColor(89, 89, 89)
    
    doc.add_paragraph() # spacing

    # Instructions box
    p_inst = doc.add_paragraph()
    run_inst = p_inst.add_run("Instructions : Cette grille permet d'observer, de consigner et de reconnaître les progrès et les compétences de l'élève ou de l'employé en situation de travail. Utilisez l'échelle d'évaluation pour chaque critère et tâche.")
    run_inst.font.name = 'Calibri'
    run_inst.font.size = Pt(10.5)
    run_inst.font.italic = True
    
    # Scale explanation
    scale_table = doc.add_table(rows=1, cols=4)
    scale_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    scale_headers = ["1 - Non acquis (NA)", "2 - En acquisition (EA)", "3 - Acquis (A)", "4 - Maîtrisé / Autonome (M)"]
    hdr_cells = scale_table.rows[0].cells
    for i, title in enumerate(scale_headers):
        hdr_cells[i].text = title
        set_cell_shading(hdr_cells[i], "F2F2F2")
        set_cell_margins(hdr_cells[i], 80, 80, 100, 100)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.name = 'Calibri'
            run.font.size = Pt(9.5)
            run.font.bold = True
            
    doc.add_paragraph()

    competencies = [
        {
            "code": "501",
            "title": "Nettoyer les aires publiques (halls d'entrée, corridors, ascenseurs, escaliers, etc.)",
            "complexity": "2",
            "criteres": [
                "Respect des règles de santé et de sécurité au travail.",
                "Respect des règles d'hygiène ou de salubrité.",
                "Respect des directives de travail.",
                "Application correcte des techniques de travail.",
                "Utilisation appropriée de l'équipement et des produits de nettoyage.",
                "Ordre et propreté."
            ],
            "taches": [
                "Replacer les tables, les fauteuils, les chaises, les présentoirs à revues, etc.",
                "Épousseter le mobilier et les cadres ou les affiches sur les murs.",
                "Passer l'aspirateur ou balayer les planchers.",
                "Passer une vadrouille ou une serpillière sur les planchers et dans les escaliers.",
                "Laver les vitres ou les miroirs.",
                "Laver les rampes ou les mains courantes.",
                "Essuyer les comptoirs, les portes, les cadres de portes et les poignées.",
                "Enlever les taches sur les plinthes et les murs.",
                "Astiquer les accessoires et les garnitures de métal.",
                "Vider les poubelles et les bacs de récupération.",
                "Porter les objets perdus à la réception, au service à la clientèle, à la sécurité, etc.",
                "Détecter des problèmes divers (bris, dysfonctionnement d'un équipement, disparition d'un objet, etc.), et en informer la personne responsable."
            ]
        },
        {
            "code": "503",
            "title": "Exécuter des tâches prescrites dans le cadre de la gestion des matières résiduelles",
            "complexity": "2",
            "criteres": [
                "Respect des règles de santé et de sécurité au travail.",
                "Respect des règles d'hygiène ou de salubrité.",
                "Respect des directives de travail.",
                "Respect des lois et des règlements relatifs à l'environnement.",
                "Application correcte des techniques de travail.",
                "Souci de la protection de l'environnement."
            ],
            "taches": [
                "Transporter les sacs poubelles et les déposer dans un conteneur à déchets.",
                "Transporter les bacs de récupération et les vider dans un conteneur.",
                "Transvider les bacs de matières compostables dans un autre bac plus volumineux, les transporter et les déposer à l'endroit de collecte.",
                "Déposer tout résidu domestique dangereux dans un endroit prévu à cet effet.",
                "Laver les bacs."
            ]
        },
        {
            "code": "833203",
            "title": "Répondre à la clientèle de l'immeuble d'habitation ou de l'établissement",
            "complexity": "2",
            "criteres": [
                "Service courtois.",
                "Pertinence, exactitude et clarté de l'information transmise.",
                "Souci de la satisfaction de la clientèle."
            ],
            "taches": [
                "Saluer les personnes.",
                "Répondre aux questions.",
                "Transmettre des messages à la personne responsable.",
                "Détecter des problèmes divers (bris, dysfonctionnement d'un équipement, disparition d'un objet, etc.), et en informer la personne responsable."
            ]
        }
    ]

    for comp in competencies:
        # Competency Header Heading
        h = doc.add_paragraph()
        run_h = h.add_run(f"Compétence {comp['code']} : {comp['title']} (Complexité : {comp['complexity']})")
        run_h.font.name = 'Calibri'
        run_h.font.size = Pt(13)
        run_h.font.bold = True
        run_h.font.color.rgb = RGBColor(46, 117, 182) # Accent Blue
        
        # 1. Criteria Table
        p_crit = doc.add_paragraph()
        r_c = p_crit.add_run("Critères de performance évalués :")
        r_c.font.name = 'Calibri'
        r_c.font.size = Pt(11)
        r_c.font.bold = True
        
        table_crit = doc.add_table(rows=len(comp['criteres']) + 1, cols=3)
        table_crit.alignment = WD_TABLE_ALIGNMENT.CENTER
        table_crit.autofit = False
        
        col_widths_crit = [Inches(4.5), Inches(1.0), Inches(1.0)]
        headers_crit = ["Critères de performance", "Évaluation (1-4)", "Commentaires / Observations"]
        
        for i, h_text in enumerate(headers_crit):
            cell = table_crit.cell(0, i)
            cell.text = h_text
            set_cell_shading(cell, "2F5597") # Dark Navy Blue
            set_cell_margins(cell, 120, 120, 150, 150)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i > 0 else WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(10)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                
        for row_idx, crit in enumerate(comp['criteres'], start=1):
            row_cells = table_crit.rows[row_idx].cells
            row_cells[0].text = f"• {crit}"
            row_cells[1].text = ""
            row_cells[2].text = ""
            
            for i, cell in enumerate(row_cells):
                set_cell_margins(cell, 100, 100, 120, 120)
                if row_idx % 2 == 1:
                    set_cell_shading(cell, "F9FBFD")
                p = cell.paragraphs[0]
                for run in p.runs:
                    run.font.name = 'Calibri'
                    run.font.size = Pt(9.5)
                    
        for i, row in enumerate(table_crit.rows):
            if i == 0: continue
            for j, w in enumerate(col_widths_crit):
                row.cells[j].width = w

        doc.add_paragraph() # Spacing

        # 2. Tasks Table
        p_tache = doc.add_paragraph()
        r_t = p_tache.add_run("Observation des tâches à réaliser :")
        r_t.font.name = 'Calibri'
        r_t.font.size = Pt(11)
        r_t.font.bold = True
        
        table_tache = doc.add_table(rows=len(comp['taches']) + 1, cols=3)
        table_tache.alignment = WD_TABLE_ALIGNMENT.CENTER
        table_tache.autofit = False
        
        headers_tache = ["Tâches et opérations", "Évaluation (1-4)", "Commentaires / Observations"]
        col_widths_tache = [Inches(4.5), Inches(1.0), Inches(1.0)]
        
        for i, h_text in enumerate(headers_tache):
            cell = table_tache.cell(0, i)
            cell.text = h_text
            set_cell_shading(cell, "1F4E78") # Professional Blue
            set_cell_margins(cell, 120, 120, 150, 150)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i > 0 else WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(10)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                
        for row_idx, tache in enumerate(comp['taches'], start=1):
            row_cells = table_tache.rows[row_idx].cells
            row_cells[0].text = f"• {tache}"
            row_cells[1].text = ""
            row_cells[2].text = ""
            
            for i, cell in enumerate(row_cells):
                set_cell_margins(cell, 100, 100, 120, 120)
                if row_idx % 2 == 1:
                    set_cell_shading(cell, "F9FBFD")
                p = cell.paragraphs[0]
                for run in p.runs:
                    run.font.name = 'Calibri'
                    run.font.size = Pt(9.5)
                    
        for i, row in enumerate(table_tache.rows):
            if i == 0: continue
            for j, w in enumerate(col_widths_tache):
                row.cells[j].width = w

        doc.add_page_break()

    # Final Summary / Validation Section
    h_sum = doc.add_paragraph()
    r_sum = h_sum.add_run("Bilan et Suivi de l'Évolution des Compétences")
    r_sum.font.name = 'Calibri'
    r_sum.font.size = Pt(14)
    r_sum.font.bold = True
    r_sum.font.color.rgb = RGBColor(31, 78, 121)
    
    p_sum_desc = doc.add_paragraph()
    r_sum_desc = p_sum_desc.add_run("Ce bilan synthétise l'évolution de l'apprenant(e) ou de l'employé(e) et consigne les ententes de suivi pour favoriser le perfectionnement continu.")
    r_sum_desc.font.name = 'Calibri'
    r_sum_desc.font.size = Pt(10.5)
    
    table_sum = doc.add_table(rows=5, cols=2)
    table_sum.alignment = WD_TABLE_ALIGNMENT.CENTER
    sum_data = [
        ("Nom de l'élève / employé(e) :", ""),
        ("Nom de l'évaluateur / accompagnateur :", ""),
        ("Date de l'évaluation / suivi :", ""),
        ("Commentaires généraux et plans d'action :", ""),
        ("Signature de l'intervenant / formateur :                          ", "Signature de l'élève / employé(e) :")
    ]
    
    for row_idx, (label, val) in enumerate(sum_data):
        row_cells = table_sum.rows[row_idx].cells
        row_cells[0].text = label
        row_cells[1].text = val
        for i, cell in enumerate(row_cells):
            set_cell_margins(cell, 140, 140, 150, 150)
            set_cell_shading(cell, "F2F2F2" if row_idx % 2 == 0 else "FFFFFF")
            p = cell.paragraphs[0]
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(10)
                run.font.bold = (i == 0 or row_idx == 4)

    file_path = "Grille_Observation_Aide_Concierge.docx"
    doc.save(file_path)
    print(f"Document saved successfully as {file_path}")

create_concierge_evaluation_grid()