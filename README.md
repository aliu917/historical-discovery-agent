# cs224v-final-proj

### Demo

Website: https://aliu917.github.io/cs224v-proj/#

Video demo:

The website is composed of organized static pages that display the final navigation topics, high-level claims, comparison results, and African Times sources. All of the displayed results are computed from running the code using the steps below.
Because running the full pipeline is expensive and time-consuming, and we do not expect The African Times
or General History of Africa to change frequently, this website is the easiest way to interact with the final results.

The website is currently displaying final results from the run titled `v2_cluster_single_final`.

### Running Code

Note: after the initial set up, each section can be run independently. In the current configuration, results are cached to use existing previous results, though some large files may need to be downloaded separately (links to download provided below). We recommend using the same `run_name` for all steps.

#### Initial Setup

1. `pip install -r requirements.txt`
2. `echo OPENAI_API_KEY=\"sk...\" > .env`
3. `cd src`

#### Processing General History of Africa PDF chapters

The full data processing has been completed for General History of Africa volumes 6 and 7. For additional volumes, data processing to convert the original PDF to JSONL format can be done in the following steps:

1. Upload the chapter pdf file into `../gha_raw_pdf/`.
2. Run `python ocr_script.py -f <input_filepath>` to perform OCR and convert the PDF at `input_filepath` into a JSON file logged at `../gha_texts/<input_filename>`.
   - By default, `python ocr_script.py` will convert GHA volume 7 (`../gha_raw_pdf/africa7_all.pdf`) into json format at `../gha_texts/africa7_all.json`.
3. Run `python process_data_jsonl.py -f <input_filepath>` to convert the JSON from step 2 into a JSONL format saved at `../gha_jsonl/<input_filename>`.
    - By default, `python process_data_jsonl.py` will convert JSON file (`../gha_texts/africa7_all.json`) into JSONL format at `../gha_jsonl/africa7_all.jsonl`.
    - This program will also print a console output of all the document titles and section headers which can be used to manually verify the outputs against the volume PDFs (we noticed that there are occasionally OCR errors which require manual cleaning in this step).

#### Low-level Claim Extraction from The African Times

