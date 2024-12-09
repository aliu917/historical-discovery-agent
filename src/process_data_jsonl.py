"""
jsonl format:
{"id": "integer", "content": "string", "document_title": "string", "full_section_title": "string"}
- id: counter
- content: chunk text content limited to <= 500 tokens with https://python.langchain.com/v0.1/docs/modules/data_connection/document_transformers/
- document_title: chapter title
- full_section_title: chapter title > section title > subsection title > ...
"""
from collections import OrderedDict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

import json
import os
import re
import tiktoken
import argparse

CHUNK = 500
end_titles = "Members of the International Scientific Committee for the Drafting of a General History of Africa"


manual_sections = {
    "Conclusion" : 1,
    "The western and southern Volta plateaux" : 2,
    "The trans-Saharan trade" : 1,
    "The Muslim revolution in Massina: the reign of Seku Ahmadu (Shaykh Ahmad Lobbo)": 1,
    "The insecure situation of the Fulbe in the inland Niger delta just before the outbreak of the revolution" : 2,
    end_titles : 0,
    "Biographies of authors" : 1,
    "Bibliography" : 1,
    "Index" : 1,
    "Means of control and administration" : 1,
    "The workers' burden" : 1,
    "Compulsory service and provision of crops" : 3,
    "The labour system and legislation" : 3,
    "Production" : 3,
    "Food shortage, famine and epidemic" : 3,
    "The features of agricultural colonization" : 4,
    "The agricultural sector" : 4,
    "Mining" : 4,
    "Communication and ports" : 4,
    "The customs system" : 4,
    "The fiscal system" : 4,
    "The crisis and the major sectors of the economy of North Africa" : 3,
    "Tunisia, Algeria and Morocco during the great economic crisis (1930-5)" : 3,
    "The effects of the crisis on the settler economy" : 4,
    "The disruption of the Muslim economy by the crisis" : 4,
    "Social effects of the crisis" : 4,
    "Government intervention" : 4,
    "The peasant policy" : 4,
    "Nerv trends in agriculture; the persistently colonial nature of the economic system" : 4,
    "Economic policy during the period of Italian occupation" : 4,
    "The development of the infrastructure" : 4,
    "Free-trade policy" : 4,
    "Investment pattern" : 4,
    "Agricultural development" : 4,
    "Traditional African religion in the pre-colonial period" : 2,
    "African traditional religion and colonial rule" : 1,
    "Mahdist risings" : 3,
    "Neo-Mahdism" : 3,
    "Somaliland" : 1,
    "Political activities in Francophone West Africa, 1919-35" : 1,
    "Africa at the beginning of the nineteenth century: issues and prospects" : 0,
}

begin_sections = {
    "Contents" : False,
    "Preface" : False,
    "Description of the Project" : False,
    end_titles : False,
}

manual_text = {
    "Whatever happens we have got The maxim-gun and they have not 9"
}


class ResultObject:
    def __init__(self, id):
        self.full_section_list = []
        self.final_jsonl = []
        self.curr_text = ""
        self.curr_idx = id


def create_full_sections(full_section_list):
    section_titles = [x[0] for x in full_section_list]
    return " > ".join(section_titles)


def get_section_idx(height, section_list, left, is_text_len=False):
    prev_idx = len(section_list) - 1
    abs_height_idx = 0
    if prev_idx < 0 or (round(height) >= 18 and left > 100):
        abs_height_idx = 0
    elif is_text_len > 80:
        return 10
    elif round(height) >= 14 or (prev_idx == 0 and not is_text_len):
        abs_height_idx = 1
    elif not is_text_len:
        abs_height_idx = 2
    else:
        if height > 11 and len(section_list) >= 2:
            abs_height_idx = 2
        else:
            abs_height_idx = 10
    if is_text_len:
        return abs_height_idx
    relative_height_idx = prev_idx

    if relative_height_idx >= 1:
        prev_height = section_list[relative_height_idx][1]
        if relative_height_idx > 1 and height > prev_height + 1.1 and prev_height > 11:
            relative_height_idx = prev_idx - 1
        elif abs(height - prev_height) < 0.9:
            relative_height_idx = prev_idx
        else:
            relative_height_idx = prev_idx + 1
    else:
        relative_height_idx = prev_idx + 1
    return max(0, min(abs_height_idx, relative_height_idx))


