from vector_db import VectorDB, GPTQuery
from genie_search import post_request
from prompts import COMPARE_TEXTS_PROMPT

vdb = VectorDB(json_doc_fpath='../gha_jsonl/chapters_200.jsonl')
gpt_obj = GPTQuery()

def compare_texts(topic : str):
    gha_result = vdb.query(topic, k=20, verbose=False)
    gha_remove_commentary = [x for x in gha_result.split("\n") if "**" in x]
    gha_text_only = "\n\n".join([rc.split("**")[-1] for rc in gha_remove_commentary])
    afr_times_json = post_request(topic, 2)
    afr_times_content = [x['content'] for x in afr_times_json[0]['results']]
    afr_times_text = "\n\nAnother Letter to the African times: ".join(afr_times_content)

    prompt = COMPARE_TEXTS_PROMPT(topic, gha_text_only, afr_times_text)
    res = gpt_obj.query(prompt) 

    return res



if __name__ == '__main__':
    query = "liquor and alcohol"
    res = compare_texts(query)
    print(res)