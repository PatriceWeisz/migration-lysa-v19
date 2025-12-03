#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICATION EMPLOYES SOURCE vs DESTINATION
===========================================
Compare les employés créés avec les données source
"""

import sys
from connexion_double_v19 import ConnexionDoubleV19

def verifier_employes():
    """Compare les 5 premiers employés source avec destination"""
    print("\n" + "="*70)
    print("VERIFICATION EMPLOYES SOURCE vs DESTINATION")
    print("="*70)
    
    conn = ConnexionDoubleV19()
    
    if not conn.connecter_tout():
        print("X Echec de connexion")
        return False
    
    # Récupérer les 5 premiers employés SOURCE avec TOUS les champs
    print("\nRecuperation des employes SOURCE (tous les champs)...")
    employes_source = conn.executer_source(
        'hr.employee',
        'search_read',
        [],
        fields=[],  # Tous les champs
        limit=5
    )
    
    print(f"OK {len(employes_source)} employes recuperes de SOURCE")
    
    # Afficher TOUS les champs disponibles du premier employé
    if employes_source:
        print("\n" + "="*70)
        print(f"CHAMPS DISPONIBLES DANS SOURCE (exemple: {employes_source[0]['name']})")
        print("="*70)
        for key in sorted(employes_source[0].keys()):
            value = employes_source[0][key]
            if value and value != False:
                print(f"  - {key}: {value}")
    
    # Récupérer les employés DESTINATION
    print("\n" + "="*70)
    print("Recuperation des employes DESTINATION...")
    employes_dest = conn.executer_destination(
        'hr.employee',
        'search_read',
        [],
        fields=[]  # Tous les champs
    )
    
    print(f"OK {len(employes_dest)} employes recuperes de DESTINATION")
    
    # Créer un index par nom
    employes_dest_by_name = {e['name']: e for e in employes_dest}
    
    # Comparer chaque employé
    print("\n" + "="*70)
    print("COMPARAISON DETAILLEE")
    print("="*70)
    
    for idx, emp_src in enumerate(employes_source, 1):
        name = emp_src['name']
        print(f"\n[{idx}/5] Employe: {name}")
        print("-" * 70)
        
        # Trouver dans destination
        if name not in employes_dest_by_name:
            print("  ERREUR: Employe introuvable dans destination!")
            continue
        
        emp_dest = employes_dest_by_name[name]
        
        # Comparer les champs importants
        champs_importants = [
            'name', 'work_email', 'work_phone', 'mobile_phone',
            'job_title', 'department_id', 'parent_id', 'user_id',
            'address_id', 'active', 'coach_id', 'work_location_id',
            'resource_calendar_id', 'tz', 'job_id', 'address_home_id',
            'country_id', 'gender', 'marital', 'birthday', 'place_of_birth',
            'country_of_birth', 'certificate', 'study_field', 'study_school',
            'emergency_contact', 'emergency_phone', 'visa_no', 'permit_no',
            'visa_expire', 'work_permit_expiration_date', 'identification_id',
            'passport_id', 'bank_account_id', 'km_home_work'
        ]
        
        differences = []
        champs_presents_source = []
        champs_absents_dest = []
        
        for champ in champs_importants:
            if champ in emp_src and emp_src[champ] and emp_src[champ] != False:
                champs_presents_source.append(champ)
                
                if champ in emp_dest:
                    val_src = emp_src[champ]
                    val_dest = emp_dest[champ]
                    
                    # Comparer les valeurs
                    if val_src != val_dest:
                        differences.append(f"    - {champ}: SOURCE={val_src} vs DEST={val_dest}")
                else:
                    champs_absents_dest.append(champ)
        
        # Afficher le résultat
        print(f"  SOURCE: {len(champs_presents_source)} champs remplis")
        print(f"  DESTINATION: {len(champs_presents_source) - len(champs_absents_dest)} champs migres")
        
        if champs_absents_dest:
            print(f"\n  ATTENTION: {len(champs_absents_dest)} champ(s) NON migre(s):")
            for champ in champs_absents_dest:
                print(f"    - {champ}: {emp_src[champ]}")
        
        if differences:
            print(f"\n  ATTENTION: {len(differences)} difference(s):")
            for diff in differences:
                print(diff)
        
        if not champs_absents_dest and not differences:
            print("  OK: Employe identique")
    
    print("\n" + "="*70)
    print("VERIFICATION TERMINEE")
    print("="*70)
    
    return True


if __name__ == "__main__":
    success = verifier_employes()
    sys.exit(0 if success else 1)