# Note: assumption of 55 char line length only applies to
# level 1 sections. Breaks on level 2 sections but is ok bc
# we don't have level 3 sections.
def calculate_section_height(json_section):
    text = json_section["text"]
    text_box = json_section["prov"][0]["bbox"]
    raw_height = float(text_box["t"]) - float(text_box["b"])
    text_length = len(text)
    estimate_lines = text_length // 55 + (text_length % 55 > 0)
    raw_estimate = raw_height / (1 + 0.9 * (estimate_lines-1))
    return raw_estimate, text_box["l"]


def compare_height(section_height1, section_height2):
    if section_height1 < section_height2 - 1.1:
        return "smaller"
    elif abs(section_height1 - section_height2) < 1.1:
        return "equal"
    else:
        return "larger"


def is_json_type(obj, label_type):
    return obj["label"] == label_type


def is_section_header(obj):
    return is_json_type(obj, "section_header")


def is_content(obj):
    return is_json_type(obj, "text")


def skip_footnote_text(content_text):

    #Edge case
    if content_text == "1880-1900":
        return False

    if not any(char.isalpha() for char in content_text):
        return True

    # if len(content_text) < 200:
    number_pattern = r'^\d+\.\s'
    if re.match(number_pattern, content_text):
        return True

    # manual edge cases
    if "Sumatra see J. Bastin. op. cit., p. 89" in content_text:
        return True

    return False


def is_prev_continuing_text(text):
    for p in ['.', '?', '!']:
        if p in text[-2:] or (p in text[-3:] and not text[-1].isupper()):
            return False
    return True


def is_body_list_item(content_text):
    number_pattern = r'^\(\d+\)\s'
    if re.match(number_pattern, content_text):
        return True
    return False


def is_next_continuing_text(text):
    return not text[0].isupper()


def collect_fields(json_file, id, single_chapter=False):
    result = ResultObject(id)
    with open (json_file, 'r') as file:
        data = json.load(file)
        all_text = data["texts"]

        new_section = True
        new_chapter = False
        start = False
        start_chapters = False
        if single_chapter:
            start = True
            start_chapters = True
        is_text_title = False
        sub_part_idx = 0

        for i, section_json in enumerate(all_text):

            text = section_json["text"]

            if new_chapter:
                new_chapter = False
                # Skip second text (likely author)
                if len(text) < 150:
                    continue

            # New text content
            if is_json_type(section_json, "text"):

                if skip_footnote_text(text):
                    continue

                new_section_level = 10
                valid_start_char = text[0].isupper() or text[0].isdigit() or text[:2] == "c."
                valid_end_char = text[-1].isalpha() or text[-1].isdigit() or text[-1] == ","
                if text in manual_sections:
                    new_section_level = manual_sections[text]
                elif start_chapters and valid_start_char and valid_end_char:
                    new_section_height, left = calculate_section_height(section_json)
                    new_section_level = get_section_idx(round(new_section_height), result.full_section_list, left, len(text))
                if new_section_level <= 2:
                    is_text_title = True
                else:
                    separator = "\n"
                    # Continuing paragraph text content
                    if not new_section and len(result.final_jsonl) > 0 and (is_prev_continuing_text(result.curr_text) or is_next_continuing_text(text)):
                        separator = " "

                    result.curr_text += separator + text
                    new_section = False

            # New list item content
            elif is_json_type(section_json, "list_item"):
                if skip_footnote_text(text):
                    new_section = False
                    continue

                if not start_chapters:
                    result.curr_text += " " + text
                elif not new_section and len(result.final_jsonl) > 0 and is_prev_continuing_text(result.curr_text) and is_body_list_item(text):
                    result.curr_text += " " + text
                    new_section = False
                    continue

            # New section header
            if is_section_header(section_json) or is_text_title:
                is_text_title = False

                if skip_footnote_text(text):
                    new_section = False
                    continue

                new_section = True
                create_new_section(result)

                new_section_height, left = calculate_section_height(section_json)
                new_section_level = get_section_idx(new_section_height, result.full_section_list, left)
                if new_section_level == 0:
                    new_chapter = True
                    start_chapters = start
                    start = True

                if not start_chapters:
                    if new_section_level > 1:
                        result.curr_text += " " + text
                        continue
                    elif text in begin_sections:
                        begin_sections[text] = True
                    elif new_section_level == 1 and not begin_sections["Contents"]:
                        result.curr_text += " " + text
                        continue
                    elif begin_sections["Preface"] and text != "Description of the Project":
                        result.curr_text += " " + text
                        continue
                    elif text == "Description of the Project":
                        start_chapters = True

                if text == end_titles:
                    begin_sections[end_titles] = True
                elif begin_sections[end_titles]:
                    if text not in manual_sections:
                        result.curr_text += " " + text
                        continue

                # Edge case: section multi-line
                # if compare_height(new_section_height, curr_section_height) == "equal":
                if is_next_continuing_text(text) and is_section_header(all_text[i-1]):
                    result.full_section_list[-1] = (result.full_section_list[-1][0] + " " + text, result.full_section_list[-1][1])
                    continue

                if text[:6] == "Part I":
                    sub_part_idx = 1
                elif new_section_level == 0:
                    sub_part_idx = 0
                elif sub_part_idx:
                    new_section_level += 1

                # Hardcoded
                if text in manual_text:
                    result.curr_text += " " + text
                    continue
                elif len(text) < 5:
                    # Likely just the chapter number
                    continue
                elif result.full_section_list and text == result.full_section_list[-1][0]:
                    result.curr_text += " " + text
                    continue
                elif text in manual_sections:
                    result.full_section_list = result.full_section_list[:manual_sections[text]]
                elif new_section_height > 40 and new_section_level != 0:
                    # Most likely something incorrect since size is too large but position not in title pos
                    continue
                elif result.full_section_list and result.full_section_list[-1][0] == "Conclusion" and new_section_level != 0:
                    result.curr_text += " " + text
                    continue
                elif text.isupper():
                    result.full_section_list = result.full_section_list[:5]
                else:
                    result.full_section_list = result.full_section_list[:new_section_level]

                indent = " > " * len(result.full_section_list)
                print(f"{indent} {round(new_section_height, 2)} - {text}")

                result.full_section_list.append((text, new_section_height))

        create_new_section(result)

    return result


