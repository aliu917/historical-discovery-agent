import os
import sys
import json
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv()
import openai
import csv

def read_jsonl(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            yield json.loads(line.strip())
            
def format_topic(topic):
    topic = topic.lower()
    topic = topic.replace(" ", "_")
    return topic[:25]


def assert_run_path(run_name):
    if os.path.exists(f"../out/{run_name}"):
        user_input = input(f"Overriding existing run outputs at run name: {run_name}. Confirm: y/n\n")
        if "y" in user_input.lower():
            return
        else:
            print("aborting")
            sys.exit(0)


class OutputWriter():

    def __init__(self, run_name, topic=None, log=True):
        out_path = f"../out/{run_name}"
        if topic:
            self.topic = topic
            topic = format_topic(topic)
            out_path += f"/{topic}"
        os.makedirs(out_path, exist_ok=True)
        self.out_dir = out_path + "/"
        self.files = []
        self.log = log
        self.run_name = run_name
        self.close_files = []

    def append_file(self, filename, content):
        if not self.log:
            return
        filepath = self.out_dir + filename
        write_type = "a"
        if filepath not in self.files:
            write_type = "w"
            self.files.append(filepath)
            content = content[2:]
        file1 = open(filepath, write_type)
        file1.write(content)
        file1.close()

    def append_extract(self, filename="tat_ll_extract", chunk=None, ll=None):
        if not self.log:
            return
        content = []
        if chunk:
            content.append("Extracting low level hypotheses from TAT chunk:\n" + str(chunk))
        if ll:
            content.append("Found low level hypotheses:\n" + "\n".join(ll))
        self.append_file(filename, "\n\n" + "\n\n".join(content))

    def write_hh(self, hh_mapping, all_ll):
        if not self.log:
            return
        file1 = open(self.out_dir + "tat_hh_ll", "w")
        file2 = open(self.out_dir + "tat_hh", "w")
        for hh in hh_mapping:
            file1.write(f"[HH] {hh}\n")
            file2.write(f"- {hh}\n")
            for ll_id in hh_mapping[hh]:
                file1.write(f"\t - {ll_id}:{all_ll[ll_id]}\n")
            file1.write("\n\n")
        file1.close()
        file2.close()

    def append_hh(self, hh_mapping, all_ll):
        if not self.log:
            return

        filepath1 = self.out_dir + "tat_hh_ll"
        write_type = "a"
        prepend = ""
        if filepath1 not in self.files:
            write_type = "w"
            self.files.append(filepath1)
        
        file1 = open(filepath1, write_type)
        file2 = open(self.out_dir + "tat_hh", write_type)
        
        for hh in hh_mapping:
            file1.write(f"{prepend}[HH] {hh}\n")
            file2.write(f"- {hh}\n")
            for i, ll_id in enumerate(hh_mapping[hh]):
                file1.write(f"\t - {ll_id}:{all_ll[i]}\n")
            file1.write("\n\n")
        file1.close()
        file2.close()


    def append_hh_tat(self, hh, tat_chunks, orig_len, ok=True):
        if not self.log:
            return
        filepath = self.out_dir + "hh_tat_chunks"
        if not ok:
            filepath += "_excluded"
        write_type = "a"
        prepend = ""
        if filepath not in self.files:
            write_type = "w"
            self.files.append(filepath)
        else:
            prepend = "\n\n"
        file1 = open(filepath, write_type)
        file1.write(f"{prepend}HH: {hh}\n")
        for i, chunk in enumerate(tat_chunks):
            if i < orig_len:
                file1.write(f"\t - {str(chunk)}\n")
            else:
                file1.write(f"\t + {str(chunk)}\n")
        file1.close()

    def append_hh_gha(self, hh, gha_chunks, citations, ok=True):
        if not self.log:
            return
        filepath = self.out_dir + "hh_gha_chunks"
        if not ok:
            filepath += "_excluded"
        write_type = "a"
        prepend = ""
        if filepath not in self.files:
            write_type = "w"
            self.files.append(filepath)
        else:
            prepend = "\n\n"
        file1 = open(filepath, write_type)
        file1.write(f"{prepend}HH: {hh}\n")
        for chunk in gha_chunks:
            file1.write(f"\t - {str(chunk)}\n")
        file1.write(f"Selected relevant chunks: " + str(citations))
        file1.close()

    def append_final_cmp(self, hh, gha_cmp, tat_cmp, final, ok=True):
        if not self.log:
            return
        filepath1 = self.out_dir + "hh_gha_tat_cmp"
        filepath2 = self.out_dir + "final.md"
        if not ok:
            filepath1 += "_excluded"
            filepath2 = self.out_dir + "final_excluded.md"
        write_type = "a"
        prepend1 = ""
        prepend2 = ""
        if filepath1 not in self.files:
            write_type = "w"
            self.files.append(filepath1)
        else:
            prepend1 = "\n\n"
            prepend2 = "---\n\n"
        file1 = open(filepath1, write_type)
        file2 = open(filepath2, write_type)

        file2.write(f"{prepend2}# {hh}\n\n{final}\n\n")
        file1.write(f"{prepend1}HH: {hh}\n\n")
        file1.write(f"\t - From GHA: {gha_cmp}\n")
        file1.write(f"\t - From TAT: {tat_cmp}\n")
        file1.close()

    def log_final_code(self, hh, result, gha_result, tat_result, gha, tat, orig_len, ok=True):
        if not self.log:
            return
        filepath1 = self.out_dir + "hh_sources.csv"
        filepath2 = self.out_dir + "hh_final.csv"
        if filepath2 not in self.files:
            self.files.append(filepath2)
            file1 = open(filepath1, "w")
            file2 = open(filepath2, "w")
            file1.write("hh,gha,tat_orig,tat_extra,ok\n")
            file2.write("hh,result,gha,tat,ok\n")
            file1.close()
            file2.close()

        with open(filepath2, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([hh, result, gha_result, tat_result, ok])

        with open(filepath1, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([hh, gha, tat[:orig_len], tat[orig_len:], ok])


    def log_analysis_doc(self, hh="", result="", gha=None, tat=None, cite=False, ok=True):
        if not self.log:
            return
        filepath = self.out_dir + "analysis_full.md"
        if not ok:
            filepath = self.out_dir + "analysis_full_excluded.md"
        write_type = "a"
        title = ""
        if filepath not in self.files:
            write_type = "w"
            self.files.append(filepath)
            title = self.topic

        file = open(filepath, write_type)

        if title:
            file.write("# " + title + "\n\n")

        if hh:
            file.write("---\n\n## " + hh + "\n\n")
        if result:
            file.write(result + "\n\n")
        if gha:
            cited_text = " (relevant only)" if cite else ""
            file.write(f"Retrieved{cited_text} GHA chunks:\n")
            for g in gha:
                file.write(f"* **{g['section_title']}**: {g['content']}\n")
            file.write("\n\n")
        if tat:
            file.write("Retrieved TAT chunks:\n")
            for g in tat:
                if "article_title" in g:
                    title = "article_title"
                else:
                    title = "document_title"
                if "content" in g:
                    content = "content"
                else:
                    content = "content_string"
                file.write(f"* **{g[title]}**: {g[content]}\n")
            file.write("\n\n")
            
    def write_cluster(self, clusters, all_ll_list):
        if not self.log:
            return
        np.save(self.out_dir + 'cluster_labels', clusters.labels_)
        np.save(self.out_dir + 'cluster_probs', clusters.probabilities_)
        
        numbered_ll = list(zip(list(range(len(all_ll_list))), all_ll_list))
        probs_numbered_ll = list(zip(clusters.probabilities_.tolist(), numbered_ll))
        cluster_ll = list(zip(clusters.labels_.tolist(), probs_numbered_ll))
        sorted_cluster_ll = sorted(cluster_ll, key=lambda x: x[0])

        file1 = open(self.out_dir + "cluster_ll", "w")
        
        no_cluster_str = ""
        prev_cluster = -193847
        for elem in sorted_cluster_ll:
            cluster, (probs, (ll_id, ll)) = elem
            if cluster == -1:
                no_cluster_str += f"\t - [{round(probs, 2)}] {ll_id} - {ll}\n"
                continue
            if cluster != prev_cluster:
                file1.write("\n")
                file1.write(f"Cluster {int(cluster)}:\n")
                prev_cluster = cluster
            file1.write(f"\t - [{round(probs, 2)}] {ll_id} - {ll}\n")
            
        # Add all non-clustered data at the end
        file1.write("\n\n")
        file1.write(f"No cluster:\n")
        file1.write(no_cluster_str)
        
        file1.close()

    def write_params(self, params):
        if not self.log:
            return
        for name, param in params.items():
            f = open(self.out_dir + name + ".json", "w")
            json.dump(param, f)
            f.close()
            
    def end_task(self):
        for file in self.close_files:
            f = open(file, "a")
            f.write("}\n")
            f.close()
            
    def write_embeds(self, embeds, embed_name):
        if not self.log:
            return
        np.save(self.out_dir + embed_name + "_embeds", embeds)


class GPTQuery:
    def __init__(self, model="gpt-4o"):
        self.model = model
        openai.api_key = os.environ["OPENAI_API_KEY"]
        self.context = [] # Later if we want to do multiturn conversations

    def query(self, prompt, max_tokens=1000, use_context=False):
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages= [*self.context, {"role": "user", "content": prompt}] if use_context \
                                        else [{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0,
                n=1,
            )
            # breakpoint()
            return response.choices[0].message.content
        except Exception as e:
            print("Error querying GPT-4:", e)
            return None