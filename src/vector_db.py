import os
from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import json
from prompts import *
import openai

class GPTQuery:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        openai.api_key = os.environ["OPENAI_API_KEY"]
        self.context = [] # Later if we want to do multiturn conversations

    def query(self, prompt, max_tokens=1000, use_context=False):
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages= [*self.context, {"role": "user", "content": prompt}] if use_context \
                                        else [{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0,
                n=1,
            )
            # breakpoint()
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
                for key in ['id', 'full_section_title']:
                    chapter_doc.metadata[key] = chapter[key]
                chapter_doc.metadata['document_title'] = chapter['document_title']
                documents.append(chapter_doc)
        
        self.documents = documents

    def _embed(self):
        self.db = Chroma.from_documents(self.documents, OpenAIEmbeddings())

    def additional_similarity(self, query_text : str, convo : GPTQuery, docs : list, k : int = 5):
        response = convo.query(FIND_SIMILAR_TOPIC_PROMPT(query_text)).strip().strip('"')
        additional_topics = response.split(':')[-1].split(',')[:10]
        print("also querying topics: ", response)

        # Note: this seems to help a decent percentage of the time for alcohol
        response_docs = self.db.similarity_search(response, k=20)
        for d in response_docs[:20]:
            if d not in docs:
                print(f"ID: {d.metadata['id']}; CONTENT: {d.page_content}")
                docs.append(d)
        print()

        # TODO: if this takes too long, can remove, it is very rarely helpful
        for topic in additional_topics:
            more_docs = self.db.similarity_search(topic.strip(), k=k)
            for doc in more_docs:
                if doc not in docs:
                    print(f"ID: {doc.metadata['id']}; CONTENT: {doc.page_content}")
                    docs.append(doc)
        print()
        return docs

    def query(self, query_text : str, k : int = 10, use_rerank = True, similar_topics=False, verbose=True):
        docs = self.db.similarity_search(query_text, k=k)
        if verbose:
            for d in docs[:k]:
                print(f"ID: {d.metadata['id']}; CONTENT: {d.page_content}")
            print()

        convo = GPTQuery()

        if similar_topics:
            docs = self.additional_similarity(query_text, convo, docs)

        # breakpoint()
        all_content = "\n".join([f"ID: {d.metadata['id']}; CONTENT: {d.page_content}" for d in docs])
        if use_rerank and k > 1:
            convo = GPTQuery()
            response = convo.query(RERANK_DOCS_PROMPT(query_text, all_content))
            return response
        return docs[:k]



if __name__ == '__main__':
    vdb = VectorDB(json_doc_fpath='../gha_jsonl/chapters_200.jsonl')
    query = "liquor and alcohol"
    result = vdb.query(query, k=20)
    print(result)
    # for x in result:
    #     print(x)


"""
ID: 460; CONTENT: They not only abandoned their ancestral traditions, beliefs and rituals, but used their political offices to impose the tenets of western, Christian civilization on their people. Their spirited efforts to banish the public use of alcoholic beverages were near-obsessive. They imposed stringent liquor laws which included a ban on the brewing of African beer.

ID: 274; CONTENT: brewers of an intoxicating drink called 'bouza'.

ID: 1259; CONTENT: cheap European goods - guns, alcoholic beverages, fabrics, cheap glassware, trinkets - being bartered for slaves, ivory, palm oil, rubber, ebony and redwood.

ID: 1217; CONTENT: Slaves were paid for with salt, fish, spirits, firearms, hats and beads, as well as iron, copper, and brass bars.

"""