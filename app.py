from fastapi import FastAPI
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer, util
import requests
import re
import numpy as np

# ------------------- Setup -------------------
app = FastAPI()
client = MongoClient("mongodb://localhost:27017/")
db = client.books_db
collection = db.books

model = SentenceTransformer('all-MiniLM-L6-v2')  # small & fast

# ------------------- Helper Functions -------------------
def fetch_gutenberg(url):
    r = requests.get(url)
    r.encoding = 'utf-8'
    return r.text

def extract_first_chapters(text, num_chapters=2):
    chapters = re.split(r'Chapter \d+', text, flags=re.IGNORECASE)
    return chapters[1:num_chapters+1]

def split_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s]

def store_embeddings(sentences):
    for s in sentences:
        embedding = model.encode(s).tolist()
        collection.insert_one({"sentence": s, "embedding": embedding})

# ---------------- CLEAN SENTENCES BEFORE OUTPUT ----------------
def clean_sentence(s: str) -> str:
    s = s.replace("\r", " ") \
         .replace("\n", " ") \
         .replace("_", "")
    return " ".join(s.split())   # remove extra spaces

# ----------------- Search with similarity -----------------
def search_similar(query, top_k=5):
    query_emb = model.encode(query)
    results = []
    for doc in collection.find():
        emb = np.array(doc['embedding'], dtype=np.float32)
        score = util.cos_sim(query_emb, emb).item()

        cleaned_sentence = clean_sentence(doc["sentence"])  # CLEAN HERE ✔

        results.append((cleaned_sentence, score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]

# ------------------- API Endpoints -------------------
@app.get("/load_book")
def load_book():
    url = "https://www.gutenberg.org/files/1342/1342-0.txt"
    r = requests.get(url)
    r.encoding = 'utf-8'
    text = r.text

    # Extract chapters
    chapters = re.split(r'Chapter [IVXLCDM]+\.?', text, flags=re.IGNORECASE)
    chapters = [ch.strip() for ch in chapters if ch.strip()]
    chapters = chapters[:2]

    # Sentence split
    sentences = []
    for ch in chapters:
        sents = re.split(r'(?<=[.!?]) +', ch)
        sentences.extend([s.strip() for s in sents if s.strip()])

    # Store embeddings
    for s in sentences:
        embedding = model.encode(s).tolist()
        collection.insert_one({"sentence": s, "embedding": embedding})

    return {"message": f"{len(sentences)} sentences stored in MongoDB."}

@app.get("/query")
def query_book(q: str):
    results = search_similar(q)
    return {"query": q, "results": results}
