#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYSE SYSTÉMATIQUE DES DIFFÉRENCES DES JOURNAUX
=================================================
Analyse toutes les différences entre source et destination
pour identifier les patterns communs
"""

import sys
from connexion_double_v19 import ConnexionDoubleV19

def analyser_toutes_differences():
    """Analyse systématique de toutes les différences"""
    print("\n" + "=" * 70)
    print("ANALYSE SYSTÉMATIQUE DES DIFFÉRENCES")
    print("=" * 70)
    
    conn = ConnexionDoubleV19()
    
    if not conn.connecter_tout():
        print("✗ Échec de connexion")
        return False
    
    # Récupérer tous les journaux
    fields = [
        'code', 'name', 'type',
        'default_account_id',
        'suspense_account_id', 
        'profit_account_id',
        'loss_account_id',
        'sequence',
    ]
    
    print("\nRécupération des journaux...")
    journaux_source = conn.executer_source('account.journal', 'search_read', [], fields=fields)
    journaux_dest = conn.executer_destination('account.journal', 'search_read', [], fields=fields)
    
    # Créer dictionnaires par code
    source_dict = {j['code']: j for j in journaux_source}
    dest_dict = {j['code']: j for j in journaux_dest}
    
    # Analyser les journaux communs
    codes_communs = set(source_dict.keys()) & set(dest_dict.keys())
    
    print(f"✓ {len(journaux_source)} journaux source")
    print(f"✓ {len(journaux_dest)} journaux destination")
    print(f"✓ {len(codes_communs)} journaux communs à analyser")
    
    # Compteurs de différences
    stats_diff = {
        'name': 0,
        'type': 0,
        'sequence': 0,
        'default_account_id': 0,
        'suspense_account_id': 0,
        'profit_account_id': 0,
        'loss_account_id': 0,
    }
    
    # Patterns de différences
    patterns_profit_loss = []
    patterns_autres = []
    
    print("\n" + "=" * 70)
    print("ANALYSE PAR JOURNAL")
    print("=" * 70)
    
    for code in sorted(codes_communs):
        s = source_dict[code]
        d = dest_dict[code]
        
        diff_journal = []
        
        # Analyser chaque champ
        for champ in ['name', 'type', 'sequence', 'default_account_id', 'suspense_account_id', 'profit_account_id', 'loss_account_id']:
            val_s = s.get(champ)
            val_d = d.get(champ)
            
            # Extraire les valeurs comparables
            if champ.endswith('_account_id'):
                # Pour les comptes, comparer les codes (pas les IDs)
                val_s_str = val_s[1] if (val_s and val_s != False and isinstance(val_s, (list, tuple))) else 'Non configuré'
                val_d_str = val_d[1] if (val_d and val_d != False and isinstance(val_d, (list, tuple))) else 'Non configuré'
            else:
                val_s_str = val_s
                val_d_str = val_d
            
            # Comparer
            if val_s_str != val_d_str:
                diff_journal.append({
                    'champ': champ,
                    'source': val_s_str,
                    'dest': val_d_str
                })
                stats_diff[champ] += 1
        
        # Afficher si différences
        if diff_journal:
            print(f"\n{code} ({s['type']}) - {len(diff_journal)} différence(s):")
            
            for diff in diff_journal:
                champ = diff['champ']
                print(f"  • {champ:25s}: '{diff['source']}' → '{diff['dest']}'")
                
                # Classifier la différence
                if champ in ['profit_account_id', 'loss_account_id']:
                    if diff['source'] == 'Non configuré' and '999' in str(diff['dest']):
                        patterns_profit_loss.append(code)
                    else:
                        patterns_autres.append((code, champ, diff))
                else:
                    patterns_autres.append((code, champ, diff))
    
    # Résumé des patterns
    print("\n" + "=" * 70)
    print("ANALYSE DES PATTERNS")
    print("=" * 70)
    
    print(f"\nStatistiques des différences:")
    print(f"  - Noms différents        : {stats_diff['name']}")
    print(f"  - Types différents       : {stats_diff['type']}")
    print(f"  - Séquences différentes  : {stats_diff['sequence']}")
    print(f"  - Compte défaut          : {stats_diff['default_account_id']}")
    print(f"  - Compte suspens         : {stats_diff['suspense_account_id']}")
    print(f"  - Compte profit          : {stats_diff['profit_account_id']}")
    print(f"  - Compte loss            : {stats_diff['loss_account_id']}")
    
    print(f"\nPatterns identifiés:")
    print(f"  ✅ Comptes profit/loss v19 (NORMAL): {len(set(patterns_profit_loss))} journaux")
    print(f"  ⚠️  Autres différences            : {len(patterns_autres)} cas")
    
    # Détail des patterns profit/loss
    if patterns_profit_loss:
        print(f"\n✅ Journaux avec ajout automatique profit/loss v19 (ACCEPTABLE):")
        unique_profit_loss = sorted(set(patterns_profit_loss))
        for code in unique_profit_loss:
            print(f"  - {code}")
    
    # Détail des autres différences
    if patterns_autres:
        print(f"\n⚠️  Autres différences à examiner:")
        
        # Grouper par type de différence
        par_type = {}
        for code, champ, diff in patterns_autres:
            if champ not in par_type:
                par_type[champ] = []
            par_type[champ].append((code, diff))
        
        for champ, items in par_type.items():
            print(f"\n  {champ} ({len(items)} cas):")
            for code, diff in items[:5]:  # Afficher les 5 premiers
                print(f"    - {code}: '{diff['source']}' → '{diff['dest']}'")
            if len(items) > 5:
                print(f"    ... et {len(items) - 5} autre(s)")
    
    # Conclusion
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    
    total_diff = sum(stats_diff.values())
    diff_acceptables = stats_diff['profit_account_id'] + stats_diff['loss_account_id']
    diff_a_examiner = total_diff - diff_acceptables
    
    print(f"\nTotal différences        : {total_diff}")
    print(f"  ✅ Acceptables (v19)   : {diff_acceptables} (profit/loss)")
    print(f"  ⚠️  À examiner          : {diff_a_examiner}")
    
    if diff_a_examiner == 0:
        print("\n✅ Toutes les différences sont ACCEPTABLES (comportement v19)")
        print("✅ Les journaux sont correctement configurés")
        return True
    else:
        print(f"\n⚠️  {diff_a_examiner} différence(s) à examiner")
        print("   Principalement : noms, séquences, ou codes de comptes")
        return False


if __name__ == "__main__":
    success = analyser_toutes_differences()
    print("\n" + "=" * 70 + "\n")
    sys.exit(0 if success else 1)

