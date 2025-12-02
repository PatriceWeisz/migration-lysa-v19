#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG MIGRATION PARTENAIRES
===========================
Script pour identifier les problèmes de migration des partenaires
"""

import sys
from connexion_double_v19 import ConnexionDoubleV19

def test_creation_partenaire_simple():
    """Test de création d'un partenaire simple"""
    print("\n" + "=" * 70)
    print("TEST: Création d'un partenaire simple")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        print("✗ Échec de connexion")
        return False
    
    # Partenaire test minimal
    partenaire_test = {
        'name': 'Test Migration Partenaire',
    }
    
    print(f"\nTentative de création: {partenaire_test}")
    
    try:
        # Vérifier s'il existe déjà
        existing = connexion.executer_destination(
            'res.partner',
            'search',
            [('name', '=', partenaire_test['name'])]
        )
        
        if existing:
            print(f"⚠️  Le partenaire existe déjà (ID: {existing[0]}), suppression...")
            connexion.executer_destination(
                'res.partner',
                'unlink',
                existing
            )
            print("✓ Partenaire test supprimé")
        
        # Créer le partenaire
        print("\nCréation du partenaire test...")
        new_id = connexion.executer_destination(
            'res.partner',
            'create',
            partenaire_test
        )
        
        print(f"✓ Partenaire créé avec succès! ID: {new_id}")
        
        # Nettoyer
        print("\nNettoyage...")
        connexion.executer_destination(
            'res.partner',
            'unlink',
            [new_id]
        )
        print("✓ Partenaire test supprimé")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERREUR lors de la création: {e}")
        print("\nDétails de l'erreur:")
        import traceback
        traceback.print_exc()
        return False


def analyser_partenaire_problematique():
    """Analyse un partenaire qui pose problème"""
    print("\n" + "=" * 70)
    print("ANALYSE: Partenaires sans nom dans la source")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        print("✗ Échec de connexion")
        return False
    
    try:
        # Chercher les partenaires sans nom ou avec name=False
        print("\n1. Recherche des partenaires problématiques...")
        
        partenaires_sans_nom = connexion.executer_source(
            'res.partner',
            'search_read',
            [('name', '=', False)],
            fields=['id', 'name', 'email', 'phone', 'ref', 'vat'],
            limit=5
        )
        
        if partenaires_sans_nom:
            print(f"\n✓ {len(partenaires_sans_nom)} partenaire(s) sans nom trouvé(s):\n")
            for p in partenaires_sans_nom:
                print(f"  ID: {p['id']}")
                print(f"  Name: {p.get('name')}")
                print(f"  Email: {p.get('email')}")
                print(f"  Phone: {p.get('phone')}")
                print(f"  Ref: {p.get('ref')}")
                print(f"  VAT: {p.get('vat')}")
                print()
        else:
            print("✓ Aucun partenaire sans nom trouvé")
        
        # Chercher les partenaires avec noms vides
        print("2. Recherche des partenaires avec nom vide...")
        
        all_partners = connexion.executer_source(
            'res.partner',
            'search_read',
            [],
            fields=['id', 'name'],
            limit=100
        )
        
        empty_names = [p for p in all_partners if not p.get('name') or str(p.get('name')).strip() == '']
        
        if empty_names:
            print(f"\n⚠️  {len(empty_names)} partenaire(s) avec nom vide dans l'échantillon")
        else:
            print("✓ Tous les partenaires ont un nom dans l'échantillon")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_champs_destination():
    """Teste les champs requis pour la destination"""
    print("\n" + "=" * 70)
    print("ANALYSE: Champs requis pour res.partner en v19")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        print("✗ Échec de connexion")
        return False
    
    try:
        # Récupérer les champs requis du modèle
        fields_info = connexion.executer_destination(
            'ir.model.fields',
            'search_read',
            [('model', '=', 'res.partner'), ('required', '=', True)],
            fields=['name', 'field_description', 'ttype']
        )
        
        print("\nChamps REQUIS pour res.partner en v19:\n")
        for field in fields_info:
            print(f"  ✓ {field['name']:20s} ({field['ttype']:10s}): {field['field_description']}")
        
        # Récupérer un partenaire existant pour voir la structure
        print("\n" + "=" * 70)
        print("Structure d'un partenaire existant en v19:")
        print("=" * 70)
        
        existing = connexion.executer_destination(
            'res.partner',
            'search_read',
            [],
            fields=[],
            limit=1
        )
        
        if existing:
            print(f"\nPartenaire: {existing[0].get('name')}")
            print("\nChamps présents:")
            for key, value in existing[0].items():
                if value and value != False:
                    print(f"  - {key:30s}: {str(value)[:50]}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale de debug"""
    print("\n" + "█" * 70)
    print("  SCRIPT DE DEBUG - MIGRATION PARTENAIRES")
    print("█" * 70)
    
    tests = [
        ("Création partenaire simple", test_creation_partenaire_simple),
        ("Analyse partenaires problématiques", analyser_partenaire_problematique),
        ("Champs requis destination", test_champs_destination),
    ]
    
    for name, test_func in tests:
        print(f"\n{'=' * 70}")
        print(f"▶ {name}")
        print("=" * 70)
        
        try:
            test_func()
        except Exception as e:
            print(f"\n✗ Erreur: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("FIN DU DEBUG")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

