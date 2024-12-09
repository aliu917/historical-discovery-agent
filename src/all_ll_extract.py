from genie_search import african_times_request
from prompts import *
from knowledge_extract import clean_list_hypotheses
from utils import *
import ast
import re
import json
from collections import OrderedDict
import argparse

gpt_obj = GPTQuery()


def extract_all_tat(write_obj, source):
    low_level_citation = {}
    all_ll = []

    id = 0

    for chunk in read_jsonl(source):
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
                ("ll", ll[:-1]),
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
    w_file = open("../out/topic_v1/all/tat_ll_map2.jsonl", "w")
    w_file2 = open("../out/topic_v1/all/tat_ll_test2", "w")
    for line in r_file:
        if len(line) == 1:
            next_chunk = False
            continue
        elif "Extracting low level hypotheses from TAT chunk" in line:
            next_chunk = True
            next_ll = False
        elif "Found low level hypotheses" in line:
            next_ll = True
            next_chunk = False
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
            w_file2.write(line)
            id += 1
        else:
            next_chunk=False
            next_ll = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="OCR script input.")
    parser.add_argument('-r', '--run_name', type=str, required=True, help='The name of the run, which will define the output path where logged results are saved.')
    parser.add_argument('-p', '--primary_source', type=str, default='../tat/the_african_times_articles.jsonl', help='The name of the run, which will define the output path where logged results are saved.')
    args = parser.parse_args()

    write_obj = OutputWriter(args.run_name, log=True)
    extract_all_tat(write_obj, args.primary_source)
    remap()