The full low-level claim extraction has been completed, with the final list of all low-level claims [here](https://drive.google.com/file/d/1TV5plbqIWpmB0kkAWDeW6na2h855fYzh/view?usp=drive_link) and the full mapping of low-level claims to their corresponding African Times source chunks available to download at [this link](https://drive.google.com/file/d/1pIu9pstbeRea6bUY97EBkt_LNUCBdizC/view?usp=drive_link).

To manually rerun this section, do the following:

1. Run `python all_ll_extract.py -r <run_name>`.
   - `-p <filepath>`: filepath pointing to the JSONL of all African Times. By default, this will extract from `../tat/the_african_times_articles.jsonl`.

All outputs are saved in the `../out/<run_name>/overall` directory and contain the following files:
- `tat_ll`: debug logging of a complete list of all low-level claims extracted from the entire African Times.
- `tat_ll_extract`: debug logging of the full output of each African Times chunk and the corresponding low-level claims extracted it
- `tat_ll_map.jsonl`: a JSONL containing a mapping of each indexed low-level claim with the African Times chunk it was extracted from.

Note: this step goes through every chunk of The African Times sequentially, so it takes a long time to run (a few hours). Intermediate outputs can be monitored real-time through the logged outputs at `/out/<input_run_name>/all/`.

#### Low-Level Claims Clustering

In this step, we group the low-level claims into clusters:

1. Run `python all_ll_clustering.py -r <run_name>`
   - `-e <embed_save_path>`: A path to pre-computed sentence embeddings for each low-level claims or, if not available, where the computed embeddings will be saved. By default, this points to `../tat/sentence_embeddings` and pre-computed embeddings can be downloaded from [here](https://drive.google.com/file/d/1gLo5X8ztR4HTjOIjaVtLpTu9AMaLE8Bv/view?usp=drive_link).
   - `-s <custom_saved_path>`: A custom folder path to load pre-computed UMAP and HDBSCAN cluster results from. By default, this is set to the current run directory. If using pre-computed UMAP and HDBSCAN results, files should be saved in this path as `<path>/umap_embeds.npy` and `<path>/final_cluster_map.json`.
   - `-c <run_new_cluster>`: By default, set to False. When True, this forces re-calculating the UMAP and HDBSCAN clustering logic even if pre-computed values already exist in the path.

All outputs are saved in the `../out/<run_name>/overall` directory and contain the following files (if not using pre-computed):

- `umap_params.json`: saving the UMAP param configuration used for this run
- `hdbscan_params.json`: saving the HDBSCAN param configuration used for this run
- `umap_embeds.npy`: the computed UMAP embeddings
- `final_cluster_map.json`: a JSON file mapping the cluster ID to a list of all low-level claims assigned to that cluster. Cluster index `-1` contains all un-clustered claims.

Note: Running the full low-level claim embedding takes a long time (5+ hours), so it is recommended to pre-download the embeddings from the link provided above and use the pre-computed values. Running new clustering (UMAP and HDBSCAN) takes about 5-10 minutes.

#### High-level claim generation and comparison

To generate all final high-level claims and comparison results, do the following:
1. Run `python comparison.py -r <run_name>`
- `-c <cluster_map_path>`: Path to the clustering map output from the previous step. By default, this is set to an existing cluster result.
- `-l <ll_map_path>`: Path to the mapping of low-level claims to The African Times chunks from an above step. This should come from the output of the Low-Level Extraction step above. By default, this is set to a pre-saved mapping at `../tat/tat_ll_map.jsonl` (not available on github pull, must be manually [downloaded](https://drive.google.com/file/d/1pIu9pstbeRea6bUY97EBkt_LNUCBdizC/view?usp=drive_link) and placed in that path).
- `-t <topic>`: A topic string to focus comparison of two sources only on the specific input topic. Note: if this string is provided, the cluster map and ll_map_path args above are not needed/used and low-level extraction is re-calculated based on only chunks related to the input topic.

All outputs are saved in the `../out/<run_name>/<topic>/` directory, where `topic` is `"overall"` if not provided.

- `analysis_full.md`: human-readable markdown version of final output with all TAT and GHA source chunks
- `final.md`: human-readable markdown of the high-level claims and comparison results only (no chunk sources)
- `hh_final.csv`: code-readable format logging of final table output for each high-level claim and its associated final comparison, TAT-only comparison, and GHA-only comparison in a csv file.
- `hh_gha_chunks`: debug logging of all GHA chunks retrieved for each high-level claim
- `hh_gha_tat_cmp` : debug logging of each high-level claim and its comparisons with all GHA chunks, and separately all TAT chunks
- `hh_sources.csv`: code-readable format logging of final table output for each high-level claim and its associated TAT source chunks, additional retrieved TAT chunks, and GHA chunks.
- `hh_tat_chunks`: debug logging of each high-level claim and its TAT chunks (`-` used to signify source chunks and `+` used to signify additional retrieved context chunks based on genie search similarity)
- `tat_hh`: debug logging of all high-level claims
- `tat_hh_ll`: debug logging of all high-level claims and their associated low-level claims

Note: this section takes a long time to run depending on how many outputs are expected. For a single topic run (using `-t <topic_name>`), this takes around 10 minutes. For all claims (no specified topic), this takes about 20+ hours (up to 1 min per high-level claim / cluster).

#### Topic Modeling

Topic Modeling consists of two parts: 1) determining topic titles and 2) assigning the appropriate topic section for each high-level claim. This is used only for grouping high-level claims over the entire source (no topic specified).

###### Part 1: determining topic titles

Since this section is already pre-determined in `topic1.json` and `topic2.json`, it does not need to be re-run, but providing the steps for posterity:
1. Using any `csv` file from the previous step (recommend `hh_final.csv` since it is smaller), upload onto google drive and run [this colab](https://colab.research.google.com/drive/1p_P7V5HoaII_MWjmSsZIzLnFobQjBW9Z#scrollTo=1A1RfWQXIqhT) for LLooM workbench topic generation. (Source: [LLooM Documentation](https://stanfordhci.github.io/lloom/about/get-started.html)).
2. Save the resulting topics and concept queries into a json file titled `topic<i>.json` for level `i` (1-indexed) within the `out/<run_name>/overall/` directory
3. Run `python topic_modeling.py -r <run_name> -i <depth> -t <topic_path>` where `run_name` must match a run where high-level claims have already been computed and `<depth>` is an integer value between [1, 3] and must be done in order (ie. `depth=2` can only be calculated after `depth=1` and so on). The `topic_path` should point to the directory containing the topics from the previous step.
3. After running a single depth, re-do step 1 to generate the next level of topics for depth `i+1`.

All outputs are saved in the `../out/<run_name>/overall` folder:

- `hh_topic.csv`: a table where each row contains a high-level claim and its topic up to level `i`.

###### Part 2: assigning topic titles

Steps:
1. Run `python topic_collection.py -r <run_name>`
- `-t <topic_path>`: path to the folder containing the `topic1.json` and `topic2.json` calculated from part 1. This is by default set to a topic set defined for an existing run: `../out/{run_name}/overall/`
- Note: `<run_name>` must be an existing run that already has generated high-level claims. If topics have already been assigned for a subset of high-level claims, it will only assign topics to new claims, unless some existing topic assignments do not exist in the provided topic mapping.

All outputs are saved in the `../out/<run_name>/overall` folder:

- `hh_topic.csv`: a table where each row contains a high-level claim and its corresponding first-level and second-level topics