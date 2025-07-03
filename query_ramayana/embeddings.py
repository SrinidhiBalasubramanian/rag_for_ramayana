import chromadb

from openai import OpenAI
from typing import List

from config import RAMAYANA_VERSIONS, OPENAI_API_KEY, EmbeddingResult
from utils import Tools

safe_run = Tools.safe_run
logger = Tools.setup_logger("query_ramayana")

class EmbeddingStore:
    def __init__(self, ramayana, persist_path="./chroma_data"):
        self.ramayana = ramayana
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name=ramayana)
        self.openai = OpenAI(api_key = OPENAI_API_KEY)

    @safe_run(default_return=[
        EmbeddingResult("", {}, 0)
    ])
    def get_query_results(self, query_text: str, top_k: int = 5) -> List[EmbeddingResult]:
        embedding = self.openai.embeddings.create(
            model="text-embedding-ada-002",
            input=query_text
        ).data[0].embedding

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )

        return [
            EmbeddingResult(doc, meta, dist)
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
    
    
if __name__ == "__main__":
    ramayana_version = RAMAYANA_VERSIONS.VALMIKI
    embedding_store = EmbeddingStore(ramayana=ramayana_version)

    query = "What is the story of Ahalya?"
    results = embedding_store.get_query_results(query)

    for result in results:
        print(f"Document: {result['document']}, Metadata: {result['metadata']}, Distance: {result['distance']}")