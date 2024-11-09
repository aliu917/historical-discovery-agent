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
    def __init__(self, model="gpt-4o"):
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