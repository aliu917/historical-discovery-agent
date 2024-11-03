from vector_db import VectorDB, GPTQuery
from genie_search import *
from prompts import *
from knowledge_extract import extract_hypotheses

vdb = VectorDB(json_doc_fpath='../gha_jsonl/chapters_200.jsonl')
gpt_obj = GPTQuery()

def compare_texts(topic : str):
    gha_result = vdb.query(topic, k=20, verbose=False)
    gha_remove_commentary = [x for x in gha_result.split("\n") if "**" in x]
    gha_text_only = "\n\n".join([rc.split("**")[-1] for rc in gha_remove_commentary])
    afr_times_json = african_times_request(topic, 2)
    afr_times_content = [x['content'] for x in afr_times_json[0]['results']]
    afr_times_text = "\n\nAnother Letter to the African times: ".join(afr_times_content)

    prompt = COMPARE_TEXTS_PROMPT(topic, gha_text_only, afr_times_text)
    res = gpt_obj.query(prompt) 

    return res


def find_compare_texts(topic : str):
    hypotheses_list, all_hh_mappings = extract_hypotheses(topic)
    hh_observations = {}
    for hh_claim in all_hh_mappings:
        print(f"High-level topic related to {topic}: {hh_claim}")
        # print()
        # print("African times claims:")
        afr_times_claims = all_hh_mappings[hh_claim]
        # for claim in afr_times_claims:
            # print("\t * " + claim)

        print()
        result_chunks = gha_request(hh_claim)[0]['results'][:5]
        if not result_chunks:
            print("did not match any GHA chunks. Re-querying with overall topic string")
            result_chunks = gha_request(topic)[0]['results'][:5]

        print("GHA found results")
        for result in result_chunks:
            print(result)

        print()
        # print()
        all_observations = ""
        for chunk in result_chunks:
            content = chunk["content"]
            similar_prompt = FIND_COMPARE_PROMPT(hh_claim, afr_times_claims, content, "similarities")
            similar_res = gpt_obj.query(similar_prompt)
            diff_prompt = FIND_COMPARE_PROMPT(hh_claim, afr_times_claims, content, "differences")
            diff_res = gpt_obj.query(diff_prompt)

            all_observations += similar_res + "\n" + diff_res + "\n"

        if not result_chunks:
            claims = "\n".join(afr_times_claims)
            all_observations = f"We found the following observations related to {hh_claim} from the African Times but nothing in the General History of Africa:{claims}"

        print("raw observations: ", all_observations)
        print()
        print()
        result = gpt_obj.query(SUMMARIZE_KEY_POINTS(all_observations, hh_claim))
        print(result)

        hh_observations[hh_claim] = result

    final = gpt_obj.query(SUMMARIZE_FINAL_KEY_POINTS(hh_observations, topic))
    return final


if __name__ == '__main__':
    query = "alcohol"
    res = find_compare_texts(query)
    print()
    print("###################")
    print()
    print(res)