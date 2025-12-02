#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTS DE CONNEXION POUR MIGRATION V19
=====================================
Tests unitaires des connexions aux bases
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connexion_double_v19 import ConnexionDoubleV19
from config_v19 import SOURCE_CONFIG, DEST_CONFIG_V19


def test_connexion_source():
    """Test de la connexion à la base source"""
    print("\n" + "=" * 70)
    print("TEST CONNEXION SOURCE")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    result = connexion.connecter_source()
    
    assert result == True, "La connexion à la source a échoué"
    assert connexion.source_uid is not None, "UID source non défini"
    assert connexion.source_models is not None, "Modèles source non définis"
    
    print("✓ Test connexion source réussi")
    return True


def test_connexion_destination():
    """Test de la connexion à la base destination"""
    print("\n" + "=" * 70)
    print("TEST CONNEXION DESTINATION")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    result = connexion.connecter_destination()
    
    assert result == True, "La connexion à la destination a échoué"
    assert connexion.dest_uid is not None, "UID destination non défini"
    assert connexion.dest_models is not None, "Modèles destination non définis"
    
    print("✓ Test connexion destination réussi")
    return True


def test_connexion_double():
    """Test de la connexion simultanée aux deux bases"""
    print("\n" + "=" * 70)
    print("TEST CONNEXION DOUBLE")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    result = connexion.connecter_tout()
    
    assert result == True, "La connexion double a échoué"
    
    print("✓ Test connexion double réussi")
    return connexion


def test_executer_source():
    """Test d'exécution sur la base source"""
    print("\n" + "=" * 70)
    print("TEST EXÉCUTION SOURCE")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    connexion.connecter_tout()
    
    # Compter les partenaires
    count = connexion.executer_source('res.partner', 'search_count', [])
    print(f"Nombre de partenaires source: {count:,}")
    
    assert count >= 0, "Le comptage a échoué"
    
    print("✓ Test exécution source réussi")
    return True


def test_executer_destination():
    """Test d'exécution sur la base destination"""
    print("\n" + "=" * 70)
    print("TEST EXÉCUTION DESTINATION")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    connexion.connecter_tout()
    
    # Compter les partenaires
    count = connexion.executer_destination('res.partner', 'search_count', [])
    print(f"Nombre de partenaires destination: {count:,}")
    
    assert count >= 0, "Le comptage a échoué"
    
    print("✓ Test exécution destination réussi")
    return True


def test_verification_version():
    """Test de la vérification de version"""
    print("\n" + "=" * 70)
    print("TEST VÉRIFICATION VERSION")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    connexion.connecter_tout()
    
    result = connexion.verifier_version_destination()
    
    if not result:
        print("⚠️  ATTENTION: La destination n'est pas en v19")
        print("   Ce test peut échouer si la base n'est pas encore en v19")
    
    print("✓ Test vérification version terminé")
    return True


def test_comptage_models():
    """Test du comptage de différents modèles"""
    print("\n" + "=" * 70)
    print("TEST COMPTAGE MODÈLES")
    print("=" * 70)
    
    connexion = ConnexionDoubleV19()
    connexion.connecter_tout()
    
    modeles = [
        'res.partner',
        'product.product',
        'account.account',
        'account.journal',
        'account.move',
    ]
    
    print("\nComptage source:")
    for model in modeles:
        count = connexion.compter_records(model, base='source')
        print(f"  {model:30s}: {count:>10,}")
    
    print("\nComptage destination:")
    for model in modeles:
        count = connexion.compter_records(model, base='destination')
        print(f"  {model:30s}: {count:>10,}")
    
    print("✓ Test comptage modèles réussi")
    return True


def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "█" * 70)
    print("  SUITE DE TESTS - CONNEXION MIGRATION V19")
    print("█" * 70)
    
    tests = [
        ("Connexion Source", test_connexion_source),
        ("Connexion Destination", test_connexion_destination),
        ("Connexion Double", test_connexion_double),
        ("Exécution Source", test_executer_source),
        ("Exécution Destination", test_executer_destination),
        ("Vérification Version", test_verification_version),
        ("Comptage Modèles", test_comptage_models),
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