def create_new_section(result):
    if not result.curr_text:
        return

    chunked_text = chunk_section(result.curr_text)
    for text_chunk in chunked_text:
        new_jsonl = dict()
        new_jsonl["id"] = result.curr_idx
        result.curr_idx += 1
        new_jsonl["content"] = text_chunk
        new_jsonl["document_title"] = result.full_section_list[0][0]
        new_jsonl["full_section_title"] = create_full_sections(result.full_section_list)
        result.final_jsonl.append(new_jsonl)

    result.curr_text = ""


def chunk_section(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK,
        chunk_overlap=50,
        length_function=lambda x: len(tiktoken.get_encoding("o200k_base").encode(x)),
        is_separator_regex=False,
    )
    chunks = text_splitter.create_documents([text])
    return [chunk.page_content for chunk in chunks]


def process_data(filename):

    all_results = []
    single_chapters = False

    id = 0
    if single_chapters:
        path = "../gha_texts/chapters"
        for filename in os.listdir(path):
            if filename.split('.')[-1] != "json":
                continue
            file_path = os.path.join(path, filename)
            print()
            print("processing ", str(file_path))
            print()
            result = collect_fields(file_path, id, True)
            id = result.curr_idx
            all_results += result.final_jsonl
        out_filename = "chapters"
    else:
        result = collect_fields(filename, id)
        all_results = result.final_jsonl
        out_filename = filename

    output_dir = Path("../gha_jsonl")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / out_filename.split("/")[-1].split(".")[0]

    filename = f"{str(path)}_{CHUNK}.json"
    with open(filename + "l", 'w') as file1, open(filename, 'w') as file2:
        wrapper = {"all" : []}
        for entry in all_results:
            od = OrderedDict([
                ("id", entry["id"]),
                ("document_title", entry["document_title"]),
                ("full_section_title", entry["full_section_title"]),
                ("content", entry["content"])
            ])
            file1.write(json.dumps(od) + '\n')
            wrapper["all"].append(od)
        file2.write(json.dumps(wrapper))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Data pre-processing to JSONL format script input.")
    parser.add_argument('-f', '--file', type=str, default="../gha_texts/africa6_all.json",
                        help='The input filename (default: ./gha_texts/africa6_all.json)')
    args = parser.parse_args()

    process_data(args.file)

