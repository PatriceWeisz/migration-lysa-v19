#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DETECTION DES MODULES STUDIO
============================
Détecte tous les modèles personnalisés créés avec Odoo Studio
"""

import sys
import os

# Forcer affichage
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

def main():
    afficher("="*70)
    afficher("DETECTION DES MODULES STUDIO")
    afficher("="*70)
    
    # Connexion
    afficher("\nConnexion...")
    conn = ConnexionDoubleV19()
    
    if not conn.connecter_tout():
        afficher("ERREUR: Connexion")
        return False
    
    afficher("OK\n")
    
    # 1. Détecter les modèles personnalisés (créés avec Studio)
    afficher("="*70)
    afficher("1. MODELES PERSONNALISES (STUDIO)")
    afficher("="*70)
    
    modeles_custom = conn.executer_source('ir.model', 'search_read',
                                         [('state', '=', 'manual')],
                                         fields=['model', 'name', 'info'])
    
    afficher(f"OK {len(modeles_custom)} modeles personnalises trouves\n")
    
    total_records = 0
    modeles_a_migrer = []
    
    for modele in modeles_custom:
        model_name = modele['model']
        model_label = modele['name']
        
        try:
            # Compter les enregistrements
            count = conn.executer_source(model_name, 'search_count', [])
            afficher(f"  {model_label:40s} ({model_name:30s}) : {count:>6,d} enreg.")
            
            if count > 0:
                modeles_a_migrer.append({
                    'model': model_name,
                    'name': model_label,
                    'count': count
                })
                total_records += count
                
        except Exception as e:
            afficher(f"  {model_label:40s} : ERREUR - {str(e)[:40]}")
    
    # 2. Détecter les champs personnalisés (x_studio_...)
    afficher("\n" + "="*70)
    afficher("2. CHAMPS PERSONNALISES (STUDIO)")
    afficher("="*70)
    
    champs_custom = conn.executer_source('ir.model.fields', 'search_read',
                                        [('state', '=', 'manual'), 
                                         ('name', 'like', 'x_studio_%')],
                                        fields=['model', 'name', 'field_description'])
    
    afficher(f"OK {len(champs_custom)} champs Studio trouves\n")
    
    # Regrouper par modèle
    champs_par_modele = {}
    for champ in champs_custom:
        model = champ['model']
        if model not in champs_par_modele:
            champs_par_modele[model] = []
        champs_par_modele[model].append(champ['name'])
    
    afficher("Modeles avec champs Studio:")
    for model, champs in sorted(champs_par_modele.items()):
        afficher(f"  {model:40s} : {len(champs):>3d} champs Studio")
    
    # 3. Détecter les vues personnalisées Studio
    afficher("\n" + "="*70)
    afficher("3. VUES PERSONNALISEES (STUDIO)")
    afficher("="*70)
    
    vues_custom = conn.executer_source('ir.ui.view', 'search_read',
                                       [('name', 'like', '%Studio%')],
                                       fields=['name', 'model', 'type'])
    
    afficher(f"OK {len(vues_custom)} vues Studio trouvees")
    
    # 4. Résumé
    afficher("\n" + "="*70)
    afficher("RESUME STUDIO")
    afficher("="*70)
    afficher(f"Modeles personnalises     : {len(modeles_a_migrer)}")
    afficher(f"Total enregistrements     : {total_records:,d}")
    afficher(f"Champs Studio             : {len(champs_custom)}")
    afficher(f"Modeles avec champs       : {len(champs_par_modele)}")
    afficher(f"Vues Studio               : {len(vues_custom)}")
    
    if modeles_a_migrer:
        afficher("\n" + "="*70)
        afficher("MODELES A MIGRER")
        afficher("="*70)
        for m in modeles_a_migrer:
            afficher(f"  - {m['name']} ({m['model']}) : {m['count']:,d} enreg.")
    
    # Sauvegarder la liste
    import json
    from pathlib import Path
    
    with open(Path('logs') / 'modules_studio.json', 'w') as f:
        json.dump({
            'modeles': modeles_a_migrer,
            'champs_par_modele': champs_par_modele,
            'total_records': total_records
        }, f, indent=2)
    
    afficher("\n-> Liste sauvegardee dans logs/modules_studio.json")
    afficher("="*70)
    
    return True

if __name__ == "__main__":
    main()

