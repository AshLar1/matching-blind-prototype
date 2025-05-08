import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec, LdaModel
from gensim import corpora
import os

# Download only needed NLTK resources
nltk.download('stopwords')

# Load data
df = pd.read_csv('data/messages.csv')  # Ensure this file exists
assert 'message' in df.columns, "❌ 'message' column not found in CSV"

# Clean the text
stop_words = set(stopwords.words('english'))


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    tokens = text.split()  # Simpler tokenizer for Replit
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)


df['clean_message'] = df['message'].apply(clean_text)

# Tokenize for LDA & Word2Vec
tokenized = [msg.split() for msg in df['clean_message']]

# TF-IDF
tfidf_vectorizer = TfidfVectorizer(max_features=100)
tfidf_matrix = tfidf_vectorizer.fit_transform(df['clean_message'])
tfidf_df = pd.DataFrame(
    tfidf_matrix.toarray(),
    columns=[f'tfidf_{i}' for i in range(tfidf_matrix.shape[1])])

# LDA (Topic Modeling)
dictionary = corpora.Dictionary(tokenized)
corpus = [dictionary.doc2bow(text) for text in tokenized]
lda_model = LdaModel(corpus=corpus,
                     id2word=dictionary,
                     num_topics=10,
                     passes=5)


def topic_vector(doc_topics, num_topics=10):
    vec = [0] * num_topics
    for topic_num, score in doc_topics:
        vec[topic_num] = score
    return vec


lda_topics = [
    topic_vector(lda_model.get_document_topics(doc), 10) for doc in corpus
]
lda_df = pd.DataFrame(lda_topics, columns=[f'lda_{i}' for i in range(10)])

# Word2Vec
w2v_model = Word2Vec(sentences=tokenized,
                     vector_size=50,
                     window=5,
                     min_count=1,
                     workers=4)


def avg_word2vec(words, model, size=50):
    vectors = [model.wv[word] for word in words if word in model.wv]
    if not vectors:
        return [0] * size
    return list(sum(vectors) / len(vectors))


w2v_features = [avg_word2vec(words, w2v_model) for words in tokenized]
w2v_df = pd.DataFrame(w2v_features, columns=[f'w2v_{i}' for i in range(50)])

# Combine everything
final_df = pd.concat([df, tfidf_df, lda_df, w2v_df], axis=1)

# Save output
os.makedirs('data', exist_ok=True)
final_df.to_csv('data/messages_with_features.csv', index=False)

print("✅ Feature-enriched dataset saved to data/messages_with_features.csv")
