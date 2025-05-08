import pandas as pd
from sklearn.cluster import KMeans

# Load your messages file
df = pd.read_csv("data/messages.csv")

# ✅ Generate w2v_persona (from w2v_1 to w2v_50)
w2v_cols = [f"w2v_{i}" for i in range(1, 51)]
kmeans_w2v = KMeans(n_clusters=10, random_state=42, n_init="auto")
df['w2v_persona'] = kmeans_w2v.fit_predict(df[w2v_cols])

# ✅ Generate lda_persona (from lda_score + lda_topic)
# Optional: can use lda_topic directly, but here we cluster for flexibility
lda_cols = ['lda_score', 'lda_topic']
kmeans_lda = KMeans(n_clusters=10, random_state=42, n_init="auto")
df['lda_persona'] = kmeans_lda.fit_predict(df[lda_cols])

# ✅ Save updated file
df.to_csv("data/messages.csv", index=False)
print("✅ Added 'w2v_persona' and 'lda_persona' to messages.csv")
