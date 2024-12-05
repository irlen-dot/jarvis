from langchain_openai import OpenAIEmbeddings
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
   def __init__(self):
       self.embeddings = OpenAIEmbeddings(model=os.getenv('EMBEDDING_MODEL'))

   def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
       texts = [chunk['text'] for chunk in chunks]
       embeddings = self.embeddings.embed_documents(texts)

       for chunk, embedding in zip(chunks, embeddings):
           chunk['embedding'] = embedding

       return chunks

   def embed_query(self, query: str) -> List[float]:
       return self.embeddings.embed_query(query)