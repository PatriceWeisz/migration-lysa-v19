#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTS MIGRATION JOURNAUX
========================
Tests unitaires de la migration des journaux
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connexion_double_v19 import ConnexionDoubleV19
from migration_journaux import MigrationJournaux
from config_v19 import MIGRATION_PARAMS


def test_connexion_et_comptage():
    """Test de connexion et comptage des journaux"""
    print("\n" + "=" * 70)
    print("TEST CONNEXION ET COMPTAGE JOURNAUX")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        print("✗ Échec de connexion")
        return False
    
    migration = MigrationJournaux(connexion)
    migration.compter_journaux()
    
    assert migration.stats['total_source'] > 0, "Aucun journal dans la source"
    
    print(f"✓ {migration.stats['total_source']} journaux trouvés dans la source")
    print(f"✓ {migration.stats['total_dest_avant']} journaux dans la destination")
    
    return True


def test_recuperation_journaux():
    """Test de récupération des journaux source"""
    print("\n" + "=" * 70)
    print("TEST RÉCUPÉRATION JOURNAUX SOURCE")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    connexion.connecter_tout()
    
    migration = MigrationJournaux(connexion)
    journaux = migration.recuperer_journaux_source(limit=10)
    
    assert len(journaux) > 0, "Aucun journal récupéré"
    assert 'code' in journaux[0], "Champ 'code' manquant"
    assert 'name' in journaux[0], "Champ 'name' manquant"
    assert 'type' in journaux[0], "Champ 'type' manquant"
    
    print(f"✓ {len(journaux)} journaux récupérés")
    print(f"\nExemples de journaux:")
    for journal in journaux[:5]:
        print(f"  Code: {journal.get('code'):10s} Type: {journal.get('type'):10s} Nom: {journal.get('name')}")
    
    return True


def test_preparer_donnees():
    """Test de préparation des données"""
    print("\n" + "=" * 70)
    print("TEST PRÉPARATION DONNÉES")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    migration = MigrationJournaux(connexion)
    
    # Journal test
    journal_test = {
        'id': 1,
        'code': 'TESTJ',
        'name': 'Journal Test',
        'type': 'general',
        'active': True,
        'sequence': 10,
    }
    
    data = migration.preparer_donnees(journal_test)
    
    assert 'code' in data, "Champ 'code' manquant"
    assert 'name' in data, "Champ 'name' manquant"
    assert 'type' in data, "Champ 'type' manquant"
    assert data['code'] == 'TESTJ', "Code incorrect"
    
    print(f"✓ Données préparées:")
    for key, value in data.items():
        print(f"  - {key}: {value}")
    
    return True


def test_types_journaux():
    """Test des différents types de journaux"""
    print("\n" + "=" * 70)
    print("TEST TYPES DE JOURNAUX")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    connexion.connecter_tout()
    
    migration = MigrationJournaux(connexion)
    journaux = migration.recuperer_journaux_source()
    
    # Compter par type
    types = {}
    for journal in journaux:
        jtype = journal.get('type', 'unknown')
        types[jtype] = types.get(jtype, 0) + 1
    
    print("\nRépartition par type:")
    for jtype, count in sorted(types.items()):
        print(f"  - {jtype:15s}: {count:>3}")
    
    print(f"\n✓ {len(types)} types différents trouvés")
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
        
        migration = MigrationJournaux(connexion)
        
        # Migration de seulement 3 journaux en simulation
        success = migration.executer(limit=3)
        
        print(f"\n✓ Mode simulation:")
        print(f"  - Migrés (simulation): {migration.stats['migres']}")
        print(f"  - Ignorés: {migration.stats['ignores']}")
        print(f"  - Erreurs: {migration.stats['erreurs']}")
        
        return success
        
    finally:
        # Restaurer le mode original
        MIGRATION_PARAMS['MODE_SIMULATION'] = mode_original


def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "█" * 70)
    print("  SUITE DE TESTS - MIGRATION JOURNAUX")
    print("█" * 70)
    
    tests = [
        ("Connexion et comptage", test_connexion_et_comptage),
        ("Récupération journaux", test_recuperation_journaux),
        ("Préparation données", test_preparer_donnees),
        ("Types de journaux", test_types_journaux),
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

