import text_lloom.workbench as wb
import os
import pandas as pd
from utils import *
from prompts import *
from tqdm import tqdm
import json
import ast


gpt_obj = GPTQuery()


# def load_hh(run_name):
#     filename = f"../out/{run_name}/overall/tat_hh"
#     f = open(filename, "r")
#     hh_list = f.readlines()
#     hh_list_cleaned = []
#     for hh in hh_list:
#         if len(hh) == 1:
#             continue
#         if "- " in hh[:2]:
#             hh_list_cleaned.append(hh[2:-1])  # remove "- " and "\n"
#         else:
#             hh_list_cleaned.append(hh[:-1])
#             print("incorrectly formatted hh:", hh)
#     return hh_list_cleaned
#
#
# # does not work, using the colab instead
# def topic_collect(run_name):
#     # hh_list = load_hh(run_name)
#     # hh_df = pd.DataFrame({'hh': hh_list})
#     hh_df = pd.read_csv(f"../out/{run_name}/overall/hh_final.csv")
#
#     l = wb.lloom(
#         df=hh_df,
#         text_col="hh",
#     )
#
#     score_df = l.gen_auto(seed=None, max_concepts=len(hh_df) / 10)
#     export_df = l.export_df()
#     export_df.to_csv(f"../out/{run_name}/overall/hh_topics.csv")
#
#
# def topic_categorize(run_name, hh_df, topics, col_name):
#     hh_df[col_name] = None
#     for index, row in tqdm(hh_df.iterrows(), total=len(hh_df)):
#         hh_claim = row["hh"]
#         prompt = HH_TOPIC(hh_claim, topics)
#         response = gpt_obj.query(prompt)
#         response = response.strip().strip('"').strip()
#         hh_df.at[index, col_name] = response
#     hh_df.to_csv(f"../out/{run_name}/overall/hh_topic.csv")
#
#
# def topic_categorize_level2(run_name, ref_col_name, topics, new_col_name):
#     hh_df = pd.read_csv(f"../out/{run_name}/overall/hh_topic.csv")
#     hh_df[new_col_name] = None
#     for index, row in tqdm(hh_df.iterrows(), total=len(hh_df)):
#         hh_claim = row["hh"]
#         outer_topic = row[ref_col_name]
#         if outer_topic not in topics:
#             continue
#         next_topics = topics[outer_topic]
#         prompt = HH_TOPIC(hh_claim, next_topics)
#         response = gpt_obj.query(prompt)
#         response = response.strip().strip('"').strip()
#         hh_df.at[index, new_col_name] = response
#     hh_df.to_csv(f"../out/{run_name}/overall/hh_topic.csv")
#
#
# def run1(run_name):
#     hh_df = pd.read_csv(f"../out/{run_name}/overall/hh_final.csv")
#     hh_topic_df = hh_df[["hh"]]
#     # topics = {
#     #     "Colonial Mismanagement": "Does the text describe instances of ineffective governance or mismanagement by colonial authorities?",
#     #     "Trade and Economic Impact": "Does the text discuss the impact of colonial trade policies or economic activities on local economies?",
#     #     "Resistance and Conflict": "Does the text describe resistance or conflict between local populations and colonial powers?",
#     #     "Missionary Influence": "Does the text highlight the role or influence of missionaries in African societies during the colonial period?",
#     #     "Health and Disease": "Does the text address health challenges or the impact of diseases during the colonial period?",
#     # }
#     topics = {
#         "Slave Trade": "Does the text discuss the slave trade or efforts to suppress it?",
#         "Economic Impact and Trade Dynamics": "Does the text discuss the impact of colonial trade policies or economic activities on local economies?",
#         "Colonial Mismanagement": "Does the text describe instances of ineffective governance or mismanagement by colonial authorities?",
#         "African Leadership": "Does the text discuss the roles or actions of African leaders in historical or political contexts?",
#         "Resistance and Conflict": "Does the text describe resistance or conflict between local populations and colonial powers?",
#         "Religious and Missionary Influence": "Does the text highlight the role or influence of missionaries and religion in African societies during the colonial period?",
#         "Health and Disease": "Does the text address health challenges or the impact of diseases during the colonial period?",
#         "European Influence": "Does the text describe the influence or involvement of specific European nations in African affairs?",
#         "Colonial Narratives": "Does the text critique or analyze colonial narratives or perceptions of Africa?",
#         "Diplomatic Relations": "Does the text explore diplomatic relations or interactions between African and foreign leaders?",
#     }
#     topic_categorize(run_name, hh_topic_df, topics, "topic1")
#
#
# def run2(run_name):
#     # topics = {
#     #     "Colonial Mismanagement": {
#     #         "Cultural and Social Impact": "Does the text example discuss the impact of colonialism on local cultures, social structures, or indigenous practices?",
#     #         "Resistance and Reform": "Does the text example describe efforts to resist colonial rule or advocate for reforms and improvements?",
#     #         "Colonial Governance": "Does the text describe the structure or nature of governance during colonial times in Africa?",
#     #         "Economic Impact": "Does the text discuss the economic effects or policies related to colonialism in Africa?",
#     #         "Social Hierarchies": "Does the text mention social hierarchies or racial dynamics in colonial Africa?",
#     #         "Colonial Justification": "Does the text provide justifications or ideologies used to support colonialism in Africa?",
#     #         "Political Instability": "Does the text example highlight political instability or conflicts caused by colonial governance?",
#     #         "Colonial Exploitation": "Does the text example discuss the exploitation of resources or economic systems under colonial rule?",
#     #         "Local Agency": "Does the text example describe the role or influence of local communities or leaders in shaping colonial policies?",
#     #     },
#     #     "Trade and Economic Impact" : {
#     #         "Slave Trade Impact": "Does the text example discuss the impact or involvement of the slave trade in African societies or economies?",
#     #         "Economic Development": "Does the text example highlight efforts or challenges related to economic development in Africa?",
#     #         "Agricultural Potential": "Does the text example discuss the potential or challenges of agriculture in Africa?",
#     #         "Infrastructure Development": "Does the text example focus on the development or impact of infrastructure in colonial Africa?",
#     #         "European-African Trade": "Does the text example discuss trade interactions or economic connections between Europe and Africa?",
#     #         "British Expansion": "Does the text example highlight British expansion or influence in Africa?",
#     #         "Diplomatic Relations": "Does the text example discuss diplomatic efforts or relations involving African regions?",
#     #         "Resource Exploitation": "Does the text example discuss the exploitation of African resources by external powers?",
#     #         "Colonial Impact": "Does the text example describe the impact of colonial powers on African societies and governance?",
#     #     },
#     #     "Resistance and Conflict" : {
#     #         "Economic and Trade Issues": "Does the text discuss economic challenges, trade disruptions, or commerce-related conflicts in Africa?",
#     #         "Cultural and Social Dynamics": "Does the text explore cultural practices, social structures, or traditional customs in African societies?",
#     #         "Colonial Dynamics": "Does the text explore resistance to colonial rule and the impact of colonial policies on African societies?",
#     #         "Power Struggles": "Does the text involve military or diplomatic power struggles between African societies and European powers during the colonial period?",
#     #     },
#     #     "Missionary Influence" : {
#     #         "Exploration and Knowledge": "Does the text highlight the role of explorers in advancing geographical or cultural understanding of Africa?",
#     #         "Religious Influence": "Does the text focus on the spread of Christianity or other religious influences in Africa?",
#     #         "Local Agency and Leadership": "Does the text discuss the role of local leaders or the agency of Africans in shaping their own futures?",
#     #         "Women's Role": "Does the text example highlight the role or influence of women in African societies or education?",
#     #         "Philanthropy and Aid": "Does the text example mention philanthropic efforts or aid initiatives aimed at supporting African development?",
#     #         "Economic and Industrial Development": "Does the text example focus on economic or industrial development initiatives in Africa?",
#     #         "Missionary Challenges": "Does the text describe any challenges or obstacles faced by missionaries in their work?",
#     #         "Cultural Dynamics": "Does the text explore the impact of European influence on African cultures or the integration and conflict between different customs?",
#     #         "Colonial and Religious Intersections": "Does the text explore the interactions between colonial authorities and missionaries or the intersection of religious and political elements?",
#     #     },
#     #     "Health and Disease" : {
#     #         "Traditional vs. European Medicine": "Does the text compare traditional African medical practices with European medicine?",
#     #         "Exploration Risks": "Does the text highlight the risks and challenges faced by explorers in Africa?",
#     #         "Tropical Diseases": "Does the text example discuss the impact or prevalence of tropical diseases in Africa or other regions?",
#     #         "Perceptions of West Africa": "Does the text example challenge or discuss perceptions of West Africa's desirability or healthfulness?",
#     #         "Nutrition and Health": "Does the text discuss the impact of nutrition on health outcomes?",
#     #         "Colonial Influence": "Does the text explore the influence of colonial activities on health or economy?",
#     #         "Environment and Infrastructure Health": "Does the text discuss how environmental and infrastructural factors influence health outcomes?",
#     #     },
#     # }
#     topics = {
#         "Slave Trade" : {
#             "Slave Trade Impact on Societies": "Does the text discuss the impact of the slave trade on societies?",
#             "Repatriation and Migration": "Does the text discuss the repatriation or migration of African descendants?",
#             "Human Rights Abuses during the Slave Trade": "Does the text highlight human rights abuses or inhumane conditions?",
#             # "Colonial Expansion": "Does the text discuss territorial expansion or annexation by colonial powers?",
#             # "Military Presence": "Does the text discuss the military presence or actions in Africa?",
#             "Health and Mortality Issues from the Slave Trade": "Does the text mention health issues or mortality rates related to the slave trade?",
#             "Cultural and Ancestral Connections": "Does the text discuss cultural or ancestral connections, particularly in the context of repatriation?",
#             "Economic Dependence on the Slave Trade": "Does the text describe economic systems or entities that depended on the slave trade?",
#             "Role of African Leaders on the Slave Trade": "Does the text discuss the role of African leaders in the slave trade?",
#             "19th Century Initiatives against Slavery": "Does the text discuss 19th-century initiatives against slavery?",
#             "Public Condemnation of the Slave Trade": "Does the text mention public condemnation of the slave trade?",
#         },
#         "Economic Impact and Trade Dynamics" : {
#             "Trade Infrastructure Development": "Does the text mention infrastructure development in Africa during the colonial period?",
#             "Agricultural Potential and Development": "Does the text highlight the agricultural potential or development in Africa?",
#             "Military and Economic Interests": "Does the text link military actions to economic interests in Africa?",
#             "Global Economic Integration of African economies": "Does the text describe the integration of African economies into global markets?",
#             # "Colonial Administration": "Does the text mention the administrative strategies of colonial powers in Africa?",
#             "Economic Conflict": "Does the text describe resistance or conflict related to colonial economic activities?",
#             "Resource Exploitation": "Does the text discuss the exploitation and extraction of African resources by colonial powers?",
#             "Trade Control": "Does the text focus on the control or establishment of trade routes and networks in Africa?",
#             "Colonial Economic Strategies": "Does the text describe economic policies and benefits for colonial powers in Africa?",
#             "Local Economic Effects": "Does the text describe the impact of colonial activities on local African economies and their dependency?",
#         },
#         "Colonial Administration" : { # and Mismanagement" : {
#             "Military Challenges in Colonial Regions": "Does the text example discuss challenges faced by military operations in colonial regions?",
#             # "Health and Sanitation Issues": "Does the text example address health or sanitation problems in colonial areas?",
#             "Social and Political Instability": "Does the text example describe social or political instability resulting from colonial actions?",
#             # "Education Development": "Does the text example discuss the impact of colonial policies on education or development?",
#             "Neglect of Local Health, Environment, and Education": "Does the text example discuss neglect of environmental concerns in colonial areas?",
#             "Judicial and Legal Reforms": "Does the text example mention calls for judicial or legal reforms in colonial territories?",
#             "Economic Impacts of Colonial Administration": "Does the text example focus on efforts or failures to achieve economic and social progress in colonial regions?",
#             "Colonial Administration Critique": "Does the text example critique the effectiveness or strategies of colonial administration?",
#             "Racial Discrimination": "Does the text mention racial discrimination within colonial administration?",
#             "Colonial Exploitation": "Does the text describe exploitative practices under colonial rule?",
#             "Taxation and Duties": "Does the text address the imposition of taxes or duties by colonial authorities?",
#             "Local Governance Undermined": "Does the text describe how colonial rule undermined local governance?",
#             "Colonial Conflicts and Resistance": "Does the text example describe public dissatisfaction or resistance to colonial rule?",
#             "Neglect of African Cultures": "Does the text example highlight issues of cultural insensitivity or disregard by colonial authorities?",
#             "Colonial Financial Issues": "Does the text example address financial mismanagement or misconduct under colonial rule?",
#         },
#         "African Leadership" : {
#             "Diplomatic Strategies": "Does the text describe diplomatic strategies or negotiations involving African kingdoms?",
#             "Education and Development": "Does the text emphasize the role of education in societal or political development?",
#             "Resistance and Agency": "Does the text highlight resistance against colonial influences or the agency of African leaders?",
#             # "Humanitarian Efforts": "Does the text discuss humanitarian efforts or contributions by African or Caribbean leaders?",
#             "Political Stability": "Does the text address efforts or challenges related to political stability in African regions?",
#             "Empowerment and Progress": "Does the text focus on empowerment or progress within African communities?",
#             "Religious and Cultural Influence": "Does the text explore the influence of religious or cultural factors on governance or society?",
#             "Historical Contributions": "Does the text highlight historical contributions or achievements of African societies?",
#             # "Development Initiatives": "Does the text focus on initiatives aimed at economic or community development in African regions?",
#         },
#         "Resistance and Conflict" : {
#             # "Cultural Preservation": "Does the text highlight efforts to preserve cultural identity or traditions?",
#             "Colonial Expansion": "Does the text discuss efforts or challenges related to colonial expansion?",
#             # "Infrastructure Development": "Does the text discuss infrastructure development and its impact on local communities?",
#             "Religious Influence": "Does the text describe the influence of religious beliefs or institutions on local or colonial actions?",
#             "Political Alliances": "Does the text discuss political alliances or rivalries between different groups?",
#             "Military Presence": "Does the text mention the presence or actions of military forces in a region?",
#             "Trade and Economic Disruptions": "Does the text discuss disruptions or changes in trade routes or practices?",
#             "Legal and Political Control": "Does the text describe legal or political measures used to maintain control?",
#             "Political Instability": "Does the text highlight political instability or turmoil in a region?",
#             # "Technological Influence": "Does the text discuss the impact of technology on warfare or conflicts?",
#             "Resistance Movements": "Does the text describe resistance movements or uprisings?",
#             # "Strategic Importance": "Does the text highlight the strategic importance of a region or group in conflicts?",
#             # "Resource Issues": "Does the text mention control or disputes over resources?",
#             # "Environmental Impact": "Does the text mention environmental factors affecting actions or conflicts?",
#         },
#         "Religious and Missionary Influence" : {
#             "Women's Empowerment": "Does the text discuss the empowerment or education of women in Africa?",
#             "Philanthropy and Support for Religious Efforts": "Does the text discuss philanthropic efforts or support for African initiatives?",
#             "Integration Efforts": "Does the text describe efforts to integrate local populations into new societal structures?",
#             "Local Agency": "Does the text highlight the role of local agency or leadership in religious or social contexts?",
#             "Political Dynamics": "Does the text address political dynamics or negotiations during the colonial period?",
#             # "Community Support": "Does the text describe efforts or initiatives aimed at supporting or improving community well-being?",
#             "Infrastructure Development": "Does the text mention efforts or projects related to building or improving infrastructure?",
#             # "Government Involvement": "Does the text refer to the role or actions of government entities in societal or community matters?",
#             "European Religious Collaboration and Cooperation": "Does the text describe collaborative efforts or partnerships between different groups or organizations?",
#             "Conflict and Influence on Traditional Cultures": "Does the text emphasize the importance of preserving or maintaining cultural practices or traditions?",
#             # "Identity and Belonging": "Does the text explore themes of identity, belonging, or cultural identity changes?",
#             # "Economic Motivations": "Does the text mention economic motivations or development efforts in Africa?",
#             "Health Concerns": "Does the text address health risks or initiatives related to wellness in Africa?",
#         },
#         "Health and Disease" : {
#             "Impact on European Settlers": "Does the text mention high mortality rates among European settlers in colonial regions?",
#             "Traditional vs. Western Medicine": "Does the text discuss the interaction or conflict between traditional African medical practices and Western medicine?",
#             "Colonial Health Policy Influence": "Does the text discuss how health considerations influenced colonial policies?",
#             # "Local Medical Expertise": "Does the text emphasize the role of local medical expertise in addressing health issues?",
#             # "Colonial Health Infrastructure": "Does the text address efforts to develop public health and sanitation infrastructure during colonial times?",
#             "Colonial Disease Challenges": "Does the text discuss health challenges and disease prevalence during the colonial era, particularly in Africa?",
#         },
#         "European Expeditions and Influence" : {
#             "Military Operations": "Does the text discuss military operations or strategies in Africa?",
#             "European Exploration": "Does the text mention European exploration efforts or geographical discoveries in Africa?",
#             "Strategic Alliances": "Does the text discuss strategic alliances or treaties between colonial powers and local leaders in Africa?",
#             "Challenges of Exploration": "Does the text describe the challenges faced by explorers in Africa, such as geographical or environmental obstacles?",
#             "European Rivalries": "Does the text mention rivalries or conflicts between European powers in Africa?",
#             "Societal and Infrastructure Development": "Does the text refer to humanitarian, education, or infrastructure development in Africa during the colonial period?",
#             # "Legal Systems": "Does the text describe the establishment or influence of European legal systems in colonial Africa?",
#             # "Social and Political Structures": "Does the text discuss the social or political structures in Africa during the colonial period?",
#             # "Humanitarian Efforts": "Does the text mention humanitarian efforts or advocacy related to Africa during the colonial period?",
#             # "Educational Influence": "Does the text discuss the influence of European educational systems or institutions in Africa?",
#             "Local Resistance": "Does the text describe resistance or opposition from local African communities against colonial powers?",
#             "Cultural Integration": "Does the text mention the integration or blending of European and African cultural elements?",
#             # "Economic Exploitation": "Does the text highlight the economic activities and resource exploitation by colonial powers in Africa?",
#             "Colonial Governance": "Does the text describe the governance and influence of colonial powers, particularly the British, in Africa?",
#         },
#         "Colonial Narratives" : {
#             # "Polygamy Criticism": "Does the text critique polygamy as an oppressive practice?",
#             # "Local Perspectives": "Does the text emphasize the importance of including local or indigenous perspectives?",
#             "Racial Stereotypes": "Does the text challenge or address racial stereotypes?",
#             "Governance Critique": "Does the text critique colonial governance or administration?",
#             "Resource Mismanagement": "Does the text discuss the mismanagement or exploitation of resources?",
#             # "Indigenous Narratives": "Does the text highlight the importance of indigenous narratives or stories?",
#             # "Women's Rights": "Does the text focus on enhancing the status or rights of women?",
#             # "Social and Economic Reform": "Does the text discuss efforts towards social or economic reform?",
#             # "Mature Political Consciousness": "Does the text discuss the development of political awareness or consciousness?",
#             # "Social Justice": "Does the text advocate for social justice or equality?",
#             # "Colonial Legal Frameworks": "Does the text address how colonial control shaped legal or governance frameworks?",
#             "African Cultural Complexities": "Does the text emphasize the complexity or richness of African cultures?",
#             "Colonial Power Dynamics": "Does the text discuss the power dynamics between European settlers and indigenous communities?",
#             "European Beliefs on African Social and Economic Reform" : "Does the text discuss European perspectives and impacts on African narratives?",
#             "Impact of Media on Local and Colonial Perspectives" : "Does the text discuss the impact of media on African perspectives and shaping African narratives?",
#             "Colonial Governance Practices" : "Does the text discuss the existing African governance movements and practices?"
#         },
#         "Diplomatic Relations" : {
#             "Cultural Exchange": "Does the text describe cultural exchanges between different regions or groups?",
#             # "Military Strategy": "Does the text involve military strategy or presence as part of diplomatic efforts?",
#             "Diplomatic Challenges": "Does the text mention challenges in diplomatic relations?",
#             "Economic Diplomacy": "Does the text examine how economic factors and trade shape diplomatic relations?",
#             "Territorial Geopolitics": "Does the text discuss territorial issues and geopolitical dynamics affecting regional strategies?",
#         },
#     }
#     topic_categorize_level2(run_name, "topic1", topics, "topic2")
#
#
# def run3(run_name):
#     topics = {
#         # "Colonial Power Dynamics": {
#         #     "Cultural Persistence": "Does the text highlight the persistence of cultural practices despite external influences?",
#         #     "Racial Dynamics": "Does the text explore racial dynamics or systemic racial inequality?",
#         #     "Colonial Economic Exploitation": "Does the text describe the exploitation of resources or labor during colonial times?",
#         # },
#         "Colonial Administration Critique" : {
#             "Critique of British Colonial Administration" : "Does the text example critique the effectiveness or strategies of British colonial administration?",
#             "Critique of French Colonial Administration" : "Does the text example critique the effectiveness or strategies of French colonial administration?",
#             "Critique of Dutch Colonial Administration" : "Does the text example critique the effectiveness or strategies of Dutch colonial administration?",
#             "Critique of Portuguese Colonial Administration": "Does the text example critique the effectiveness or strategies of Portuguese colonial administration?",
#             "Critique of Belgian Colonial Administration": "Does the text example critique the effectiveness or strategies of Belgian colonial administration?",
#             "Critique of German Colonial Administration": "Does the text example critique the effectiveness or strategies of German colonial administration?",
#             "Critique of General Colonial Administrations": "Does the text example critique the effectiveness or strategies of general colonial administration without specific mention of any European nations?",
#             # "Local Leadership Changes": "Does the text example describe changes or challenges in local leadership or governance?",
#             # "Economic Impact": "Does the text example highlight negative effects on economic development or exploitation?",
#             # "Traditional Leadership Tensions": "Does the text example discuss tensions or conflicts with traditional leadership structures?",
#             # "Imperial Interests vs. Local Needs": "Does the text example explore the conflict between imperial interests and local needs or rights?",
#             # "Governor Criticism": "Does the text example involve criticism or challenges faced by a governor?",
#             # "Policy and Strategy Shifts": "Does the text example describe shifts in policy or strategic approaches?",
#             # "Local Engagement": "Does the text example emphasize the importance of engaging with local communities?",
#             # "Social Disorder": "Does the text example highlight social disorder or dissatisfaction?",
#             # "Leadership Experience": "Does the text example discuss the experience or qualifications of leaders?",
#             # "Legal and Diplomatic Approaches": "Does the text example mention the use of legal or diplomatic approaches in governance?",
#             # "Exploitation and Neglect": "Does the text example address the exploitation or neglect of local populations?",
#             # "Internal Conflicts": "Does the text example describe internal conflicts or tensions within groups or regions?",
#             # "Military Influence": "Does the text highlight the influence of military leadership in colonial governance?",
#             # "Colonial Reforms": "Does the text discuss reforms or changes in colonial governance?",
#         }
#     }
#     topic_categorize_level2(run_name, "topic2", topics, "topic3")


