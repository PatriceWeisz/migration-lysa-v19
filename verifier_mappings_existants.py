import json
from pathlib import Path

files = {
    'Comptes': 'account_mapping.json',
    'Partenaires': 'partner_mapping.json', 
    'Produits': 'product_template_mapping.json',
    'Taxes': 'tax_mapping.json',
    'Unités': 'uom_mapping.json',
    'Emplacements': 'location_mapping.json',
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

