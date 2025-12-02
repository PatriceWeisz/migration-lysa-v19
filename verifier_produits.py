#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICATION PRODUITS SOURCE vs DESTINATION
===========================================
Compare les produits créés avec les données source
"""

import sys
from connexion_double_v19 import ConnexionDoubleV19

def verifier_produits():
    """Compare les 10 premiers produits source avec destination"""
    print("\n" + "="*70)
    print("VERIFICATION PRODUITS SOURCE vs DESTINATION")
    print("="*70)
    
    conn = ConnexionDoubleV19()
    
    if not conn.connecter_tout():
        print("X Echec de connexion")
        return False
    
    # Récupérer les 10 premiers produits SOURCE
    print("\nRecuperation des produits SOURCE...")
    produits_source = conn.executer_source(
        'product.template',
        'search_read',
        [],
        fields=['name', 'default_code', 'type', 'categ_id', 'list_price', 
               'standard_price', 'sale_ok', 'purchase_ok', 'active'],
        limit=10
    )
    
    print(f"OK {len(produits_source)} produits recuperes de SOURCE")
    
    # Récupérer les produits DESTINATION
    print("\nRecuperation des produits DESTINATION...")
    produits_dest = conn.executer_destination(
        'product.template',
        'search_read',
        [],
        fields=['name', 'default_code', 'type', 'categ_id', 'list_price', 
               'standard_price', 'sale_ok', 'purchase_ok', 'active']
    )
    
    print(f"OK {len(produits_dest)} produits recuperes de DESTINATION")
    
    # Créer un index par nom
    produits_dest_by_name = {p['name']: p for p in produits_dest}
    
    # Comparer chaque produit
    print("\n" + "="*70)
    print("COMPARAISON DETAILLEE")
    print("="*70)
    
    for idx, prod_src in enumerate(produits_source, 1):
        name = prod_src['name']
        print(f"\n[{idx}/10] Produit: {name}")
        print("-" * 70)
        
        # Trouver dans destination
        if name not in produits_dest_by_name:
            print("  ERREUR: Produit introuvable dans destination!")
            continue
        
        prod_dest = produits_dest_by_name[name]
        
        # Comparer les champs
        differences = []
        
        # Nom
        if prod_src['name'] != prod_dest['name']:
            differences.append(f"  - Nom: '{prod_src['name']}' vs '{prod_dest['name']}'")
        
        # Référence
        ref_src = prod_src.get('default_code', '')
        ref_dest = prod_dest.get('default_code', '')
        if ref_src != ref_dest:
            differences.append(f"  - Reference: '{ref_src or 'vide'}' vs '{ref_dest or 'vide'}'")
        
        # Type
        type_src = prod_src.get('type', 'consu')
        type_dest = prod_dest.get('type', 'consu')
        # Type 'product' en source devient 'consu' en destination
        if type_src == 'product':
            type_src_attendu = 'consu'
        else:
            type_src_attendu = type_src
        
        if type_src_attendu != type_dest:
            differences.append(f"  - Type: '{type_src}' (source) -> '{type_src_attendu}' (attendu) vs '{type_dest}' (destination)")
        
        # Catégorie
        categ_src = prod_src.get('categ_id', [False, ''])[1] if prod_src.get('categ_id') else 'Aucune'
        categ_dest = prod_dest.get('categ_id', [False, ''])[1] if prod_dest.get('categ_id') else 'Aucune'
        if categ_src != categ_dest:
            differences.append(f"  - Categorie: '{categ_src}' vs '{categ_dest}'")
        
        # Prix
        list_price_src = prod_src.get('list_price', 0.0)
        list_price_dest = prod_dest.get('list_price', 0.0)
        if abs(list_price_src - list_price_dest) > 0.01:
            differences.append(f"  - Prix vente: {list_price_src} vs {list_price_dest}")
        
        standard_price_src = prod_src.get('standard_price', 0.0)
        standard_price_dest = prod_dest.get('standard_price', 0.0)
        if abs(standard_price_src - standard_price_dest) > 0.01:
            differences.append(f"  - Prix cout: {standard_price_src} vs {standard_price_dest}")
        
        # Flags
        if prod_src.get('sale_ok') != prod_dest.get('sale_ok'):
            differences.append(f"  - Peut etre vendu: {prod_src.get('sale_ok')} vs {prod_dest.get('sale_ok')}")
        
        if prod_src.get('purchase_ok') != prod_dest.get('purchase_ok'):
            differences.append(f"  - Peut etre achete: {prod_src.get('purchase_ok')} vs {prod_dest.get('purchase_ok')}")
        
        if prod_src.get('active') != prod_dest.get('active'):
            differences.append(f"  - Actif: {prod_src.get('active')} vs {prod_dest.get('active')}")
        
        # Afficher le résultat
        if differences:
            print("  ATTENTION: Differences detectees:")
            for diff in differences:
                print(diff)
        else:
            print("  OK: Produit identique (ou equivalents corrects)")
            
        # Afficher les données principales
        print(f"\n  SOURCE:")
        print(f"    - Type: {prod_src.get('type', 'N/A')}")
        print(f"    - Categorie: {categ_src}")
        print(f"    - Prix vente: {list_price_src}")
        print(f"    - Prix cout: {standard_price_src}")
        
        print(f"\n  DESTINATION:")
        print(f"    - Type: {prod_dest.get('type', 'N/A')}")
        print(f"    - Categorie: {categ_dest}")
        print(f"    - Prix vente: {list_price_dest}")
        print(f"    - Prix cout: {standard_price_dest}")
    
    print("\n" + "="*70)
    print("VERIFICATION TERMINEE")
    print("="*70)
    
    return True


if __name__ == "__main__":
    success = verifier_produits()
    sys.exit(0 if success else 1)