def create_final_mapping(run_name):
    dir = f"../out/{run_name}/overall/"
    hh_df = pd.read_csv(dir + "hh_topic_final.csv")
    topics1 = hh_df['topic1'].unique().tolist()

    for topic in topics1:
        sub_df = hh_df[hh_df["topic1"] == topic]
        print(f'"{topic}": {len(sub_df)}')
        for topic2 in sub_df["topic2"].unique().tolist():
            print(f'\t "{topic2}": {len(sub_df[sub_df["topic2"] == topic2])}')

    # for topic in topics1:
    #     print(f'"{topic}" : "",')
    # print()
    #
    # for topic in topics1:
    #     print(f'"{topic}" : {{')
    #     for topic2 in hh_df[hh_df["topic1"] == topic]["topic2"].unique().tolist():
    #         print(f'\t "{topic2}" : "",')
    #     print('},')


def run_fix():
    dir = f"../out/{run_name}/overall/"
    hh_df = pd.read_csv(dir + "hh_topic.csv")

    with open(f"../out/{run_name}/overall/topic1.json", 'r') as file:
        topics1 = json.load(file)
    with open(f"../out/{run_name}/overall/topic2.json", 'r') as file:
        topics2 = json.load(file)

    for index, row in tqdm(hh_df.iterrows(), total=len(hh_df)):
        hh_claim = row["hh"]

        topic1_missing = "topic1" not in row or row["topic1"] not in topics1
        topic2_missing = "topic2" not in row or not row["topic2"]

        if topic1_missing or row["topic2"] not in topics2[row["topic1"]]:
            prompt = HH_TOPIC(hh_claim, topics1)
            response = gpt_obj.query(prompt)
            response = response.strip().strip('"').strip()
            hh_df.at[index, "topic1"] = response
        row_topic1 = hh_df.at[index, "topic1"]
        if row_topic1 not in topics1:
            continue
        next_topics = topics2[row_topic1]
        if topic2_missing or row["topic2"] not in topics2[row_topic1]:
            prompt = HH_TOPIC(hh_claim, next_topics)
            response = gpt_obj.query(prompt)
            response = response.strip().strip('"').strip()
            hh_df.at[index, "topic2"] = response
    hh_df.to_csv(f"../out/{run_name}/overall/hh_topic_final.csv")


def topic_assign(run_name, hh_path='hh_final.csv', save_path='hh_topic.csv'):
    dir = f"../out/{run_name}/overall/"
    hh_df = pd.read_csv(dir + hh_path)

    save_df = hh_df
    if save_path != hh_path:
        save_df = hh_df[["hh"]]
    if not os.path.exists(save_path):
        save_df["topic1"] = None
        save_df["topic2"] = None

    with open(f"../out/{run_name}/overall/topic1.json", 'r') as file:
        topics1 = json.load(file)
    with open(f"../out/{run_name}/overall/topic2.json", 'r') as file:
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
    run_name = "v2_cluster_single_final"
    # run3(run_name)
    # create_final_mapping(run_name)
    # run_fix()
    # create_final_mapping(run_name)
    topic_assign(run_name, hh_path='hh_final.csv', save_path='hh_topic.csv')