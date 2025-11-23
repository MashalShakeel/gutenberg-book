#### Mashal Shakeel
#### FA23-BCS-187
#### Assignment 

# Gutenberg Book Search API

The FastAPI lab task downloads text from Project Gutenberg, extracts sentences, stores their vector embeddings in MongoDB, and allows user to run semantic search on the book.

## Features

- Fetches Pride & Prejudice from Project Gutenberg
- Extracts first 2 chapters
- Splits text into clean sentences

## Stores

- sentence text and SentenceTransformer MiniLM
- `/query?q=...` endpoint returns the most similar sentences
- I have added logic tp remove extra symbols like _, \r, \n before returning results

## Tech Stack

- FastAPI: REST API
- MongoDB: stores sentences + embeddings
- SentenceTransformers: MiniLM-L6-v2 model for embeddings
- NumPy: similarity scoring

## Setup Instructions
### 1. Install dependencies
```
pip install fastapi uvicorn pymongo sentence-transformers requests numpy
```

### 2. Start MongoDB
Make sure MongoDB is running at:
`mongodb://localhost:27017/`

### 3. Run the API
```commandline
uvicorn app:app --reload
```

## Endpoints
### 1. /load_book
Downloads the book → extracts sentences → stores them in MongoDB.
Response example:
```
{
  "message": "126 sentences stored in MongoDB."
}
```
Run this once before querying.

### 2. /query?q=your_text

Searches the stored sentences and returns top 5 similar matches.
Example: `/query?q=Lizzy`

Response:
```
{
  "query": "Lizzy",
  "results": [
    ["But you are always giving her the preference...", 0.63],
    ["Lizzy is not a bit better than the others...", 0.62],
    ...
  ]
}

```

## Project Structure
- app.py        
- MongoDB collection: books_db.books

## Notes
- I store only first 2 chapters (to keep it small).
- Similarity score is cosine similarity.
