from genie_search import african_times_request
from prompts import *
from all_ll_clustering import load_ll
import ast
from tqdm import tqdm
import re
from utils import read_jsonl, GPTQuery
import json

gpt_obj = GPTQuery()


def extract_and_filter_numbers(text):
    # Find all numbers within brackets
    pattern = r'\[(\d+(?:\.\d+)?)\]'
    matches = re.findall(pattern, text)
    return [int(num) for num in matches]


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

    breakpoint()
    write_obj.append_extract(filename="tat_ll", ll=all_hypotheses)
    write_obj.write_hh(all_hh_mappings, all_hypotheses)

    return all_hypotheses, all_hh_mappings, low_level_citation


def extract_hypotheses_generator(topic, write_obj):
    all_hypotheses, all_hh_mappings, low_level_citation = extract_hypotheses(topic, write_obj)
    for hh_claim, ll_ids in all_hh_mappings.items():
        yield hh_claim, ll_ids, low_level_citation
        
        
def low_level_citations_all(ll_citation_path):
    low_level_unformatted = read_jsonl(ll_citation_path)
    low_level_citation = {}
    for ll_uf in low_level_unformatted:
        low_level_citation[ll_uf['id']] = ast.literal_eval(ll_uf['chunk'])
    return low_level_citation


def extract_hypotheses_from_cluster_generator(cluster_map_path, low_level_citation, write_obj):
    all_hh_mappings = {}
    with open(cluster_map_path, 'r') as f:
        ll_clusters = json.load(f)
    # all_hypotheses = load_ll()[1:]
    i = 0
    for cluster_id, ll_claims in tqdm(ll_clusters.items()):
        if i > 20:
            break
        i+= 1
        ll_clustered_formatted = [f"[id: {ll_claim['ll_id']}] {ll_claim['ll']}" for ll_claim in ll_claims]
        # hh_mapping = get_high_level_hypotheses(ll_clustered_formatted)
        hh_mapping = get_single_high_level_hypotheses(ll_clustered_formatted, [ll_claim['ll_id'] for ll_claim in ll_claims])
        write_obj.append_hh(hh_mapping, [ll_claim['ll'] for ll_claim in ll_claims])
        for hh_claim, ll_ids in hh_mapping.items():
            yield hh_claim, ll_ids, low_level_citation


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
        if not common_hypothesis:
            continue
        try:
            hypothesis, ll_ids = common_hypothesis.split("ids:") # TODO: this is trusting GPTs output a lot
            if not ll_ids:
                ids = extract_and_filter_numbers(common_hypothesis)
                if not ids:
                    raise Exception("Did not have any ids in format")
                hypothesis = get_single_high_level_hypotheses([hypothesis_list[i] for i in ids])
                ll_ids = str(ids)
            hypothesis = hypothesis.strip().split('\n')[0]
            ll_ids = ast.literal_eval(ll_ids.split('\n')[0].strip())
            hypothesis_mapping[hypothesis] = ll_ids
        except:
            print(f"Error with common_hypothesis {common_hypothesis}, breaking")
            breakpoint()

    return hypothesis_mapping


def get_single_high_level_hypotheses(hypothesis_list, ids=None):
    prompt = EXTRACT_ONE_COMMON_CLAIM(hypothesis_list)
    response = gpt_obj.query(prompt)
    if ids:
        return {response : ids}
    return response
    



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
