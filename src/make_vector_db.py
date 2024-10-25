import os
from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import json

# could rerank with gpt
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

    def query(self, query_text, k = 1):
        docs = self.db.similarity_search(query_text)
        return docs[:k]

if __name__ == '__main__':
    vdb = VectorDB(json_doc_fpath='gha_jsonl/final.jsonl')
    query = "Who were the boers and what role did they play in South Africa?"
    print(vdb.query(query))