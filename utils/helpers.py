#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FONCTIONS UTILITAIRES POUR MIGRATION V19
========================================
Fonctions helper pour faciliter la migration
"""

import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from functools import wraps

def timer(func):
    """Décorateur pour mesurer le temps d'exécution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"⏱️  {func.__name__} exécuté en {duration:.2f}s")
        return result
    return wrapper

def retry(max_attempts=3, delay=2):
    """Décorateur pour réessayer en cas d'erreur"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"⚠️  Erreur: {e}. Tentative {attempt + 2}/{max_attempts}...")
                    time.sleep(delay)
        return wrapper
    return decorator

def chunk_list(data: List, chunk_size: int) -> List[List]:
    """Découpe une liste en chunks"""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def format_number(num: int) -> str:
    """Formate un nombre avec séparateurs de milliers"""
    return f"{num:,}".replace(',', ' ')

def format_duration(seconds: float) -> str:
    """Formate une durée en format lisible"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def format_date(date_str: str, input_format='%Y-%m-%d', output_format='%d/%m/%Y') -> str:
    """Formate une date"""
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except:
        return date_str

def safe_get(dct: Dict, *keys, default=None):
    """Récupère une valeur dans un dictionnaire imbriqué de manière sûre"""
    for key in keys:
        try:
            dct = dct[key]
        except (KeyError, TypeError, IndexError):
            return default
    return dct

def clean_dict(data: Dict, remove_empty=True, remove_none=True) -> Dict:
    """Nettoie un dictionnaire"""
    cleaned = {}
    for key, value in data.items():
        # Ignorer les valeurs vides si demandé
        if remove_empty and value == '':
            continue
        # Ignorer les valeurs None si demandé
        if remove_none and value is None:
            continue
        cleaned[key] = value
    return cleaned

def map_fields(source_dict: Dict, field_mapping: Dict) -> Dict:
    """Map les champs d'un dictionnaire selon un mapping"""
    result = {}
    for source_field, dest_field in field_mapping.items():
        if source_field in source_dict:
            result[dest_field] = source_dict[source_field]
    return result

def compare_dicts(dict1: Dict, dict2: Dict, ignore_keys=None) -> Dict:
    """Compare deux dictionnaires et retourne les différences"""
    if ignore_keys is None:
        ignore_keys = []
    
    differences = {}
    all_keys = set(dict1.keys()) | set(dict2.keys())
    
    for key in all_keys:
        if key in ignore_keys:
            continue
            
        val1 = dict1.get(key)
        val2 = dict2.get(key)
        
        if val1 != val2:
            differences[key] = {'source': val1, 'dest': val2}
    
    return differences

def progress_bar(current: int, total: int, width=50) -> str:
    """Crée une barre de progression en texte"""
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percent*100:.1f}% ({current}/{total})"

def estimate_remaining_time(start_time: float, current: int, total: int) -> str:
    """Estime le temps restant"""
    if current == 0:
        return "Calcul en cours..."
    
    elapsed = time.time() - start_time
    rate = current / elapsed
    remaining = (total - current) / rate if rate > 0 else 0
    
    return format_duration(remaining)

def validate_odoo_date(date_str: str) -> bool:
    """Valide un format de date Odoo"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except:
        return False

def validate_odoo_datetime(datetime_str: str) -> bool:
    """Valide un format de datetime Odoo"""
    try:
        datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        return True
    except:
        return False

def sanitize_string(text: str) -> str:
    """Nettoie une chaîne de caractères"""
    if not isinstance(text, str):
        return text
    # Supprimer les espaces en début/fin
    text = text.strip()
    # Remplacer les espaces multiples par un seul
    text = ' '.join(text.split())
    return text

def round_amount(amount: float, precision=2) -> float:
    """Arrondit un montant"""
    return round(amount, precision)

class ProgressTracker:
    """Classe pour suivre la progression"""
    
    def __init__(self, total: int, description: str = "Progression"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.errors = []
        
    def update(self, increment: int = 1):
        """Met à jour la progression"""
        self.current += increment
        
    def add_error(self, error: str):
        """Ajoute une erreur"""
        self.errors.append(error)
        
    def display(self):
        """Affiche la progression"""
        bar = progress_bar(self.current, self.total)
        remaining = estimate_remaining_time(self.start_time, self.current, self.total)
        print(f"\r{self.description}: {bar} - Restant: {remaining}", end='', flush=True)
        
    def finish(self):
        """Termine l'affichage"""
        elapsed = time.time() - self.start_time
        print(f"\n✓ Terminé en {format_duration(elapsed)}")
        if self.errors:
            print(f"⚠️  {len(self.errors)} erreur(s) détectée(s)")


if __name__ == "__main__":
    # Tests
    print("Test des helpers:")
    
    # Test chunk_list
    data = list(range(25))
    chunks = chunk_list(data, 10)
    print(f"Chunks: {len(chunks)} lots de {[len(c) for c in chunks]}")
    
    # Test format_number
    print(f"Formatage: {format_number(1234567)}")
    
    # Test format_duration
    print(f"Durée: {format_duration(3725)}")
    
    # Test progress_bar
    print(progress_bar(75, 100))
    
    # Test ProgressTracker
    tracker = ProgressTracker(100, "Test migration")
    for i in range(100):
        tracker.update()
        if i % 10 == 0:
            tracker.display()
        time.sleep(0.02)
    tracker.finish()

