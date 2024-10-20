"""
jsonl format:
{"id": "integer", "content": "string", "document_title": "string", "full_section_title": "string"}
- id: counter
- content: chunk text content to <= 500 tokens with https://python.langchain.com/v0.1/docs/modules/data_connection/document_transformers/
- document_title: chapter title
- full_section_title: chapter title > section title > subsection title > ...


Some notes from observing the jsons:
- document_title: can detect from a string that appears both in a "page_header" labeled element
                 and appears in "text" labeled element (note: not all page headers are titles)
                 Ex: "African initiatives and resistance in West Africa, 1880-1914"
                 Note: not all page header elements are chapter titles (ex: "Africa under Colonial Domination ...")
                 Actually, I think we should just manually do this lol, seems harder to detect after the fact and if
                 there are typos...

- full_section_title: For the most part, these should be in the "section_header" labeled elements. However,
                      it doesn't seem like the json parse is very good at finding subsections. Ex: "Senegambia"
                      is a subsection of "Conquest and reaction in French West Africa ..." but they are both labeled
                      "section_header." Currently thinking a hacky method of getting this would be to use the "prov"
                      and roughly measure the text height (if a section is at least 1 pt smaller than another section
                      header, then it is a subsection or something). Tested this and I think the diff is enough to tell:

                      ** Senegambia:
                      "prov": [
                        {
                          "page_no": 4,
                          "bbox": {
                            "l": 39.72174835205078,
                            "t": 177.33309936523438,
                            "r": 98.95807647705078,
                            "b": 164.8936767578125,
                            "coord_origin": "BOTTOMLEFT"
                          },
                          "charspan": [
                            0,
                            10
                          ]
                        }
                      ]

                      ** Conquest and reaction in French West Africa ...
                      "prov": [
                        {
                          "page_no": 4,
                          "bbox": {
                            "l": 40.32535171508789,
                            "t": 479.55426025390625,
                            "r": 371.5114440917969,
                            "b": 464.8079833984375,
                            "coord_origin": "BOTTOMLEFT"
                          },
                          "charspan": [
                            0,
                            54
                          ]
                        }
                      ]

                    In each bbox, subtract t - b:

                    Conquest and reaction in French West Africa ...
                      479.55426025390625 - 464.8079833984375 = 14.74627685546875

                    Senegambia:
                      177.33309936523438 - 164.8936767578125 = 12.439422607421875

                    Also confirmed "Tukulor empire" (another subsection of Conquest and reaction in French West Africa):
                      323.73651123046875 - 311.451171875 = 12.28533935546875

- content: TODO - figure out how to chunk. Paragraphs are already json-separated, maybe chunk the long paragraphs by
           SemanticChunker or something? TODO: how to ensure token size <= 500.
           Note: some paragraphs are separated by page break. Combine texts with no capitalization I guess.

"""
import json


EMPTY_JSONL = {"content": ""}


class ResultObject:
    def __init__(self):
        self.full_section_list = []
        self.final_jsonl = []
        self.curr_title = ""
        self.curr_jsonl = EMPTY_JSONL


def create_full_sections(full_section_list):
    section_titles = [x[0] for x in full_section_list]
    return " > ".join(section_titles)


def calculate_section_height(json_section):
    # TODO: implement calculating t - b from the "prov"
    return 10


def is_height_smaller(section_height1, section_height2):
    return section_height1 < section_height2 - 1


def is_json_type(obj, label_type):
    return obj["label"] == label_type


def collect_fields(json_file):
    result = ResultObject()
    with open (json_file, 'r') as file:
        data = json.load(file)
        all_text = data["texts"]
        new_page = False
        for section_json in all_text[:200]:

            # First title text
            if result.curr_title == "":
                title = section_json["text"]
                result.curr_title = title
                result.full_section_list.append((title, float("inf")))
                continue

            # New text content
            if is_json_type(section_json, "text"):
                text = section_json["text"]

                # edge case: paragraph continuing over page break
                if new_page:
                    # TODO: implement continued page break content
                    continued_content = False
                    if continued_content:
                        result.final_jsonl[-1]["content"] += text
                        continue

                result.curr_jsonl["document_title"] = result.curr_title
                result.curr_jsonl["content"] = text
                result.curr_jsonl["full_section_title"] = create_full_sections(result.full_section_list)
                result.final_jsonl.append(result.curr_jsonl.copy())
                result.curr_jsonl = EMPTY_JSONL

            # New section header
            elif is_json_type(section_json, "section_header"):
                curr_section_height = result.full_section_list[-1][-1]
                new_section_height = calculate_section_height(section_json)
                while not is_height_smaller(new_section_height, curr_section_height):  # TODO: update to soft compare
                    result.full_section_list.pop()
                    curr_section_height = result.full_section_list[-1][-1]
                result.full_section_list.append((section_json["text"], new_section_height))

            # New page header
            elif is_json_type(section_json, "section_header"):
                new_page = True
                continue

            new_page = False

    return result



if __name__ == '__main__':
    result = collect_fields("../gha_texts/Africa7.json")
    for elem in result.final_jsonl:
        print(json.dumps(elem))
