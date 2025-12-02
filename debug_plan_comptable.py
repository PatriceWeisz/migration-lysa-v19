#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE DEBUG PLAN COMPTABLE
==============================
Pour identifier les problèmes de migration du plan comptable
"""

import sys
from connexion_double_v19 import ConnexionDoubleV19

def debug_comptes_source():
    """Debug des comptes source"""
    print("\n" + "=" * 70)
    print("DEBUG: Analyse des comptes SOURCE")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        print("✗ Échec de connexion")
        return False
    
    try:
        # Récupérer 1 compte pour voir la structure
        print("\n1. Récupération d'un compte test...")
        comptes = connexion.executer_source(
            'account.account',
            'search_read',
            [('deprecated', '=', False)],
            fields=[],  # Tous les champs
            limit=1
        )
        
        if comptes:
            print(f"✓ Compte récupéré: {comptes[0].get('code')} - {comptes[0].get('name')}")
            print("\nChamps disponibles:")
            for key, value in comptes[0].items():
                print(f"  - {key:30s}: {value}")
        else:
            print("✗ Aucun compte trouvé")
            return False
        
        # Vérifier le champ account_type
        print("\n" + "=" * 70)
        print("2. Analyse du champ 'account_type'...")
        print("=" * 70)
        
        if 'account_type' in comptes[0]:
            print(f"✓ Champ 'account_type' existe: {comptes[0]['account_type']}")
            print(f"  Type: {type(comptes[0]['account_type'])}")
        elif 'user_type_id' in comptes[0]:
            print(f"✓ Champ 'user_type_id' existe (v16): {comptes[0]['user_type_id']}")
            print(f"  Type: {type(comptes[0]['user_type_id'])}")
            print("⚠️  Attention: Ce champ doit être converti en 'account_type' pour v19")
        else:
            print("✗ Aucun champ de type trouvé!")
        
        # Compter les comptes par type
        print("\n" + "=" * 70)
        print("3. Récupération de 10 comptes pour analyse...")
        print("=" * 70)
        
        comptes_10 = connexion.executer_source(
            'account.account',
            'search_read',
            [('deprecated', '=', False)],
            fields=['code', 'name', 'account_type', 'reconcile'],
            limit=10
        )
        
        print(f"\n✓ {len(comptes_10)} comptes récupérés:")
        for compte in comptes_10:
            code = compte.get('code', '?')
            name = compte.get('name', '?')[:40]
            acc_type = compte.get('account_type', compte.get('user_type_id', 'N/A'))
            print(f"  {code:10s} {name:42s} Type: {acc_type}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


def debug_comptes_destination():
    """Debug des comptes destination pour voir les champs requis"""
    print("\n" + "=" * 70)
    print("DEBUG: Analyse des comptes DESTINATION (v19)")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        print("✗ Échec de connexion")
        return False
    
    try:
        # Récupérer 1 compte existant pour voir la structure
        print("\n1. Récupération d'un compte existant...")
        comptes = connexion.executer_destination(
            'account.account',
            'search_read',
            [],
            fields=[],  # Tous les champs
            limit=1
        )
        
        if comptes:
            print(f"✓ Compte récupéré: {comptes[0].get('code')} - {comptes[0].get('name')}")
            print("\nChamps disponibles en v19:")
            for key, value in comptes[0].items():
                print(f"  - {key:30s}: {value}")
        
        # Récupérer les champs du modèle
        print("\n" + "=" * 70)
        print("2. Champs du modèle account.account en v19...")
        print("=" * 70)
        
        fields_info = connexion.executer_destination(
            'ir.model.fields',
            'search_read',
            [('model', '=', 'account.account'), ('name', 'in', ['code', 'name', 'account_type'])],
            fields=['name', 'field_description', 'required', 'ttype']
        )
        
        print("\nChamps clés:")
        for field in fields_info:
            required = "✓ REQUIS" if field.get('required') else "  optionnel"
            print(f"  {required} - {field['name']:20s} ({field['ttype']:10s}): {field['field_description']}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_creation_compte():
    """Test de création d'un compte simple"""
    print("\n" + "=" * 70)
    print("DEBUG: Test de création d'un compte")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        print("✗ Échec de connexion")
        return False
    
    # Compte de test
    compte_test = {
        'code': 'TEST999999',
        'name': 'Compte Test Migration',
        'account_type': 'asset_current',
    }
    
    print(f"\nTentative de création: {compte_test}")
    
    try:
        # Vérifier s'il existe déjà
        existing = connexion.executer_destination(
            'account.account',
            'search',
            [('code', '=', compte_test['code'])]
        )
        
        if existing:
            print(f"⚠️  Le compte existe déjà (ID: {existing[0]}), suppression...")
            connexion.executer_destination(
                'account.account',
                'unlink',
                existing
            )
            print("✓ Compte test supprimé")
        
        # Créer le compte
        print("\nCréation du compte test...")
        new_id = connexion.executer_destination(
            'account.account',
            'create',
            compte_test
        )
        
        print(f"✓ Compte créé avec succès! ID: {new_id}")
        
        # Nettoyer
        print("\nNettoyage...")
        connexion.executer_destination(
            'account.account',
            'unlink',
            [new_id]
        )
        print("✓ Compte test supprimé")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERREUR lors de la création: {e}")
        print("\nDétails de l'erreur:")
        import traceback
        traceback.print_exc()
        
        # Analyser l'erreur
        error_str = str(e)
        if 'required' in error_str.lower():
            print("\n⚠️  Champs requis manquants détectés!")
        if 'account_type' in error_str.lower():
            print("⚠️  Problème avec le champ 'account_type'")
        
        return False


def main():
    """Fonction principale de debug"""
    print("\n" + "█" * 70)
    print("  SCRIPT DE DEBUG - MIGRATION PLAN COMPTABLE")
    print("█" * 70)
    
    tests = [
        ("Analyse comptes SOURCE", debug_comptes_source),
        ("Analyse comptes DESTINATION", debug_comptes_destination),
        ("Test création compte", test_creation_compte),
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

