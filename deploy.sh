#!/bin/bash
# ============================================================================
# SCRIPT DE DÉPLOIEMENT AUTOMATIQUE SUR PYTHONANYWHERE
# ============================================================================

echo "=========================================================================="
echo "  DÉPLOIEMENT MIGRATION LYSA V19 SUR PYTHONANYWHERE"
echo "=========================================================================="
echo ""

# Configuration
VENV_NAME="migration_lysa"
PROJECT_DIR="$HOME/migration_lysa_v19"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Vérifier si on est sur PythonAnywhere
if [[ ! "$HOSTNAME" =~ "pythonanywhere.com" ]]; then
    print_warning "Ce script est conçu pour PythonAnywhere"
    print_info "Voulez-vous continuer quand même ? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

echo ""
print_info "Démarrage du déploiement..."
echo ""

# Étape 1 : Vérifier/Créer le virtualenv
echo "1. Vérification du virtualenv..."
if [ -d "$HOME/.virtualenvs/$VENV_NAME" ]; then
    print_success "Virtualenv '$VENV_NAME' existe déjà"
else
    print_info "Création du virtualenv '$VENV_NAME'..."
    mkvirtualenv $VENV_NAME --python=python3.11
    if [ $? -eq 0 ]; then
        print_success "Virtualenv créé"
    else
        print_error "Échec création virtualenv"
        exit 1
    fi
fi

# Activer le virtualenv
source $HOME/.virtualenvs/$VENV_NAME/bin/activate

# Étape 2 : Vérifier le dossier du projet
echo ""
echo "2. Vérification du dossier projet..."
if [ -d "$PROJECT_DIR" ]; then
    print_success "Dossier projet existe: $PROJECT_DIR"
    print_info "Voulez-vous mettre à jour ? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        cd "$PROJECT_DIR"
        if [ -d ".git" ]; then
            print_info "Mise à jour via git..."
            git pull
        else
            print_warning "Pas de repository Git. Mise à jour manuelle nécessaire."
        fi
    fi
else
    print_error "Dossier projet n'existe pas: $PROJECT_DIR"
    print_info "Veuillez d'abord uploader vos fichiers ou cloner votre repository"
    exit 1
fi

cd "$PROJECT_DIR"

# Étape 3 : Installation des dépendances
echo ""
echo "3. Installation des dépendances..."
if [ -f "requirements.txt" ]; then
    print_info "Installation depuis requirements.txt..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        print_success "Dépendances installées"
    else
        print_error "Échec installation dépendances"
        exit 1
    fi
else
    print_warning "Fichier requirements.txt non trouvé"
fi

# Étape 4 : Vérifier la configuration
echo ""
echo "4. Vérification de la configuration..."
if [ -f "config_v19.py" ]; then
    print_success "Fichier config_v19.py trouvé"
    print_warning "Vérifiez manuellement les paramètres de connexion"
else
    print_error "Fichier config_v19.py manquant"
    exit 1
fi

# Étape 5 : Créer les dossiers nécessaires
echo ""
echo "5. Création des dossiers..."
mkdir -p logs
print_success "Dossier logs créé"

# Étape 6 : Permissions
echo ""
echo "6. Configuration des permissions..."
chmod +x *.py
chmod +x *.sh
print_success "Permissions configurées"

# Étape 7 : Test de connexion
echo ""
echo "7. Test de connexion..."
print_info "Voulez-vous tester la connexion maintenant ? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    python tests/test_connexion.py
    if [ $? -eq 0 ]; then
        print_success "Test de connexion réussi"
    else
        print_warning "Test de connexion a échoué - Vérifiez la configuration"
    fi
fi

# Résumé
echo ""
echo "=========================================================================="
echo "  DÉPLOIEMENT TERMINÉ"
echo "=========================================================================="
echo ""
print_info "Prochaines étapes:"
echo ""
echo "  1. Vérifier la configuration dans config_v19.py"
echo "  2. Tester manuellement:"
echo "     cd $PROJECT_DIR"
echo "     workon $VENV_NAME"
echo "     python tests/test_connexion.py"
echo ""
echo "  3. Exécuter une migration:"
echo "     python migration_plan_comptable.py"
echo ""
echo "  4. Configurer une tâche planifiée:"
echo "     - Aller sur PythonAnywhere → Tasks"
echo "     - Créer une nouvelle tâche"
echo "     - Commande: $HOME/.virtualenvs/$VENV_NAME/bin/python $PROJECT_DIR/run_migration_scheduled.py"
echo ""
echo "  5. Vérifier le statut:"
echo "     python check_migration_status.py"
echo ""
print_success "Déploiement terminé avec succès!"
echo ""

