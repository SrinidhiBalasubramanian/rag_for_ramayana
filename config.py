import os
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

import streamlit as st
from dotenv import load_dotenv
from typing import Dict, List
from urllib.parse import quote_plus

try:
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
    USERNAME = st.secrets.get("MONGODB_USERNAME")
    PASSWORD = st.secrets.get("MONGODB_PASSWORD")
except:
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    USERNAME = os.getenv("MONGODB_USERNAME")
    PASSWORD = os.getenv("MONGODB_PASSWORD")

class MONGO_DB:
    URL = f"mongodb+srv://{quote_plus(USERNAME)}:{quote_plus(PASSWORD)}@cluster0.d2ydjrc.mongodb.net"
    DATABASE = "rag_ramayana"
    COLLECTION = "tracker_ask_ramayana_logs"

# Literal Constants
class RAMAYANA_VERSIONS:
    VALMIKI = "Valmiki"
    TULSIDAS = "Tulsidas"

class FinalResponse(BaseModel):
    answer: str = ""
    valmiki_sources: list[str] = Field(default_factory=list)
    tulsidas_sources: list[str] = Field(default_factory=list)

@dataclass
class EmbeddingResult:
    document: str
    metadata: dict
    distance: float

@dataclass
class Verses:
    _id: str
    verse: str

@dataclass
class LogDetails:
    query: str = ""
    embedding_results: Dict[RAMAYANA_VERSIONS, list] = field(default_factory=dict)
    answer: str = ""
    token_usage: int = 0

KANDA_IDS = { 
    "Valmiki" : {
        "Bala" : 1,
        "Ayodhya" : 2,
        "Aranya" : 3,
        "Kishkindha" : 4,
        "Sundara" : 5,
        "Yuddha" : 6
    },
    
    "Tulsidas" : {
      "Baal Kaand" : 1,
      "Ayodhya Kaand" : 2,
      "Aranya Kaand": 3,
      "Kishkindha Kaand" : 4,
      "Sunder Kaand" : 5,
      "Lanka Kaand" : 6,
      "Uttar Kaand" : 7
    }
}

class Prompts:
    RAG_PROMPT = """Given the following query by a user on Ramayana, answer the question based on the extracts from Valmiki Ramayana and Tulsidas Ramayana.
    The extracts are top-{no_contexts} verse matches from the respective Ramayana versions extracted automatically by a retriever system to aid you.
    If unspecified, use both Valmiki and Tulsidas Ramayana extracts and make sure to mention the version of Ramayana you are referring to in your answer.
    If any of the extracts do not contain information relevant to the query, mention that "Information was not found in version __" for the query.
    If the query is wrt to a specific version of Ramayana, use only the extracts from that version and ignor the extract from the other version.
    Make sure to be very respectful and traditional in your answer. Be aware of sanskrit non-translatables, use IAST when possible, and let your answer sound like it is coming from a traditional native speaker on Ramayana.
    
    Query: {query}
    Valmiki Ramayana Extracts: {valmiki_extract}
    Tulsidas Ramayana Extracts: {tulsidas_extract}  

    Return the following:
    response: A detailed and specific answer to the query based on the extracts provided. Include as many details and intricacies as available from the sources. Only give a natural language answer, do not include any verse or verse id in the response.
    valmiki_sources: The list of select ids from extracts of Valmiki Ramayana that are highly relevant to the response generated ["verse_id1", verse_id2", ...]. If no verses are relevant, return an empty list.
    tulsidas_sources: The list of select ids from extracts of Tulsidas Ramayana that are highly relevant to the response generated ["verse_id1", verse_id2", ...]. If no verses are relevant, return an empty list.
    """

    OUTPUT_FORMAT = """{response} \n
    Relevant extracts from Valmiki Ramayana: \n
    {valmiki_sources}
    Relevant extracts from Tulsidas Ramayana: \n
    {tulsidas_sources}
    """

if __name__ == "__main__":
    from pymongo import MongoClient
    client = MongoClient(MONGO_DB.URL)
    db = client[MONGO_DB.DATABASE]
    collection = db[MONGO_DB.COLLECTION]
    log_entry = {
            "timeStamp": "03-07-2025",
            "query": "sample query",
            "embeddingResults": "sample embedding",
            "output": "sample output",
            "tokenUsage": 0
        }
    collection.insert_one(log_entry)
    print("Inserted sampple log entry into MongoDB collection.")