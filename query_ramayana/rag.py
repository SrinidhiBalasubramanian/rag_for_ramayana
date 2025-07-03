from openai import OpenAI

from config import OPENAI_API_KEY, EmbeddingResult, Prompts, FinalResponse
from utils import Tools

logger = Tools.setup_logger("query_ramayana")
safe_run = Tools.safe_run

class RAG:
    def __init__(self, query):
        self.query = query
        self.openai = OpenAI(api_key = OPENAI_API_KEY)

    @safe_run(default_return=Prompts.RAG_PROMPT)
    def get_prompt(self, 
                   valmiki_results: EmbeddingResult, 
                   tulsidas_results: EmbeddingResult) -> str:
        
        valmiki_trans = {}
        tulsi_trans = {}
        count = len(valmiki_results)
        for ix, (v_result, t_result) in enumerate(zip(valmiki_results, tulsidas_results)):
            valmiki_trans[ix] = str(v_result.document)
            tulsi_trans[ix] = str(t_result.document)
        contexts = {
            "query": self.query,
            "no_contexts": count,
            "valmiki_extract": str(valmiki_trans),
            "tulsidas_extract": str(tulsi_trans),
        }

        return Prompts.RAG_PROMPT.format(**contexts)

    @safe_run(default_return="")
    def get_answer(self, prompt: str) -> str:

        completion = self.openai.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a traditional expert on Ramayana. Assist in the below mentioned tasks"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            response_format=FinalResponse,
            temperature=0
        )

        return completion
    
    def parse_response(self, response) -> str:

        response_parsed = response.choices[0].message.parsed

        answer = response_parsed.response
        token_usage = response_parsed.usage.total_tokens if response.usage else 0

        return answer.strip(), token_usage

    @safe_run(default_return=("An error occurred while processing your query.", 0))
    def run(self, 
            valmiki_results: EmbeddingResult, 
            tulsidas_results: EmbeddingResult) -> str:
        
        prompt = self.get_prompt(valmiki_results, tulsidas_results)
        response = self.get_answer(prompt)
        return response