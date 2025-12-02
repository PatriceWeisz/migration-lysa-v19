#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTS MIGRATION PLAN COMPTABLE
==============================
Tests unitaires de la migration du plan comptable
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connexion_double_v19 import ConnexionDoubleV19
from migration_plan_comptable import MigrationPlanComptable
from config_v19 import MIGRATION_PARAMS


def test_connexion_et_comptage():
    """Test de connexion et comptage des comptes"""
    print("\n" + "=" * 70)
    print("TEST CONNEXION ET COMPTAGE COMPTES")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        print("✗ Échec de connexion")
        return False
    
    migration = MigrationPlanComptable(connexion)
    migration.compter_comptes()
    
    assert migration.stats['total_source'] > 0, "Aucun compte dans la source"
    
    print(f"✓ {migration.stats['total_source']} comptes trouvés dans la source")
    print(f"✓ {migration.stats['total_dest_avant']} comptes dans la destination")
    
    return True


def test_recuperation_comptes():
    """Test de récupération des comptes source"""
    print("\n" + "=" * 70)
    print("TEST RÉCUPÉRATION COMPTES SOURCE")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    connexion.connecter_tout()
    
    migration = MigrationPlanComptable(connexion)
    comptes = migration.recuperer_comptes_source(limit=10)
    
    assert len(comptes) > 0, "Aucun compte récupéré"
    assert 'code' in comptes[0], "Champ 'code' manquant"
    assert 'name' in comptes[0], "Champ 'name' manquant"
    
    print(f"✓ {len(comptes)} comptes récupérés")
    print(f"\nExemple de compte:")
    print(f"  Code: {comptes[0].get('code')}")
    print(f"  Nom: {comptes[0].get('name')}")
    print(f"  Type: {comptes[0].get('account_type')}")
    
    return True


def test_mapper_account_type():
    """Test du mapping des types de comptes"""
    print("\n" + "=" * 70)
    print("TEST MAPPING TYPES DE COMPTES")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    migration = MigrationPlanComptable(connexion)
    
    # Test différents types
    types_test = [
        ('asset_receivable', 'asset_receivable'),
        ('asset_current', 'asset_current'),
        ('liability_payable', 'liability_payable'),
        ('income', 'income'),
        ('expense', 'expense'),
    ]
    
    for source_type, expected in types_test:
        result = migration.mapper_account_type(source_type)
        assert result == expected, f"Mapping incorrect pour {source_type}"
        print(f"✓ {source_type} → {result}")
    
    print("✓ Tous les mappings sont corrects")
    return True


def test_preparer_donnees():
    """Test de préparation des données"""
    print("\n" + "=" * 70)
    print("TEST PRÉPARATION DONNÉES")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    migration = MigrationPlanComptable(connexion)
    
    # Compte test
    compte_test = {
        'id': 1,
        'code': '411000',
        'name': 'Clients',
        'account_type': 'asset_receivable',
        'reconcile': True,
        'deprecated': False,
    }
    
    data = migration.preparer_donnees(compte_test)
    
    assert 'code' in data, "Champ 'code' manquant"
    assert 'name' in data, "Champ 'name' manquant"
    assert 'account_type' in data, "Champ 'account_type' manquant"
    assert data['code'] == '411000', "Code incorrect"
    
    print(f"✓ Données préparées:")
    for key, value in data.items():
        print(f"  - {key}: {value}")
    
    return True


def test_migration_simulation():
    """Test de migration en mode simulation"""
    print("\n" + "=" * 70)
    print("TEST MIGRATION EN MODE SIMULATION")
    print("=" * 70)
    
    # Activer le mode simulation temporairement
    mode_original = MIGRATION_PARAMS.get('MODE_SIMULATION', False)
    MIGRATION_PARAMS['MODE_SIMULATION'] = True
    
    try:
        connexion = ConnexionDoubleV19()
        
        if not connexion.connecter_tout():
            print("✗ Échec de connexion")
            return False
        
        migration = MigrationPlanComptable(connexion)
        
        # Migration de seulement 5 comptes en simulation
        success = migration.executer(limit=5)
        
        print(f"\n✓ Mode simulation:")
        print(f"  - Migrés (simulation): {migration.stats['migres']}")
        print(f"  - Ignorés: {migration.stats['ignores']}")
        print(f"  - Erreurs: {migration.stats['erreurs']}")
        
        return success
        
    finally:
        # Restaurer le mode original
        MIGRATION_PARAMS['MODE_SIMULATION'] = mode_original


def test_verifier_existence():
    """Test de vérification d'existence"""
    print("\n" + "=" * 70)
    print("TEST VÉRIFICATION EXISTENCE")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        print("✗ Échec de connexion")
        return False
    
    migration = MigrationPlanComptable(connexion)
    
    # Récupérer un compte existant dans la destination
    comptes_dest = connexion.executer_destination(
        'account.account',
        'search_read',
        [],
        fields=['code', 'name'],
        limit=1
    )
    
    if comptes_dest:
        compte_test = comptes_dest[0]
        existing_id = migration.verifier_existence(compte_test)
        
        assert existing_id is not None, "Compte existant non trouvé"
        print(f"✓ Compte '{compte_test['code']}' trouvé (ID: {existing_id})")
    else:
        print("⚠️  Aucun compte dans la destination pour tester")
    
    return True


def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "█" * 70)
    print("  SUITE DE TESTS - MIGRATION PLAN COMPTABLE")
    print("█" * 70)
    
    tests = [
        ("Connexion et comptage", test_connexion_et_comptage),
        ("Récupération comptes", test_recuperation_comptes),
        ("Mapping types", test_mapper_account_type),
        ("Préparation données", test_preparer_donnees),
        ("Vérification existence", test_verifier_existence),
        ("Migration simulation", test_migration_simulation),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            print(f"\n▶ Test: {name}")
            result = test_func()
            results.append((name, True, None))
        except AssertionError as e:
            print(f"✗ ÉCHEC: {e}")
            results.append((name, False, str(e)))
        except Exception as e:
            print(f"✗ ERREUR: {e}")
            results.append((name, False, str(e)))
    
    # Résumé
    print("\n" + "=" * 70)
    print("RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    for name, success, error in results:
        status = "✓ RÉUSSI" if success else "✗ ÉCHEC"
        print(f"{status:12s} - {name}")
        if error:
            print(f"             Erreur: {error}")
    
    print("=" * 70)
    print(f"Résultat: {success_count}/{total_count} tests réussis")
    print("=" * 70 + "\n")
    
    return success_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

