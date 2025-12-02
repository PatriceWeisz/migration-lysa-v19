#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VÉRIFICATION STRICTE DES CODES JOURNAUX
========================================
Vérifie que tous les codes de journaux de la source existent dans la destination
"""

import sys
from connexion_double_v19 import ConnexionDoubleV19

def verifier_codes_journaux():
    """Vérifie rigoureusement les codes de journaux"""
    print("\n" + "=" * 70)
    print("VÉRIFICATION STRICTE DES CODES JOURNAUX")
    print("=" * 70)
    
    conn = ConnexionDoubleV19()
    
    if not conn.connecter_tout():
        print("✗ Échec de connexion")
        return False
    
    # Récupérer uniquement les codes
    print("\nRécupération des codes...")
    
    journaux_source = conn.executer_source(
        'account.journal',
        'search_read',
        [],
        fields=['code', 'name', 'type']
    )
    
    journaux_dest = conn.executer_destination(
        'account.journal',
        'search_read',
        [],
        fields=['code', 'name', 'type']
    )
    
    # Créer sets de codes
    codes_source = {j['code'] for j in journaux_source if j.get('code')}
    codes_dest = {j['code'] for j in journaux_dest if j.get('code')}
    
    print(f"✓ {len(codes_source)} codes dans SOURCE")
    print(f"✓ {len(codes_dest)} codes dans DESTINATION")
    
    # Vérifier la correspondance EXACTE
    print("\n" + "=" * 70)
    print("VÉRIFICATION DES CODES")
    print("=" * 70)
    
    # Codes manquants dans destination
    manquants = codes_source - codes_dest
    
    # Codes en surplus dans destination
    surplus = codes_dest - codes_source
    
    # Codes communs
    communs = codes_source & codes_dest
    
    print(f"\nCodes communs         : {len(communs)}")
    print(f"Codes manquants (dest): {len(manquants)}")
    print(f"Codes surplus (dest)  : {len(surplus)}")
    
    # Afficher les codes en détail
    if manquants:
        print("\n" + "=" * 70)
        print("❌ CODES MANQUANTS DANS DESTINATION")
        print("=" * 70)
        
        for code in sorted(manquants):
            # Trouver le journal correspondant
            journal = next((j for j in journaux_source if j['code'] == code), None)
            if journal:
                print(f"  {code:15s} | {journal['type']:10s} | {journal['name']}")
        
        print(f"\n❌ PROBLÈME: {len(manquants)} journal(aux) manquant(s)")
        print("   → Action: Lancer migration_journaux.py")
        
    else:
        print("\n✅ TOUS les codes de journaux source sont dans la destination")
    
    if surplus:
        print("\n" + "=" * 70)
        print("ℹ️  CODES EN SURPLUS DANS DESTINATION (créés manuellement)")
        print("=" * 70)
        
        for code in sorted(surplus):
            # Trouver le journal correspondant
            journal = next((j for j in journaux_dest if j['code'] == code), None)
            if journal:
                print(f"  {code:15s} | {journal['type']:10s} | {journal['name']}")
        
        print(f"\nℹ️  {len(surplus)} journal(aux) créé(s) directement dans la destination")
        print("   C'est OK, ces journaux peuvent rester")
    
    # Liste des codes pour référence
    print("\n" + "=" * 70)
    print("LISTE COMPLÈTE DES CODES")
    print("=" * 70)
    
    print("\nCodes dans SOURCE:")
    for code in sorted(codes_source):
        status = "✅" if code in codes_dest else "❌"
        print(f"  {status} {code}")
    
    if surplus:
        print("\nCodes UNIQUEMENT dans DESTINATION:")
        for code in sorted(surplus):
            print(f"  ➕ {code}")
    
    # Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    
    if len(manquants) == 0:
        print("\n✅ VÉRIFICATION RÉUSSIE")
        print("✅ Tous les codes de journaux source sont présents dans destination")
        print(f"✅ {len(codes_source)}/{len(codes_source)} codes trouvés")
        
        if surplus:
            print(f"\nℹ️  Note: {len(surplus)} code(s) supplémentaire(s) dans destination (OK)")
        
        return True
    else:
        print("\n❌ VÉRIFICATION ÉCHOUÉE")
        print(f"❌ {len(manquants)} code(s) manquant(s) dans destination")
        print("\n💡 Action recommandée: Lancer migration_journaux.py")
        return False


if __name__ == "__main__":
    success = verifier_codes_journaux()
    print("\n" + "=" * 70 + "\n")
    sys.exit(0 if success else 1)

