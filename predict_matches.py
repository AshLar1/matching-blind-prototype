import pandas as pd
import pickle

# Step 1: Load your trained model
with open("models/catboost_model.pkl",
              "rb") as f:  # Replace with 'rf_model.pkl' if needed
          model = pickle.load(f)

# Step 2: Load processed dataset
df = pd.read_csv("data/messages.csv")

# Step 3: Select model input features
# Modify these if your model used other feature types
feature_cols = [
    "message_count_per_match", "response_time", "lda_score", "message_length",
    "word_count", "sentiment_score", "bert_sentiment_num", "lda_persona",
    "w2v_persona"
] + [f"w2v_{i}" for i in range(1, 51)] + [f"svd_{i}" for i in range(1, 51)]

X = df[feature_cols]

# Step 4: Predict match success
predictions = model.predict(X)
df['model_prediction'] = predictions

# Step 5: Save results to new file
df.to_csv("data/messages_with_predictions.csv", index=False)
print("✅ Predictions saved to data/messages_with_predictions.csv")
