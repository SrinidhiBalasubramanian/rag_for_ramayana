import ast
from typing import List, Dict

from query_ramayana.rag import RAG
from query_ramayana.embeddings import EmbeddingStore
from query_ramayana.data_processing import DataProcessing

from config import RAMAYANA_VERSIONS, Prompts, LogDetails
from utils import Tools, DB

logger = Tools.setup_logger("query_ramayana")
safe_run = Tools.safe_run

class Query:
    def __init__(self, query):
        self.query = query
        self.data_processing = DataProcessing()

    def get_sources(self, metadata: List[Dict], ramayana_version: RAMAYANA_VERSIONS) -> str:
        verse_indices = ast.literal_eval(metadata[0]["verse_indices"])
        verses = ""
        for index in verse_indices:
            verse = self.data_processing.retrive_verse(index, ramayana_version)
            verses += f"{verse}\n\n"

        return verses
        
    def make_output(self, 
                    rag_response: str, 
                    valmiki_sources: str, 
                    tulsidas_sources: str) -> str:

        contexts = {
            "response": rag_response,
            "valmiki_sources": valmiki_sources,
            "tulsidas_sources": tulsidas_sources,
        }
        return Prompts.OUTPUT_FORMAT.format(**contexts)
    
    def log(self, valmiki_results, tulsidas_results, rag_response, token_usage):
        embedding_results = {
            RAMAYANA_VERSIONS.VALMIKI: [
                {
                    "document": result.document,
                    "metadata": result.metadata,
                    "distance": result.distance
                } for result in valmiki_results
            ],
            RAMAYANA_VERSIONS.TULSIDAS: [
                {
                    "document": result.document,
                    "metadata": result.metadata,
                    "distance": result.distance
                } for result in tulsidas_results
            ]
        }
        log_details = LogDetails(
            query=self.query,
            embedding_results= embedding_results,
            answer=rag_response,
            token_usage=token_usage
        )

        DB().log_usage(log_details=log_details)

    @safe_run(default_return="An error occurred while processing your query.")
    def run(self) -> str:

        valmiki_embedding = EmbeddingStore(
            ramayana=RAMAYANA_VERSIONS.VALMIKI
        )
        tulsidas_embedding = EmbeddingStore(
            ramayana=RAMAYANA_VERSIONS.TULSIDAS
        )

        valmiki_results = valmiki_embedding.get_query_results(self.query)
        tulsidas_results = tulsidas_embedding.get_query_results(self.query)

        rag_response, token_usage = RAG(self.query).run(
            valmiki_results, 
            tulsidas_results
        )

        self.log(valmiki_results, tulsidas_results, rag_response, token_usage)  

        valmiki_sources = self.get_sources(
            [result.metadata for result in valmiki_results], 
            RAMAYANA_VERSIONS.VALMIKI
        )
        tulsidas_sources = self.get_sources(
            [result.metadata for result in tulsidas_results], 
            RAMAYANA_VERSIONS.TULSIDAS
        )

        final_response = self.make_output(
            rag_response, 
            valmiki_sources, 
            tulsidas_sources
        )

        return final_response