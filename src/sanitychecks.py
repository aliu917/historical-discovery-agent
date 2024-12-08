from utils import *
from tqdm import tqdm
from collections import defaultdict
import matplotlib.pyplot as plt
import re
from prompts import SLAVERY_ANALYSIS_PROMPT

"""
Here we check that our low level hypotheses (tat/tat_ll_map.jsonl)
are consistent with the expectations of expert historians (Prof. Getz)
"""

gpt_obj = GPTQuery("gpt-4o-mini")

def get_date(ll_h):
    # lol imagine if I actually knew json parsing
    ind = ll_h['chunk'].rfind('issue_date')
    date_str = '{"' + f"{ll_h['chunk'][ind:]}"
    date_dict = json.loads(date_str.replace("\'", "\""))
    return date_dict['issue_date']

def colonization_mentions():
    year_to_mentions = defaultdict(int)
    use = "ll"
    for ll_h in tqdm(read_jsonl('../tat/tat_ll_map.jsonl')):
        if 'coloni' in ll_h[use].lower() or 'colony' in ll_h[use].lower():
            year = get_date(ll_h).split('_')[-1]
            year_to_mentions[int(year)] += 1
    
    plt.bar(year_to_mentions.keys(), year_to_mentions.values())
    plt.title("Mentions of Colonialism in The African Times hypotheses")
    plt.savefig('../out/sanity_checks/colonialism.png', dpi=640)

def israel_mentions():
    year_to_mentions = defaultdict(int)
    use = 'll'
    for ll_h in tqdm(read_jsonl('../tat/tat_ll_map.jsonl')):
        if 'israel' in ll_h[use].lower():
            year = get_date(ll_h).split('_')[-1]
            year_to_mentions[int(year)] += 1
    
    plt.clf()
    plt.bar(year_to_mentions.keys(), year_to_mentions.values())
    plt.title("Mentions of Israel in The African Times hypotheses")
    plt.savefig('../out/sanity_checks/israel.png', dpi=640)

def slavery_mentions():
    claims_to_year = defaultdict(list)
    for ll_h in tqdm(read_jsonl('../tat/tat_ll_map.jsonl')):
        year = int(get_date(ll_h).split('_')[-1])
        claims_to_year[year].append(ll_h['ll'])
    
    with open("../out/sanity_checks/slavery.md", 'w') as f:
        ...

    for k, v in tqdm(claims_to_year.items()):
        all_claims = "\n".join(v)
        prompt = SLAVERY_ANALYSIS_PROMPT(all_claims)
        response = gpt_obj.query(prompt)
        with open("../out/sanity_checks/slavery.md", 'a') as f:
            f.write(f"##{k}\n")
            f.write(response)



if __name__ == '__main__':
    colonization_mentions()
    israel_mentions()
    # slavery_mentions()