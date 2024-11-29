import text_lloom.workbench as wb
import os
import pandas as pd


def load_hh(run_name):
    filename = f"../out/{run_name}/overall/tat_hh"
    f = open(filename, "r")
    hh_list = f.readlines()
    hh_list_cleaned = []
    for hh in hh_list:
        if len(hh) == 1:
            continue
        if "- " in hh[:2]:
            hh_list_cleaned.append(hh[2:-1])  # remove "- " and "\n"
        else:
            hh_list_cleaned.append(hh[:-1])
            print("incorrectly formatted hh:", hh)
    return hh_list_cleaned
    

async def topic_collect(run_name):
    hh_list = load_hh(run_name)
    hh_df = pd.DataFrame({'hh': hh_list})
    
    l = wb.lloom(
        df=hh_df,
        text_col="hh",
    )
    # with StringIO("y\nn\n") as fake_input:
    #     original_stdin = sys.stdin
    #     sys.stdin = fake_input

        # Call your function here
    score_df = await l.gen_auto(seed=cur_seed, max_concepts=len(hh_list) / 10)

        # Restore the original stdin
        # sys.stdin = original_stdin

    export_df = l.export_df()
    export_df.to_csv(f"../out/{run_name}/overall/topics_hh")
    

if __name__ == '__main__':
    run_name = "v2_cluster_single_final"
    topic_collect(run_name)