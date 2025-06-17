# import pandas as pd
# df = pd.read_csv("assets/data_fusionnee.csv")
# df.columns = df.columns.str.strip().str.replace('"', '')
# df = df.rename(columns=lambda x: x.strip())


# # data.py
# import pandas as pd
# import os

# file_path = os.path.join(os.path.dirname(__file__), 'assets', 'data_fusionnee.csv')
# df = pd.read_csv(file_path)
# df.columns = df.columns.str.strip().str.replace('"', '')
# df = df.rename(columns=lambda x: x.strip())


import pandas as pd
import os

import os
import pandas as pd

# Détermination du chemin vers le fichier CSV
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'data_fusionnee.csv')

# Chargement des données
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    raise FileNotFoundError(f"Impossible de trouver le fichier CSV à l'emplacement : {csv_path}")


df.columns = df.columns.str.strip().str.replace('"', '')
df = df.rename(columns=lambda x: x.strip())



# Analyse mémoire détaillée
memory_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
print(f"[INFO] df utilise environ {memory_mb:.2f} Mo en mémoire")
