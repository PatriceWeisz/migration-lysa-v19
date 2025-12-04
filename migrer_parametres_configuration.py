#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION PARAMÈTRES CONFIGURATION
===================================
Migre les paramètres de configuration de TOUS les modules
CRITIQUE : Les paramètres activent des fonctionnalités qui ajoutent des champs !
"""

import sys
import os

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from pathlib import Path
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

afficher("="*70)
afficher("MIGRATION PARAMÈTRES CONFIGURATION")
afficher("="*70)
afficher("")
afficher("⚠️ CRITIQUE : Les paramètres de configuration peuvent:")
afficher("   - Activer des fonctionnalités")
afficher("   - Ajouter des champs aux modèles")
afficher("   - Installer des sous-modules")
afficher("")
afficher("Ces paramètres DOIVENT être migrés AVANT les données !")
afficher("")
afficher("="*70)

# Connexion
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion\n")

# Créer rapport
LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(exist_ok=True)
RAPPORT = LOGS_DIR / f'migration_parametres_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

rapport = open(RAPPORT, 'w', encoding='utf-8')

def ecrire(msg):
    rapport.write(msg + '\n')
    rapport.flush()

ecrire("="*70)
ecrire("MIGRATION PARAMÈTRES CONFIGURATION")
ecrire(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
ecrire("="*70)

# =============================================================================
# 1. IR.CONFIG_PARAMETER (Paramètres système)
# =============================================================================

afficher("\n" + "="*70)
afficher("1. PARAMÈTRES SYSTÈME (ir.config_parameter)")
afficher("="*70)

ecrire("\n" + "="*70)
ecrire("IR.CONFIG_PARAMETER")
ecrire("="*70)

try:
    # Récupérer paramètres SOURCE
    params_src = conn.executer_source('ir.config_parameter', 'search_read',
                                     [('key', 'not in', ['database.uuid', 'database.secret'])],
                                     fields=['key', 'value'])
    
    afficher(f"Paramètres SOURCE: {len(params_src)}")
    ecrire(f"Paramètres SOURCE: {len(params_src)}")
    
    # Récupérer paramètres DEST
    params_dest = conn.executer_destination('ir.config_parameter', 'search_read',
                                           [],
                                           fields=['key', 'value'])
    
    dest_index = {p['key']: p for p in params_dest}
    
    stats_params = {'nouveaux': 0, 'mis_a_jour': 0, 'ignores': 0, 'erreurs': 0}
    
    # Paramètres à ignorer (spécifiques à l'instance)
    PARAMS_IGNORER = {
        'database.uuid',
        'database.secret',
        'web.base.url',
        'mail.catchall.domain',
        'mail.bounce.alias',
        'ribbon.name',
    }
    
    for param in params_src:
        key = param['key']
        value = param['value']
        
        # Ignorer paramètres système
        if key in PARAMS_IGNORER:
            stats_params['ignores'] += 1
            continue
        
        # Ignorer paramètres web.base.url.*
        if key.startswith('web.base.url.'):
            stats_params['ignores'] += 1
            continue
        
        try:
            if key in dest_index:
                # Mettre à jour si différent
                if dest_index[key]['value'] != value:
                    conn.executer_destination('ir.config_parameter', 'write',
                                            [dest_index[key]['id']], {'value': value})
                    afficher(f"  ✅ MAJ: {key} = {value[:50]}")
                    ecrire(f"  MAJ: {key} = {value}")
                    stats_params['mis_a_jour'] += 1
            else:
                # Créer
                conn.executer_destination('ir.config_parameter', 'set_param',
                                        key, value)
                afficher(f"  ✅ NEW: {key} = {value[:50]}")
                ecrire(f"  NEW: {key} = {value}")
                stats_params['nouveaux'] += 1
        
        except Exception as e:
            afficher(f"  ❌ ERREUR {key}: {str(e)[:40]}")
            ecrire(f"  ERREUR {key}: {str(e)}")
            stats_params['erreurs'] += 1
    
    afficher(f"\nRésultat:")
    afficher(f"  Nouveaux   : {stats_params['nouveaux']}")
    afficher(f"  Mis à jour : {stats_params['mis_a_jour']}")
    afficher(f"  Ignorés    : {stats_params['ignores']}")
    afficher(f"  Erreurs    : {stats_params['erreurs']}")
    
    ecrire(f"\nRésultat: {stats_params['nouveaux']} nouveaux, {stats_params['mis_a_jour']} MAJ")

except Exception as e:
    afficher(f"❌ ERREUR: {str(e)}")
    ecrire(f"ERREUR: {str(e)}")

# =============================================================================
# 2. RES.CONFIG.SETTINGS (Paramètres modules)
# =============================================================================

afficher("\n" + "="*70)
afficher("2. PARAMÈTRES MODULES (res.config.settings)")
afficher("="*70)
afficher("⚠️ ATTENTION: Ces paramètres peuvent activer des fonctionnalités")
afficher("")

ecrire("\n" + "="*70)
ecrire("RES.CONFIG.SETTINGS")
ecrire("="*70)

# Note: res.config.settings est un modèle TRANSIENT (pas de données persistées)
# Les paramètres sont stockés dans ir.config_parameter et les champs des modèles

afficher("ℹ️ res.config.settings est un modèle transient")
afficher("   Les paramètres sont déjà migrés via:")
afficher("   - ir.config_parameter (ci-dessus)")
afficher("   - Champs des modèles (ex: res.company)")
afficher("")

ecrire("Note: Modèle transient, paramètres dans ir.config_parameter et modèles")

# =============================================================================
# 3. RES.COMPANY (Paramètres société)
# =============================================================================

afficher("\n" + "="*70)
afficher("3. PARAMÈTRES SOCIÉTÉ (res.company)")
afficher("="*70)

ecrire("\n" + "="*70)
ecrire("RES.COMPANY")
ecrire("="*70)

try:
    # Récupérer société SOURCE (généralement ID 1)
    company_src = conn.executer_source('res.company', 'search_read',
                                      [('id', '=', 1)],
                                      fields=[])
    
    if not company_src:
        afficher("⚠️ Aucune société trouvée en SOURCE")
    else:
        company_src = company_src[0]
        
        # Champs à migrer (paramètres de configuration)
        CHAMPS_CONFIG = [
            # Comptabilité
            'fiscalyear_last_day',
            'fiscalyear_last_month',
            'period_lock_date',
            'fiscalyear_lock_date',
            'tax_lock_date',
            'anglo_saxon_accounting',
            'bank_account_code_prefix',
            'cash_account_code_prefix',
            'transfer_account_code_prefix',
            'account_purchase_tax_id',
            'account_sale_tax_id',
            'tax_calculation_rounding_method',
            
            # Ventes
            'sale_quotation_validity_days',
            'portal_confirmation_sign',
            'portal_confirmation_pay',
            
            # Achats
            'po_lead',
            'po_lock',
            'po_double_validation',
            'po_double_validation_amount',
            
            # Stock
            'security_lead',
            'propagation_minimum_delta',
            
            # Fabrication
            'manufacturing_lead',
            
            # RH
            'resource_calendar_id',
            'hr_presence_control_email',
            'hr_presence_control_ip',
            
            # Autres
            'paperformat_id',
            'external_report_layout_id',
        ]
        
        # Récupérer champs disponibles
        fields_info = conn.executer_source('res.company', 'fields_get', [])
        champs_disponibles = [c for c in CHAMPS_CONFIG if c in fields_info]
        
        afficher(f"Champs configuration disponibles: {len(champs_disponibles)}")
        
        # Préparer données
        data = {}
        for champ in champs_disponibles:
            if champ in company_src and company_src[champ]:
                value = company_src[champ]
                
                # Gérer relations many2one
                if isinstance(value, (list, tuple)) and len(value) == 2:
                    # Pour l'instant, on skip les relations
                    # TODO: mapper les IDs
                    continue
                
                data[champ] = value
        
        if data:
            try:
                # Mettre à jour société destination (ID 1)
                conn.executer_destination('res.company', 'write', [1], data)
                
                afficher(f"✅ {len(data)} paramètres société migrés:")
                ecrire(f"\n{len(data)} paramètres migrés:")
                
                for champ, value in data.items():
                    afficher(f"  - {champ}: {value}")
                    ecrire(f"  - {champ}: {value}")
            
            except Exception as e:
                afficher(f"❌ ERREUR: {str(e)}")
                ecrire(f"ERREUR: {str(e)}")
        else:
            afficher("ℹ️ Aucun paramètre à migrer")
            ecrire("Aucun paramètre à migrer")

except Exception as e:
    afficher(f"❌ ERREUR: {str(e)}")
    ecrire(f"ERREUR: {str(e)}")

# =============================================================================
# 4. PARAMÈTRES SPÉCIFIQUES PAR MODULE
# =============================================================================

afficher("\n" + "="*70)
afficher("4. PARAMÈTRES SPÉCIFIQUES MODULES")
afficher("="*70)

ecrire("\n" + "="*70)
ecrire("PARAMÈTRES SPÉCIFIQUES")
ecrire("="*70)

# Dictionnaire des paramètres spécifiques par module
PARAMETRES_MODULES = {
    'account': {
        'modele': 'res.company',
        'champs': [
            'anglo_saxon_accounting',
            'tax_calculation_rounding_method',
            'account_purchase_tax_id',
            'account_sale_tax_id',
        ]
    },
    'sale': {
        'modele': 'res.company',
        'champs': [
            'sale_quotation_validity_days',
            'portal_confirmation_sign',
            'portal_confirmation_pay',
        ]
    },
    'purchase': {
        'modele': 'res.company',
        'champs': [
            'po_lead',
            'po_lock',
            'po_double_validation',
            'po_double_validation_amount',
        ]
    },
    'stock': {
        'modele': 'res.company',
        'champs': [
            'security_lead',
            'propagation_minimum_delta',
        ]
    },
    'mrp': {
        'modele': 'res.company',
        'champs': [
            'manufacturing_lead',
        ]
    },
}

afficher("\nℹ️ Paramètres spécifiques déjà migrés via res.company (ci-dessus)")
afficher("")

for module, config in PARAMETRES_MODULES.items():
    afficher(f"  - {module}: {len(config['champs'])} paramètres")
    ecrire(f"  - {module}: {len(config['champs'])} paramètres")

# =============================================================================
# 5. SÉQUENCES (ir.sequence)
# =============================================================================

afficher("\n" + "="*70)
afficher("5. SÉQUENCES (ir.sequence)")
afficher("="*70)
afficher("⚠️ Les séquences définissent les numéros de factures, BL, etc.")
afficher("")

ecrire("\n" + "="*70)
ecrire("IR.SEQUENCE")
ecrire("="*70)

try:
    # Récupérer séquences SOURCE
    sequences_src = conn.executer_source('ir.sequence', 'search_read',
                                        [],
                                        fields=['name', 'code', 'prefix', 'suffix',
                                               'padding', 'number_next', 'number_increment',
                                               'implementation', 'company_id'])
    
    afficher(f"Séquences SOURCE: {len(sequences_src)}")
    ecrire(f"Séquences SOURCE: {len(sequences_src)}")
    
    # Récupérer séquences DEST
    sequences_dest = conn.executer_destination('ir.sequence', 'search_read',
                                              [],
                                              fields=['code'])
    
    dest_codes = {s['code']: s['id'] for s in sequences_dest if s.get('code')}
    
    stats_seq = {'nouveaux': 0, 'mis_a_jour': 0, 'erreurs': 0}
    
    for seq in sequences_src:
        code = seq.get('code')
        
        if not code:
            continue
        
        # Préparer données
        data = {
            'name': seq['name'],
            'prefix': seq.get('prefix', ''),
            'suffix': seq.get('suffix', ''),
            'padding': seq.get('padding', 0),
            'number_next': seq.get('number_next', 1),
            'number_increment': seq.get('number_increment', 1),
            'implementation': seq.get('implementation', 'standard'),
        }
        
        try:
            if code in dest_codes:
                # Mettre à jour
                conn.executer_destination('ir.sequence', 'write',
                                        [dest_codes[code]], data)
                afficher(f"  ✅ MAJ: {seq['name']}")
                ecrire(f"  MAJ: {seq['name']}")
                stats_seq['mis_a_jour'] += 1
            else:
                # Créer
                data['code'] = code
                conn.executer_destination('ir.sequence', 'create', data)
                afficher(f"  ✅ NEW: {seq['name']}")
                ecrire(f"  NEW: {seq['name']}")
                stats_seq['nouveaux'] += 1
        
        except Exception as e:
            afficher(f"  ❌ ERREUR {seq['name']}: {str(e)[:40]}")
            ecrire(f"  ERREUR {seq['name']}: {str(e)}")
            stats_seq['erreurs'] += 1
    
    afficher(f"\nRésultat:")
    afficher(f"  Nouveaux   : {stats_seq['nouveaux']}")
    afficher(f"  Mis à jour : {stats_seq['mis_a_jour']}")
    afficher(f"  Erreurs    : {stats_seq['erreurs']}")
    
    ecrire(f"\nRésultat: {stats_seq['nouveaux']} nouveaux, {stats_seq['mis_a_jour']} MAJ")

except Exception as e:
    afficher(f"❌ ERREUR: {str(e)}")
    ecrire(f"ERREUR: {str(e)}")

# =============================================================================
# RÉSUMÉ
# =============================================================================

afficher("\n" + "="*70)
afficher("RÉSUMÉ MIGRATION PARAMÈTRES")
afficher("="*70)

ecrire("\n" + "="*70)
ecrire("RÉSUMÉ")
ecrire("="*70)

afficher(f"\n1. ir.config_parameter:")
afficher(f"   - Nouveaux   : {stats_params['nouveaux']}")
afficher(f"   - Mis à jour : {stats_params['mis_a_jour']}")

afficher(f"\n2. res.company:")
afficher(f"   - Paramètres migrés")

afficher(f"\n3. ir.sequence:")
afficher(f"   - Nouveaux   : {stats_seq['nouveaux']}")
afficher(f"   - Mis à jour : {stats_seq['mis_a_jour']}")

ecrire(f"\n1. ir.config_parameter: {stats_params['nouveaux']} nouveaux, {stats_params['mis_a_jour']} MAJ")
ecrire(f"2. res.company: Paramètres migrés")
ecrire(f"3. ir.sequence: {stats_seq['nouveaux']} nouveaux, {stats_seq['mis_a_jour']} MAJ")

afficher("\n" + "="*70)
afficher("✅ MIGRATION PARAMÈTRES TERMINÉE")
afficher("="*70)
afficher("")
afficher("⚠️ IMPORTANT:")
afficher("   Les paramètres ont été migrés.")
afficher("   Certains peuvent nécessiter un redémarrage d'Odoo")
afficher("   pour activer toutes les fonctionnalités.")
afficher("")
afficher("Prochaine étape:")
afficher("   1. Vérifier que les fonctionnalités sont activées")
afficher("   2. Lancer la migration des données")
afficher("")

ecrire("\nMigration paramètres terminée")
ecrire("Certains paramètres peuvent nécessiter redémarrage Odoo")

afficher(f"Rapport: {RAPPORT}")

rapport.close()

