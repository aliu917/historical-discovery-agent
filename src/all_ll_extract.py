from vector_db import GPTQuery
from genie_search import african_times_request
from prompts import *
from knowledge_extract import clean_list_hypotheses
from output_utils import *
import ast
import re
import json
from collections import OrderedDict


gpt_obj = GPTQuery()


def read_jsonl(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            yield json.loads(line.strip())


def extract_all_tat(write_obj):
    low_level_citation = {}
    all_ll = []

    id = 0

    for chunk in read_jsonl("../tat/the_african_times_articles.jsonl"):
        prompt = EXTRACT_HYPOTHESES_FROM_CHUNK(chunk['content_string'])
        response = gpt_obj.query(prompt)
        response = clean_list_hypotheses(response)
        write_obj.append_extract(chunk=chunk, ll=response)
        chunk_ll = []
        for k in range(len(response)):
            ll = response[k]
            if not len(ll):
                continue
            low_level_citation[len(all_ll)] = chunk
            od = OrderedDict([
                ("id", id),
                ("ll", line[:-1]),
                ("chunk", chunk)
            ])
            chunk_ll.append(json.dumps(od))
            id += 1
            all_ll.append(ll)
        write_obj.append_extract(filename="tat_ll_map", ll=chunk_ll)
    write_obj.append_extract(filename="tat_ll", ll=all_ll)


def remap():
    id = 0
    chunk = ""
    next_chunk = False
    next_ll = False
    r_file = open("../out/topic_v1/all/tat_ll_extract", 'r')
    w_file = open("../out/topic_v1/all/tat_ll_map.jsonl", "w")
    for line in r_file:
        if len(line) == 1:
            next_chunk = False
            next_ll = False
        elif next_chunk:
            chunk = line[:-1]
            next_chunk = False
        elif next_ll:
            od = OrderedDict([
                ("id", id),
                ("ll", line[:-1]),
                ("chunk", chunk)
            ])
            w_file.write(json.dumps(od) + '\n')
            id += 1
        elif "Extracting low level hypotheses from TAT chunk" in line:
            next_chunk = True
        elif "Found low level hypotheses" in line:
            next_ll = True
        else:
            next_chunk=False
            next_ll = False


if __name__ == '__main__':
    # write_obj = OutputWriter("topic_v1", "all", True)
    # extract_all_tat(write_obj)
    remap()