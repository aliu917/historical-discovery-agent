from vector_db import GPTQuery
from genie_search import *
from prompts import *
from knowledge_extract import extract_hypotheses
from output_utils import *

gpt_obj = GPTQuery()


def find_compare_texts(topic : str, log_outputs : bool = True):
    print("querying topic:", topic)
    write_obj = OutputWriter(run_name, topic, log_outputs)

    print("extracting knowledge from TAT")
    hypotheses_list, all_hh_mappings, low_level_citation = extract_hypotheses(topic, write_obj)

    print("Extracting from GHA and comparing output")
    hh_observations = {}
    for hh_claim, ll_ids in all_hh_mappings.items():
        query = hh_claim
        result_chunks = gha_request(query, requery=True, gpt_obj=gpt_obj)[0]['results'][:20]

        if not result_chunks:
            print("GHA did not find results")
            hh_gha_cmp = f'The General History of Africa has no information related to "{hh_claim}" or the overall topic of {topic}.'
        else:
            write_obj.append_hh_gha(hh_claim, result_chunks)

            prompt = HH_COMPARE_PROMPT(hh_claim, result_chunks, "General History of Africa textbook")
            hh_gha_cmp = gpt_obj.query(prompt)

        # Extract details from relevant TAT chunks to retrieve more TAT details for final output
        tat_chunks = []
        for ll_id in ll_ids:
            tat_chunks.append(low_level_citation[ll_id])
        prompt = HH_COMPARE_PROMPT(hh_claim, tat_chunks, "African Times news articles")
        hh_tat_cmp = gpt_obj.query(prompt)

        prompt = HH_COMBINE_PROMPT(hh_claim, hh_gha_cmp, hh_tat_cmp)
        final_result = gpt_obj.query(prompt)

        write_obj.append_final_cmp(hh_claim, hh_gha_cmp, hh_tat_cmp, final_result)

    print()

if __name__ == '__main__':
    run_name = "v1"
    assert_run_path(run_name)

    query_topics = [
        "role of alcohol in Africa",
        "proponents of formation of Israel",
        "history of Kumasi",
        "Fanti confederation",
    ]
    for query in query_topics:
        find_compare_texts(query, True)