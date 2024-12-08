import pandas as pd
import json
import os


def clean_df(df):
    df = df[df["ok"] == True]
    df = df[df["tat_orig"].apply(lambda x: len(x) > 1)]
    df = df[df["hh"].apply(lambda x: "[not african]" not in x)]
    return df


def run(run_name, hh_final='hh_final.csv', hh_topic='hh_topic.csv', hh_source='hh_sources.csv'):
    load_dir = f"../out/{run_name}/overall/"
    save_dir = f"../out/{run_name}/csv_out/"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    hh_final_df = pd.read_csv(load_dir + hh_final)
    hh_topic_df = pd.read_csv(load_dir + hh_topic)
    hh_sources_df = pd.read_csv(load_dir + hh_source)

    with open(f"../out/{run_name}/overall/topic1.json", 'r') as file:
        topics1 = json.load(file)
    with open(f"../out/{run_name}/overall/topic2.json", 'r') as file:
        topics2 = json.load(file)

    hh_joined = hh_final_df.merge(hh_topic_df, on="hh", suffixes=('_final', '_topic')).merge(hh_sources_df, on="hh", suffixes=('', '_sources'))
    hh_joined = clean_df(hh_joined)
    for topic1 in topics1:
        t1_df = hh_joined[hh_joined["topic1"] == topic1]
        t1_save_dir = save_dir + topic1.lower().replace(" ", "_")
        if not os.path.exists(t1_save_dir):
            os.mkdir(t1_save_dir)
        for topic2 in topics2[topic1]:
            t2_df = t1_df[t1_df["topic2"] == topic2]
            if len(t2_df) > 1:
                t2_save_path = t1_save_dir + "/" + topic2.lower().replace(" ", "_") + ".csv"
                print("saving to: ", t2_save_path)
                t2_df.to_csv(t2_save_path)


if __name__ == '__main__':
    run_name = "v2_cluster_single_final"
    run(run_name)