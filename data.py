import pandas as pd
df = pd.read_csv("assets/data_fusionnee.csv")
df.columns = df.columns.str.strip().str.replace('"', '')
df = df.rename(columns=lambda x: x.strip())



# Analyse mémoire détaillée
memory_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
print(f"[INFO] df utilise environ {memory_mb:.2f} Mo en mémoire")
