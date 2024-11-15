import os
import sys

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

    def __init__(self, run_name, topic, log=True):
        self.topic = topic
        topic = format_topic(topic)
        out_path = f"../out/{run_name}/{topic}"
        os.makedirs(out_path, exist_ok=True)
        self.out_dir = out_path + "/"
        self.files = []
        self.log = log

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

    def append_hh_gha(self, hh, gha_chunks, citations):
        if not self.log:
            return
        filepath = self.out_dir + "hh_gha_chunks"
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

    def append_final_cmp(self, hh, gha_cmp, tat_cmp, final):
        if not self.log:
            return
        filepath1 = self.out_dir + "hh_gha_tat_cmp"
        filepath2 = self.out_dir + "final.md"
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

        file2.write(f"{prepend2}{final}\n\n")
        file1.write(f"{prepend1}HH: {hh}\n\n")
        file1.write(f"\t - From GHA: {gha_cmp}\n")
        file1.write(f"\t - From TAT: {tat_cmp}\n")
        file1.close()

    def log_analysis_doc(self, hh="", result="", gha=None, tat=None, cite=False):
        if not self.log:
            return
        filepath = self.out_dir + "analysis_full.md"
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
                file.write(f"* **{g['document_title']}**: {g['content']}\n")
            file.write("\n\n")
