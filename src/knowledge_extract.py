from vector_db import GPTQuery
from genie_search import african_times_request
from prompts import *
import re

gpt_obj = GPTQuery()


def extract_hypotheses(topic):
    all_hh_mappings = {}
    all_hypotheses = []
    chunks_all = african_times_request(topic)
    if not isinstance(topic, list):
        topic = [topic]
    for i, t in enumerate(topic):
        chunks = chunks_all[i]['results']
        for j, chunk in enumerate(chunks):
            response = gpt_obj.query(EXTRACT_HYPOTHESES_FROM_CHUNK(chunk, t))
            response = clean_list_hypotheses(response)
            all_hypotheses += response

        hh_mapping = get_high_level_hypotheses(all_hypotheses)
        all_hh_mappings.update(hh_mapping)

    return all_hypotheses, all_hh_mappings


def clean_list_hypotheses(response):
    response_list = list(filter(lambda x: len(x) > 5, response.split('\n')))
    response_list = [x.split(':')[-1].strip() for x in response_list]
    return response_list


# requery
def get_high_level_hypotheses(hypothesis_list):
    response = gpt_obj.query(EXTRACT_HIGH_LEVEL_HYPOTHESES(hypothesis_list, 5))
    hh_list = list(filter(lambda x: len(x) > 5, response.split('\n')))
    hh_list = [x.split(":")[-1].strip(" ").strip("*") for x in hh_list]

    # Remap the individual claims back to the high-level hypotheses
    hypothesis_mapping = {}
    for hh in hh_list:
        response = gpt_obj.query(REMAP_HIGH_LEVEL_HYPOTHESES(hypothesis_list, hh))
        clean_response = list(filter(lambda x: len(x) > 5, response.split('\n')))
        clean_response = [x.split(":")[-1] for x in clean_response]
        hypothesis_mapping[hh] = clean_response
    return hypothesis_mapping


# keep low-level claims combined with new high levels
def get_high_level_hypotheses_combined(hypothesis_list):
    response = gpt_obj.query(COLLECT_HIGH_LEVEL_HYPOTHESES(hypothesis_list))
    hh_list = list(filter(lambda x: len(x) > 5, response.split('\n')))

    hypothesis_mapping = {}
    latest_claim = ""
    for line in hh_list:
        type, text = line.split(":")
        if "Header" in type:
            claim = text.strip()
            hypothesis_mapping[claim] = []
            latest_claim = claim
        else:
            hypothesis_mapping[latest_claim].append(text.strip())
    return hypothesis_mapping


def pprint(hypothesis_mapping):
    for h in hypothesis_mapping:
        print(h)
        for x in hypothesis_mapping[h]:
            print("\t * " + x)


if __name__ == '__main__':
    hypotheses_list, all_hh_mappings = extract_hypotheses("alcohol")
    for h in hypotheses_list:
        print(h)
    print()
    # hh_mapping = get_high_level_hypotheses(hypotheses_list)
    pprint(all_hh_mappings)

'''
The Duke of Westminster, and the peers who supported his views in the House of Lords, on May 6, had no 
difficulty in showing that the Dark Continent is in process of wholesale demoralisation through the drink trade.
It may even be questioned whether the slave trade does so much harm as the importation of cheap intoxicants. 
For the small sum of ninepence, the native can purchase a gallon of "splendid rum," or, if his taste soars 
higher, he can lay in a whole dozen pints of "superior gin," for half a crown. Were such prices as these 
current in England, it is quite certain that there would be a most lamentable increase of intemperance. 
But by means of fiscal imposts, we place it beyond the power of the bibulous to get drunk for a few pence. 
That being our remedy, or rather palliative, the question arises as to why it is not also applied for the 
protection of the African people against the drink demon? For a very good reason; it would be sure to give 
rise to wholesale smuggling and illicit distillation. But even if these difficulties could be surmounted, 
there would be little good in England taking action by herself. The chief effect would be to divert the 
profits on the business from her traders to those of foreign countries. Then, too, as Lord Knutsford 
pointed out, it is almost impossible to enforce restriction in districts possessing any considerable number 
of Europeans among their populations. The whites will have drink, and, when they get it, not a few of them 
use the stuff as a convenient agency for barter with the natives.
There are, no doubt, some places, especially the West Coast settlements, where we are in a stronger 
position to grapple with the trade. Even there, however, the French and German traders would jump at the 
first chance of getting such profitable business into their own hands. The Colonial Secretary mentioned one 
instance in which this lately happened, a Native State under our protection being flooded with spirits from 
Porto Novo, whose King enjoys French protection. Clearly, therefore, the first step towards any effectual 
amelioration of the situation must be to bring about a self-denying ordinance among all Christian Powers 
having dealings with Africa.—*Globe.*

The passage claims that the importation of cheap intoxicants is leading to widespread demoralization in Africa, potentially more harmful than the slave trade.
It is suggested that alcohol is highly accessible to the native population, with a gallon of rum or a dozen pints of gin available for very low prices, indicating a significant issue with affordability and consumption.
The passage compares the situation in Africa with England, noting that if similar prices for alcohol existed in England, it would likely lead to increased intemperance, highlighting a disparity in alcohol regulation between the two regions.
The text discusses the difficulties of enforcing alcohol restrictions in Africa, particularly in areas with European populations, suggesting that the presence of Europeans complicates efforts to control the alcohol trade.
The passage implies that the alcohol trade is economically significant, with concerns that restricting it in Africa would merely shift profits to foreign traders rather than eliminate the trade itself.
It is noted that European traders, particularly from France and Germany, are eager to capitalize on the alcohol trade in Africa, indicating a competitive and exploitative economic environment.
The passage suggests that effective action against the alcohol trade in Africa requires a collective effort from all Christian Powers involved, indicating a need for international cooperation to address the issue.
The text mentions that some Europeans use alcohol as a means of barter with the native population, suggesting that alcohol plays a significant role in trade relationships between Europeans and Africans.
'''