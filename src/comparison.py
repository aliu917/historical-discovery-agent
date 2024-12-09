from genie_search import *
from prompts import *
from knowledge_extract import extract_hypotheses_generator, extract_hypotheses_from_cluster_generator, low_level_citations_all
from utils import *
import re
from tqdm import tqdm
import argparse

gpt_obj = GPTQuery()


def check_query(query):
    if len(query) > 512:
        print("Shortening original query:")
        print("\t- " + query)
        print("\t- " + query[:512])
        print()
        query = query[:512]
    if "[not african]" in query:
        print("Query not relevant to African history:", query)
        print()
        return query, False
    return query, True


def get_tat_chunks(low_level_citation, ll_ids, query=""):
    tat_chunks = []
    chunk_set = set()
    for ll_id in ll_ids:
        ll_citation = low_level_citation[ll_id]
        if "content_string" in ll_citation:
            chunk_str = ll_citation["content_string"]
        else:
            chunk_str = ll_citation["content"]
        if chunk_str in chunk_set:
            continue
        if "content_string" in ll_citation:
            low_level_citation[ll_id]["content"] = low_level_citation[ll_id].pop("content_string")
        tat_chunks.append(low_level_citation[ll_id])
        chunk_set.add(chunk_str)

    # Augment TAT with more chunks to find additional relevant unclustered chunks.
    added_chunks = []
    if query:
        tat_orig = [c["content"] for c in tat_chunks]
        result_chunks = african_times_request(query, num_blocks=15)[0]['results'][:20]
        for chunk in result_chunks:
            if chunk["content"] not in tat_orig:
                tat_chunks.append(chunk)
                added_chunks.append(chunk)
    return tat_chunks, added_chunks


def extract_citations(text):
    pattern = r'\[(\d+)\]'
    numbers = re.findall(pattern, text)
    return [int(num) for num in numbers]


"""
Compare the different perspectives between The African Times (TAT) and General History of Africa (GHA) on `topic`
If topic is not provided (empty string) then cluster_map_path and ll_citation_path must be given. The cluster_map is a 
json file that aggregates all low level hypotheses from TAT. The output will be an aggregation of all 
similarities and differences between TAT and GHA
"""
def find_compare_texts(topic : str = "", run_name : str = "run1", log_outputs : bool = True, short_cite : bool = False, cluster_map_path : str = None, ll_citation_path : str = None):
    print("querying topic:", topic if topic else "overall")
    write_obj = OutputWriter(run_name, topic if topic else "overall", log_outputs)

    print("extracting knowledge from TAT")
    if topic:
        h_generator = extract_hypotheses_generator(topic, write_obj)
    else:
        low_level_citation = low_level_citations_all(ll_citation_path)
        h_generator = extract_hypotheses_from_cluster_generator(cluster_map_path, low_level_citation, write_obj)

    print("Extracting from GHA and comparing output")
    for hh_claim, ll_ids, low_level_citation in tqdm(h_generator):
        query = hh_claim
        query, ok = check_query(query)
        result_chunks = gha_request(query, requery=True, gpt_obj=gpt_obj)[0]['results'][:20]

        if not result_chunks:
            print("GHA did not find results")
            hh_gha_cmp = f'The General History of Africa has no information related to "{hh_claim}" or the overall topic of {topic}.'
        else:
            prompt = HH_COMPARE_PROMPT(hh_claim, result_chunks, "General History of Africa textbook", cite=short_cite)
            hh_gha_cmp = gpt_obj.query(prompt)
            citations = extract_citations(hh_gha_cmp) if short_cite else list(range(len(result_chunks)))
            citations = list(set(citations))

            write_obj.append_hh_gha(hh_claim, result_chunks, citations, ok=ok)

            if citations:
                result_chunks = [result_chunks[i] for i in citations]

        # Extract details from relevant TAT chunks to retrieve more TAT details for final output
        tat_chunks, added_chunks = get_tat_chunks(low_level_citation, ll_ids, query=query)
        orig_chunk_len = len(tat_chunks) - len(added_chunks)
        write_obj.append_hh_tat(hh_claim, tat_chunks, orig_chunk_len, ok=ok)
        prompt = HH_COMPARE_PROMPT(hh_claim, tat_chunks, "African Times news articles")
        hh_tat_cmp = gpt_obj.query(prompt)

        prompt = HH_COMBINE_PROMPT(hh_claim, hh_gha_cmp, hh_tat_cmp)
        final_result = gpt_obj.query(prompt)

        write_obj.log_final_code(hh_claim, final_result, hh_gha_cmp, hh_tat_cmp, result_chunks, tat_chunks, orig_chunk_len, ok=True)
        write_obj.append_final_cmp(hh_claim, hh_gha_cmp, hh_tat_cmp, final_result, ok=ok)
        write_obj.log_analysis_doc(hh_claim, final_result, result_chunks, tat_chunks, short_cite, ok=ok)

    print()
    write_obj.end_task()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="OCR script input.")
    parser.add_argument('-r', '--run_name', type=str, required=True,
                        help='The name of the run, which will define the output path where logged results are saved.')
    parser.add_argument('-c', '--cluster_map_path', type=str, default='../out/cluster_v2_attempt_bigger_clusters/final_cluster_map.json',
                        help='The path to the pre-computed low-level claim clusters.')
    parser.add_argument('-l', '--ll_map_path', type=str,
                        default='../tat/tat_ll_map.jsonl',
                        help='The path to the pre-computed low-level claims and chunk sources.')
    parser.add_argument('-t', '--seed_topic', type=str, default="",
                        help='A topic string to focus high-level claim and comparison on')
    args = parser.parse_args()

    run_name = args.run_name
    assert_run_path(run_name)

    find_compare_texts(args.seed_topic,
                       run_name=run_name,
                       log_outputs=True,
                       short_cite=False,
                       cluster_map_path=args.cluster_map_path,
                       ll_citation_path=args.ll_map_path)