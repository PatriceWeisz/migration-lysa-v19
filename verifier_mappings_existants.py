import json
from pathlib import Path

files = {
    'Comptes': 'account_mapping.json',
    'Partenaires': 'partner_mapping.json', 
    'Produits': 'product_template_mapping.json',
    'Taxes': 'tax_mapping.json',
    'Journaux': 'account_journal_mapping.json',
    'Utilisateurs': 'user_mapping.json',
    'Employés': 'employe_mapping.json',
    'Départements': 'hr_department_mapping.json',
    'Postes': 'hr_job_mapping.json',
    'Entrepôts': 'stock_warehouse_mapping.json',
    'Unités': 'uom_mapping.json',
    'Emplacements': 'location_mapping.json',
    'Catégories prod': 'product_category_mapping.json',
    'Listes prix': 'pricelist_mapping.json',
    'Étiquettes contact': 'partner_category_mapping.json',
    'Plans analytiques': 'analytic_plan_mapping.json',
    'Comptes analytiques': 'analytic_account_mapping.json',
    'Équipes commerciales': 'crm_team_mapping.json',
    'Projets': 'project_mapping.json',
}

print("="*60)
print("DONNÉES DÉJÀ MIGRÉES")
print("="*60)

for nom, fichier in files.items():
    f = Path('logs') / fichier
    if f.exists():
        data = json.load(open(f))
        print(f"{nom:20s}: {len(data):>6,d} mappés")
    else:
        print(f"{nom:20s}:      0 mappés")

print("="*60)
print("Le script NE VA PAS écraser ces données")
print("Il va juste COMPLÉTER ce qui manque")
print("="*60)

