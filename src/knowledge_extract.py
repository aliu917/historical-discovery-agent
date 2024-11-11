from vector_db import GPTQuery
from genie_search import african_times_request
from prompts import *
import ast
import re

gpt_obj = GPTQuery()


def extract_hypotheses(topic, write_obj):
    low_level_citation = {}
    all_hh_mappings = {}
    all_hypotheses = []
    chunks_all = african_times_request(topic)
    if not isinstance(topic, list):
        topic = [topic]
    for i, t in enumerate(topic):
        chunks = chunks_all[i]['results']
        for j, chunk in enumerate(chunks):
            prompt = EXTRACT_HYPOTHESES_FROM_CHUNK(chunk['content'], t)
            response = gpt_obj.query(prompt)
            response = clean_list_hypotheses(response)
            write_obj.append_extract(chunk=chunk, ll=response)
            cleaned_reponses = []
            for k in range(len(response)):
                if not len(response[k]):
                    continue
                pattern = r'^\d+\.'
                ll_id = len(low_level_citation)
                cleaned_res = re.sub(pattern, '', response[k].strip())
                cleaned_res = f"[id: {ll_id}] {cleaned_res.replace('*', '')}"
                cleaned_reponses.append(cleaned_res)
                low_level_citation[ll_id] = chunk
            all_hypotheses += cleaned_reponses

        hh_mapping = get_high_level_hypotheses(all_hypotheses)
        all_hh_mappings.update(hh_mapping)

    write_obj.append_extract(filename="tat_ll", ll=all_hypotheses)
    write_obj.write_hh(all_hh_mappings, all_hypotheses)

    return all_hypotheses, all_hh_mappings, low_level_citation


def clean_list_hypotheses(response):
    response_list = list(filter(lambda x: len(x) > 5, response.split('\n')))
    response_list = [x.split(':')[-1].strip() for x in response_list]
    return response_list


# requery
def get_high_level_hypotheses(hypothesis_list):
    prompt = EXTRACT_COMMON_CLAIMS(hypothesis_list)
    response = gpt_obj.query(prompt)

    hypothesis_mapping = {}
    for common_hypothesis in response.split("*")[1:]:
        try:
            hypothesis, ll_ids = common_hypothesis.split("ids:") # TODO: this is trusting GPTs output a lot
            hypothesis = hypothesis.strip().split('\n')[0]
            ll_ids = ast.literal_eval(ll_ids.split('\n')[0].strip())
            hypothesis_mapping[hypothesis] = ll_ids
        except:
            print(f"Error with common_hypothesis {common_hypothesis}, breaking")
            breakpoint()

    return hypothesis_mapping


def pprint(hypothesis_mapping):
    for h in hypothesis_mapping:
        print(h)
        for x in hypothesis_mapping[h]:
            print("\t * " + x)


if __name__ == '__main__':
    hypotheses_list, all_hh_mappings, low_level_citation = extract_hypotheses("alcohol")
    for h in hypotheses_list:
        print(h)
    print()
    # hh_mapping = get_high_level_hypotheses(hypotheses_list)
    pprint(all_hh_mappings)
    pprint(low_level_citation)
