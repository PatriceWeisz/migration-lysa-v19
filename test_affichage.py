import sys
import os
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

sys.stdout.write("LIGNE 1\n")
sys.stdout.flush()

from connexion_double_v19 import ConnexionDoubleV19

sys.stdout.write("LIGNE 2 - APRES IMPORT\n")
sys.stdout.flush()

conn = ConnexionDoubleV19()
conn.connecter_tout()

sys.stdout.write("LIGNE 3 - APRES CONNEXION\n")
sys.stdout.flush()