'''
Output: files and section structure


processing  ../gha_texts/chapters/Africa6_7.json

 30.9 - The British, Boers and Africans in South Africa, 1850-80
 >  13.61 - British withdrawal from the interior
 >  14.6 - The Cape Colony and Natal before 1870
 >  14.62 - The Boer republics before 1870
 >  14.04 - Boer relations with the Africans before 1870
 >  14.17 - British expansion in South Africa 1870-80

processing  ../gha_texts/chapters/Africa6_24.json

 57.65 - States and peoples of Senegambia and Upper Guinea
 >  14.2 - Senegambia
 >  14.68 - Upper Guinea and Futa Jallon
 >  13.7 - The Kru bloc
 >  13.82 - The world of the southern Mande
 >  13.84 - Conclusion

processing  ../gha_texts/chapters/Africa6_28.json

The African diaspora
 >  14.5 - Introduction
 >  14.5 - The Middle East and south-east Asia 5
 >  14.5 - The diaspora in Europe
 >  14.5 - The western diaspora: background to the nineteenth century
 >  14.5 - The abolitionist period
 >  14.5 - The impact of Africa
 >  14.5 - The diaspora and Africa

processing  ../gha_texts/chapters/Africa7_8.json

African initiatives and resistance in Central Africa, 1880-1914
 >  14.5 - The struggle to maintain independence: the era of confrontation and alliance
 >  14.5 - Early localized resistance against colonial rule and capitalism
 >  14.5 - Colonial insurrections to 1918
 >  14.5 - Conclusion

processing  ../gha_texts/chapters/Africa7_9.json

African initiatives and resistance in Southern Africa
 >  14.5 - Southern Africa on the eve of colonial rule
 >  14.5 - The Zulu revolution and its aftermath
 >  14.5 - The missionary factor
 >  14.5 - Models of African initiatives and reactions
 >  14.5 - The Zulu, Ndebele, Bemba and Yao: the politics of confrontation
 >  >  12.369903564453125 - The Zulu
 >  >  12.050865173339844 - The Ndebele
 >  14.5 - The Ngwato, Lozi, Sotho, Tswana and Swazi initiatives and reaction: the model of protectorate or wardship
 >  >  11.923095703125 - The T s w a n a
 >  >  11.856109619140625 - The Swazi
 >  14.5 - The Hlubi, Mpondomise, Bhaca, Senga, Njanja, Shona, Tonga, Tawara, etc., initiatives and reactions: the model of alliance
 >  14.5 - African initiatives and reactions, 1895-1914
 >  >  12.10943603515625 - The Ndebele-Shona Chimurenga
 >  >  12.077392578125 - The Herero
 >  14.5 - Conclusion

processing  ../gha_texts/chapters/Africa6_25.json

 38.46 - States and peoples of the Niger Bend and the Volta
 >  14.1 - Political and institutional upheavals
 >  >  11.99 - The Asante system: its rise and decline
 >  >  11.87 - The Mossi states
 >  >  13.34 - The western and southern Volta plateaux
 >  >  12.22 - Other peoples
 >  >  12.52 - The eastern regions of the Volta plateaux
 >  >  12.44 - The Bambara kingdoms of Segu and Kaarta
 >  >  12.66 - Summary
 >  14.04 - Socio-economic tensions
 >  >  11.98 - Production and trade
 >  >  11.7 - Trade channels
 >  >  12.56 - Social change
 >  14.24 - Religious change
 >  11.32 - Conclusion

processing  ../gha_texts/chapters/Africa7_6.json

African initiatives and resistance in West Africa, 1880-1914
 >  14.5 - Conquest and reaction in French West Africa, 1880-1900
 >  >  12.439422607421875 - Senegambia
 >  >  12.28533935546875 - Tukulor empire
 >  >  12.1712646484375 - Samori and the French
 >  >  12.329986572265625 - Dahomey
 >  >  11.8634033203125 - The Baule and the French
 >  14.5 - Conquest and reaction in British West Africa,
 >  >  12.417999267578125 - Asante (Gold Coast)
 >  >  13.242095947265625 - Southern Nigeria
 >  >  12.636474609375 - Conquest and Reaction in Northern Nigeria
 >  14.5 - African Reactions and Responses in West Africa,
 >  >  11.887130737304688 - The rebellion of Mamadou Lamine
 >  >  11.713958740234375 - The Hut T a x rebellion
 >  >  12.16925048828125 - The Yaa Asantewaa War
 >  >  12.06976318359375 - Mass Migration
 >  >  11.87774658203125 - Strikes
 >  >  12.4046630859375 - Ideological protest
 >  >  12.4244384765625 - Elite associations
 >  14.5 - The causes of failure

processing  ../gha_texts/chapters/Africa6_26.json

 30.47 - Dahomey, Yorubaland, Borgu and Benin in the nineteenth century
 >  14.23 - The Mono-Niger area as the unit of analysis
 >  14.33 - The collapse of Old Oyó
 >  14.19 - The decline of the Benin kingdom
 >  14.08 - The growth of European interest
 >  14.64 - Socio-economic change and institutional adaptation

processing  ../gha_texts/chapters/Africa6_10.json

 38.38 - The East African coast and hinterland, 1845-80
 >  14.11 - Omani penetration and the expansion of trade
 >  >  11.87 - The Kilwa hinterland routes
 >  >  11.71 - The central Tanzanian routes
 >  >  12.27 - The Pangani valley route
 >  >  12.31 - The Mombasa hinterland routes
 >  >  6.69 - The effects of long-distance trade on East African societies
 >  14.19 - The Nguni invasion
 >  13.81 - The Maasai
 >  14.14 - Increased European pressures

processing  ../gha_texts/chapters/Africa7_11.json

Liberia and Ethiopia, 1880-1914: the survival of two A f r i c a n states
 >  14.5 - Liberia and Ethiopia on the eve of the Scramble for Africa
 >  >  11.59478759765625 - Liberia
 >  >  12.79644775390625 - Ethiopia
 >  14.5 - European aggression on Liberian and Ethiopian territory, 1880-1914
 >  >  12.707275390625 - Liberia
 >  >  12.2620849609375 - Ethiopia
 >  14.5 - Economic and social developments and European intervention in Liberia's and Ethiopia's internal affairs, 1880-1914
 >  >  12.45562744140625 - Liberia
 >  >  12.188232421875 - Ethiopia
 >  14.5 - The o u t c o m e of the S c r a m b l e and partition for L i b e r i a and Ethiopia

processing  ../gha_texts/chapters/Africa7_10.json

Madagascar, 1880S-1930S: African initiatives and reaction to colonial conquest and domination
 >  14.5 - A country divided in the face of the imperialist threat
 >  >  6.448990671258224 - The situation on the eve of thefirst F r a n c o - M e r i n a war 3
 >  >  12.759765625 - The isolation of the Malagasy rulers, 1882-94
 >  >  6.688907020970395 - The 'Kingdom of Madagascar' in 1894: weakness and disarray
 >  14.5 - A country offering uncoordinated resistance to colonial conquest
 >  >  12.43145751953125 - The failure of leadership
 >  >  12.02569580078125 - The Menalamba m o v e m n t s in Imerina
 >  >  6.479106702302632 - Popular opposition in the regions subject to the royal authority
 >  >  12.50042724609375 - The resistance of the independent peoples
 >  14.5 - A c o u n t r y united by its submission to France and its opposition to colonial domination
 >  >  6.600116930509869 - From colonization to the dawning of the national movement
 >  >  6.720099198190789 - The first reactions in opposition to the colonial system
 >  >  12.780792236328125 - Struggles to recover dignity
 >  14.5 - Conclusion

processing  ../gha_texts/chapters/Africa6_27.json

 38.6 - The Niger delta and the Cameroon region
 >  13.88 - Introduction
 >  14.35 - The Niger delta
 >  >  11.61 - The western delta
 >  >  11.48 - The eastern delta
 >  >  12.38 - The Igbo hinterland
 >  13.53 - The Cross river basin
 >  >  12.42 - The obong of Calabar
 >  >  12.1 - The Ekpe society and the Bloodmen
 >  13.9 - The Cameroon coast and its hinterland 14
 >  >  12.92 - The Ogowe basin and surrounding regions 23
 >  14.26 - Conclusion

processing  ../gha_texts/chapters/Africa7_7.json

African initiatives a n d resistance in East Africa, i880-1914
 >  14.5 - The European Scramble for East Africa and the patterns of African resistance
 >  >  12.69073486328125 - The response in Kenya
 >  >  12.308502197265625 - The r e s p o n s e in Tanganyika
 >  >  12.3656005859375 - The response in Uganda
 >  14.5 - East Africa under colonial rule
 >  >  12.95013427734375 - Anti-colonial movements in East Africa to 1914
'''