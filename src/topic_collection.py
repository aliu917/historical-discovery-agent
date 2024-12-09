import text_lloom.workbench as wb
import os
import pandas as pd
from utils import *
from prompts import *
from tqdm import tqdm
import json
import ast
import argparse

gpt_obj = GPTQuery()


def topic_assign(run_name, topic1_path, topic2_path, hh_path='hh_final.csv', save_path='hh_topic.csv'):
    dir = f"../out/{run_name}/overall/"
    hh_df = pd.read_csv(dir + hh_path)

    save_df = hh_df
    if save_path != hh_path:
        save_df = hh_df[["hh"]]
    if not os.path.exists(save_path):
        save_df["topic1"] = None
        save_df["topic2"] = None

    with open(f"{topic1_path}/topic1.json", 'r') as file:
        topics1 = json.load(file)
    with open(f"{topic2_path}/topic2.json", 'r') as file:
        topics2 = json.load(file)

    for index, row in tqdm(hh_df.iterrows(), total=len(hh_df)):
        hh_claim = row["hh"]

        topic1_missing = "topic1" not in row or row["topic1"] not in topics1
        topic2_missing = "topic2" not in row or not row["topic2"]

        if topic1_missing or row["topic2"] not in topics2[row["topic1"]]:
            prompt = HH_TOPIC(hh_claim, topics1)
            response = gpt_obj.query(prompt)
            response = response.strip().strip('"').strip()
            save_df.at[index, "topic1"] = response
        row_topic1 = save_df.at[index, "topic1"]
        if row_topic1 not in topics1:
            continue
        next_topics = topics2[row_topic1]
        if topic2_missing or row["topic2"] not in topics2[row_topic1]:
            prompt = HH_TOPIC(hh_claim, next_topics)
            response = gpt_obj.query(prompt)
            response = response.strip().strip('"').strip()
            save_df.at[index, "topic2"] = response
    save_df.to_csv(f"../out/{run_name}/overall/" + save_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="OCR script input.")
    parser.add_argument('-r', '--run_name', type=str, required=True,
                        help='The name of the run, which will define the output path where logged results are saved.')
    parser.add_argument('-t', '--topic_path', type=str, default="../out/v2_cluster_single_final/overall",
                        help='The path to pre-computed topic values.')
    args = parser.parse_args()

    run_name = args.run_name
    topic_path = args.topic_path

    topic_assign(run_name, topic_path, topic_path, hh_path='hh_final.csv', save_path='hh_topic.csv')