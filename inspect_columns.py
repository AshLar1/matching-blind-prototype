import pandas as pd

df = pd.read_csv('data/messages.csv')
print("✅ Columns in messages.csv:")
print(df.columns.tolist())

print(f"\n🧮 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
