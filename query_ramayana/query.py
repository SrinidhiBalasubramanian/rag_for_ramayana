import ast
from typing import List, Dict

from query_ramayana.rag import RAG
from query_ramayana.embeddings import EmbeddingStore
from query_ramayana.data_processing import DataProcessing

from config import RAMAYANA_VERSIONS, Prompts, LogDetails
from utils import Tools, DB

logger = Tools.setup_logger("query_ramayana")
safe_run = Tools.safe_run
parse = Tools.parse

class Query:
    def __init__(self, query):
        self.query = query
        self.data_processing = DataProcessing()

    def get_sources(self, context_ids: str, embedding_results, ramayana_version: RAMAYANA_VERSIONS) -> str:
        context_indices = parse(context_ids)
        verse_indices = []
        for index in context_indices:
            verse_indices += parse(embedding_results[int(index)]["verse_indices"])         
        verses = ""
        if verse_indices:
            for index in verse_indices:
                verse = self.data_processing.retrive_verse(index, ramayana_version)
                verses += f"{verse}\n\n"

            return verses
        
        else:
            return ""
        
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
        response_parsed = rag_response.choices[0].message.parsed
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
            answer=f"{response_parsed.answer} \n\n{response_parsed.valmiki_sources}\n\n{response_parsed.tulsidas_sources}",
            token_usage=token_usage
        )

        DB().log_usage(log_details=log_details)

    def parse_response(self, response):

        response_parsed = response.choices[0].message.parsed

        answer = response_parsed.answer
        valmiki_sources = response_parsed.valmiki_sources
        tulsidas_sources = response_parsed.tulsidas_sources
        token_usage = response.usage.total_tokens if response.usage else 0

        return answer.strip(), valmiki_sources, tulsidas_sources, token_usage

    @safe_run(default_return=("An error occurred while processing your query.", "", ""))
    def run(self):

        valmiki_embedding = EmbeddingStore(
            ramayana=RAMAYANA_VERSIONS.VALMIKI
        )
        tulsidas_embedding = EmbeddingStore(
            ramayana=RAMAYANA_VERSIONS.TULSIDAS
        )

        valmiki_results = valmiki_embedding.get_query_results(self.query)
        tulsidas_results = tulsidas_embedding.get_query_results(self.query)

        rag_response = RAG(self.query).run(
            valmiki_results, 
            tulsidas_results
        )

        answer, valmiki_source_ids, tulsidas_source_ids, token_usage = self.parse_response(rag_response)

        self.log(valmiki_results, tulsidas_results, rag_response, token_usage)  

        valmiki_sources = self.get_sources(
            valmiki_source_ids,
            [result.metadata for result in valmiki_results], 
            RAMAYANA_VERSIONS.VALMIKI
        )
        tulsidas_sources = self.get_sources(
            tulsidas_source_ids,
            [result.metadata for result in tulsidas_results],
            RAMAYANA_VERSIONS.TULSIDAS
        )

        return answer, valmiki_sources, tulsidas_sources