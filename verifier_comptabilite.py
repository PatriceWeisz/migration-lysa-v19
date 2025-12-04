#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VÉRIFICATION COMPTABILITÉ
==========================
Compare Grand Livre et Balances entre source et destination
"""

import sys
import os

print("="*70, flush=True)
print("VERIFICATION COMPTABILITE", flush=True)
print("="*70, flush=True)
print("Import...", flush=True)

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19
from collections import defaultdict

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

afficher("\n="*70)
afficher("VÉRIFICATION: GRAND LIVRE ET BALANCES")
afficher("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion\n")

# =============================================================================
# BALANCE GÉNÉRALE
# =============================================================================

afficher("="*70)
afficher("BALANCE GÉNÉRALE")
afficher("="*70)

afficher("\nCalcul balance SOURCE...")
# Récupérer toutes les lignes comptables validées
lines_src = conn.executer_source('account.move.line', 'search_read',
                                 [('move_id.state', '=', 'posted')],
                                 fields=['account_id', 'debit', 'credit'])

balance_src = defaultdict(lambda: {'debit': 0, 'credit': 0, 'solde': 0})
for line in lines_src:
    if line.get('account_id'):
        account_id = line['account_id'][0] if isinstance(line['account_id'], list) else line['account_id']
        balance_src[account_id]['debit'] += line.get('debit', 0)
        balance_src[account_id]['credit'] += line.get('credit', 0)
        balance_src[account_id]['solde'] = balance_src[account_id]['debit'] - balance_src[account_id]['credit']

afficher(f"OK {len(lines_src)} lignes analysées")
afficher(f"   {len(balance_src)} comptes avec mouvements\n")

afficher("Calcul balance DESTINATION...")
lines_dst = conn.executer_destination('account.move.line', 'search_read',
                                     [('move_id.state', '=', 'posted')],
                                     fields=['account_id', 'debit', 'credit'])

balance_dst = defaultdict(lambda: {'debit': 0, 'credit': 0, 'solde': 0})
for line in lines_dst:
    if line.get('account_id'):
        account_id = line['account_id'][0] if isinstance(line['account_id'], list) else line['account_id']
        balance_dst[account_id]['debit'] += line.get('debit', 0)
        balance_dst[account_id]['credit'] += line.get('credit', 0)
        balance_dst[account_id]['solde'] = balance_dst[account_id]['debit'] - balance_dst[account_id]['credit']

afficher(f"OK {len(lines_dst)} lignes analysées")
afficher(f"   {len(balance_dst)} comptes avec mouvements\n")

# =============================================================================
# TOTAUX
# =============================================================================

total_debit_src = sum(b['debit'] for b in balance_src.values())
total_credit_src = sum(b['credit'] for b in balance_src.values())
total_debit_dst = sum(b['debit'] for b in balance_dst.values())
total_credit_dst = sum(b['credit'] for b in balance_dst.values())

afficher("="*70)
afficher("TOTAUX")
afficher("="*70)
afficher(f"SOURCE:")
afficher(f"  Total Débit  : {total_debit_src:>15,.2f}")
afficher(f"  Total Crédit : {total_credit_src:>15,.2f}")
afficher(f"  Différence   : {total_debit_src - total_credit_src:>15,.2f}")
afficher(f"\nDESTINATION:")
afficher(f"  Total Débit  : {total_debit_dst:>15,.2f}")
afficher(f"  Total Crédit : {total_credit_dst:>15,.2f}")
afficher(f"  Différence   : {total_debit_dst - total_credit_dst:>15,.2f}")
afficher(f"\nÉCART:")
afficher(f"  Débit        : {total_debit_dst - total_debit_src:>15,.2f}")
afficher(f"  Crédit       : {total_credit_dst - total_credit_src:>15,.2f}")

ecart = abs((total_debit_dst - total_credit_dst) - (total_debit_src - total_credit_src))
if ecart < 0.01:
    afficher(f"\n✅ BALANCE OK - Écart négligeable ({ecart:.2f})")
elif ecart < 1.0:
    afficher(f"\n⚠️ BALANCE OK - Écart mineur ({ecart:.2f})")
else:
    afficher(f"\n❌ ATTENTION - Écart significatif ({ecart:.2f})")

afficher("="*70)

# =============================================================================
# STOCKS
# =============================================================================

afficher("\n="*70)
afficher("QUANTITÉS EN STOCK")
afficher("="*70)

afficher("\nCalcul stock SOURCE...")
stock_src = conn.executer_source('stock.quant', 'search_read',
                                 [],
                                 fields=['product_id', 'location_id', 'quantity'])

total_qty_src = sum(q.get('quantity', 0) for q in stock_src)
afficher(f"OK {len(stock_src)} positions stock")
afficher(f"   Quantité totale: {total_qty_src:,.2f}")

afficher("\nCalcul stock DESTINATION...")
stock_dst = conn.executer_destination('stock.quant', 'search_read',
                                     [],
                                     fields=['product_id', 'location_id', 'quantity'])

total_qty_dst = sum(q.get('quantity', 0) for q in stock_dst)
afficher(f"OK {len(stock_dst)} positions stock")
afficher(f"   Quantité totale: {total_qty_dst:,.2f}")

ecart_stock = abs(total_qty_dst - total_qty_src)
afficher(f"\nÉCART STOCK: {ecart_stock:,.2f}")

if ecart_stock < 1.0:
    afficher("✅ STOCK OK")
elif ecart_stock < 100.0:
    afficher("⚠️ STOCK OK - Écart mineur")
else:
    afficher("❌ ATTENTION - Vérifier les stocks")

afficher("="*70)

afficher("\n✅ VÉRIFICATION TERMINÉE")
afficher("="*70)
afficher("Si les balances sont OK:")
afficher("  → Migration comptable réussie ✅")
afficher("Si écarts importants:")
afficher("  → Vérifier les mappings de comptes")
afficher("  → Relancer migration des écritures")
afficher("="*70)

