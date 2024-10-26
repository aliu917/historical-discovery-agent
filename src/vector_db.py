import os
from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import json
from prompts import RERANK_PROMPT
import openai

class GPTQuery:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        openai.api_key = os.environ["OPENAI_API_KEY"]
        self.context = [] # Later if we want to do multiturn conversations

    def query(self, prompt, max_tokens=500, use_context=False):
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages= [*self.context, {"role": "user", "content": prompt}] if use_context \
                                        else [{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0,
                n=1,
            )
            breakpoint()
            return response.choices[0].message.content
        except Exception as e:
            print("Error querying GPT-4:", e)
            return None


class VectorDB:
    def __init__(self, json_doc_fpath) -> None:
        self._format_documents(json_doc_fpath)
        self._embed()

    def _format_documents(self, json_doc_fpath):
        documents = []

        with open(json_doc_fpath, 'r') as f:
            for line in f:
                chapter = json.loads(line.strip())
                chapter_doc = Document(chapter['content'])
                for key in ['id', 'document_title', 'full_section_title']:
                    chapter_doc.metadata[key] = chapter[key]
                documents.append(chapter_doc)
        
        self.documents = documents

    def _embed(self):
        self.db = Chroma.from_documents(self.documents, OpenAIEmbeddings())

    def query(self, query_text : str, k : int = 10, use_rerank = True):
        docs = self.db.similarity_search(query_text, k=k)
        breakpoint()
        all_content = "\n".join([d.page_content for d in docs])
        if use_rerank and k > 1:
            convo = GPTQuery()
            response = convo.query(RERANK_PROMPT(query_text, all_content))
            return response
        return docs[:k]



if __name__ == '__main__':
    vdb = VectorDB(json_doc_fpath='gha_jsonl/final.jsonl')
    query = "liquor and alcohol"
    print(vdb.query(query, k=10))