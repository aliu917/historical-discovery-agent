def FIND_COMPARE_PROMPT(subject, african_times_claims, gha_chunk, comparison, general_area="African history", source_1="the African Times", source_2="the General History of Africa textbook"):
    african_times_list_str = "\n".join(["* " + r for r in african_times_claims])
    differences_txt = ""
    if comparison == "differences":
        differences_txt = f"\nIf {source_2} is missing information relating to any claims, that is interesting as well, and please point that out and include what {source_2} focuses on instead in a similar topic area."
    return f"""I have two different historical sources that discuss {subject} in general {general_area}.
From {source_1}, I have found the following claims about {subject}:
{african_times_list_str}
From {source_2}, we have the following paragraph discussing {subject}:
{gha_chunk}\n
For the claims in the list above, find any specific and meaningful {comparison} between the claim and the paragraph chunk from {source_2}.
Make sure to only discuss topics relating to {subject}. If some sections of the paragraph in {source_2} are unrelated to {subject}, then ignore those statements.
We define "meaningful" as any fact that an expert historian studying this area would be interested in discovering has {comparison} between {source_1} and {source_2}. Please keep specific details that are relevant from each source. {differences_txt}
If there are no {comparison} at all, feel free to say that there are no {comparison} with a very short justification.
"""


def EXTRACT_HYPOTHESES_FROM_CHUNK(chunk, focus_topic=None, historical_topic="the history of Africa"):
    focus_topic_str = ""
    if focus_topic:
        focus_topic_str = ", specifically centering around " + focus_topic
    return f"""For the following passage of text, determine a list of hypotheses or claims about {historical_topic}{focus_topic_str}.
A hypothesis or claim should be a statement that may be argued for or against given evidence. Choose hypotheses that an amateur historian studying {historical_topic} would find interesting or novel.

Here is an example:
Passage: 
I must not be misunderstood. Though I hold the British rule in India to be a curse, I do not therefore consider Englishmen in general to be worse than any other people on earth. I have the privilege of claiming many Englishmen as dearest friends. Indeed much that I have learnt of the evil of British rule is due to the writings of frank and courageous Englishmen who have not hesitated to tell the unpalatable truth about that rule. 
And why do I regard the British rule as a curse? 
It has impoverished the dumb millions by a system of progressive exploitation and by a ruinously expensive military and civil administration which the country can never afford. 
It has reduced us politically to serfdom. It has sapped the foundations of our culture, and, by the policy of disarmament, it has degraded us spiritually. Lacking inward strength, we have been reduced by all but universal disarmament to a state bordering on cowardly helplessness. 

Response:
The British Rule in India impoverished the country by exploiting its resources and labor.
Through disarmament, the British treated Indians politically as second class citizens, destroying their morale and identity.
Indians did not view Englishmen as inherently evil, but rather their subjugation by English policies as the evil.

Please structure the response as a single sentence for each claim, separated by a newline for each statement as shown above.

Passage: {chunk}
Response:
""" # TODO: Consider a please don't include commentary statement?


def EXTRACT_COMMON_CLAIMS(response_list):
    response_list_str = "\n".join(response_list)
    return f"""For the following list of detailed claims deduced from a primary source text, you'll see many claims are similar or identical. Identify the repeated claims.
A hypothesis or claim should be a statement that may be argued for or against given evidence. Choose hypotheses that an amateur historian studying the history of Africa would find interesting or novel.
If a claim is not repeated in the input, do not include it.
Here is an example:
List of claims: 
[id: 0] The British Rule in India impoverished the country by exploiting its resources and labor
[id: 1] Through disarmament, the British treated Indians politically as second class citizens, destroying their morale and identity
[id: 2] Indians did not view Englishmen as inherently evil, but rather their subjugation by English policies as the evil.
[id: 3] By enforcing disarmament, the British politically marginalized Indians, undermining their morale and identity.
[id: 4] Indians viewed Englishmen as inherently malicious individuals who must be removed from the country at all costs
[id: 5] As a result of the exploitation of their land, many Indians fell into poverty and had to seek demeaning employment under the British.
Response:
* British rule led to widespread poverty in India by systematically extracting its resources and labor.
ids: [0, 5]
* Through the enforcement of disarmament, the British reduced Indians to a politically subordinate status
ids: [1, 3]

List of claims:
{response_list_str}
Response:
"""


def EXTRACT_ONE_COMMON_CLAIM(response_list):
    response_list_str = "\n".join(response_list)
    return f"""For the following list of detailed claims deduced from a primary source text, combine them into one single claim.
A hypothesis or claim should be a statement that may be argued for or against given evidence. Choose hypotheses that an expert historian studying the history of Africa would find interesting or novel.
Return the response as a single sentence.
Here is an example:
List of claims: 
[id: 0] The British Rule in India impoverished the country by exploiting its resources and labor
[id: 5] As a result of the exploitation of their land, many Indians fell into poverty and had to seek demeaning employment under the British.
Response:
British rule led to widespread poverty in India by systematically extracting its resources and labor.

List of claims:
{response_list_str}
Response:
"""


def SUMMARIZE_KEY_POINTS(long_text, topic, source_1="the African Times", source_2="the General History of Africa textbook"):
    return f"""We have found the following similarities and differences between {source_1} and {source_2} on the topic of {topic}:
{long_text}\n
Summarize and collect the meaningful similarities and differences that we can draw from all of these observations between the two texts.
Note that if there are differences caused by a topic not being mentioned in one text, but this same topic is mentioned in that text later on in another observation, then we can conclude that the topic was mentioned and combine the observations.
Disregard any observations that are not related to the overall topic of {topic}.
We define "meaningful" as any fact that an expert historian studying this area would be interested in discovering in terms of similarities and differences between {source_1} and {source_2}, which specific details and references to one source or the other.
Collect similar observations into a single combined observation to reduce the number of distinct bullet points, while keeping all relevant details as specific as possible.
All observations should reference and retain at least one specific detail drawn from each text to avoid making vague blanket observations.
"""

def SUMMARIZE_FINAL_KEY_POINTS(topic_comparison_map, topic, source_1="the African Times", source_2="the General History of Africa textbook"):
    long_text = ""
    for topic in topic_comparison_map:
        long_text += f"Topic: {topic}\nComparison on the topic of {topic}:\n{topic_comparison_map[topic]}\n"
    return f"""We have found the following similarities and differences between {source_1} and {source_2} relating to the overarching topic of {topic} in a series of grouped sections.
{long_text}\n
Summarize and collect the meaningful similarities and differences from each topic that we can draw from all of these observations between the two texts.
Disregard any facts or observations not related to the overall topic of {topic}.
We define "meaningful" as any fact that an expert historian studying this area would be interested in discovering in terms of similarities and differences between {source_1} and {source_2}.
Collect similar observations into a single combined observation to reduce the number of distinct bullet points, while keeping all relevant details as specific as possible.
All observations should reference and retain at least one specific detail drawn from each text to avoid making vague blanket observations.
"""

def FIND_SIMILAR_TOPIC_PROMPT(subject):
    return f"""I'm looking for information about the topic "{subject}" in a series of documents. All documents are already known to be related to African history, so we do not have to search for general Africa keywords unless they are referring to a more specific region of Africa that would help narrrow down the search.
    Please provide some additional key words or phrases related to this topic that I can search for in my document vector database. Make sure to identify the key topical words which make the topic unique and suggest some synonymous searches.
    Return the words as a single string list. Make sure not to include words that may have other very different meanings and cause false negative search matches.
    Here is an example:
    Topic: impact of wealth on African trade
    Response: riches, money, power imbalance, trade goods

    Topic: {subject}
    Response: """


def HH_COMPARE_PROMPT(hh_claim, chunks, source, cite=False):
    if cite:
        return
    format_chunks = ""
    for chunk in chunks:
        if "content" in chunk:
            content = "content"
        else:
            content = "content_string"
        format_chunks += f'* {chunk[content]}\n'
    return f"""Read the following paragraphs from {source}:\n{format_chunks}\n\n
From the above paragraphs, determine any details that support, refute, or are associated with the claim: {hh_claim}.\n
We define meaningful details as any fact that an expert historian studying this area would be interested in discovering in terms of similarities and differences between the content in {source} and the claim.
If the {source} does not include any information related to the claim, this is an interesting difference as well.
Return the output of observations in the format of a short paragraph, paying particular attention to both similarities and differences between the claims and paragraphs."""



def HH_COMPARE_PROMPT_CITE(hh_claim, chunks, source):
    format_chunks = ""
    for i, chunk in enumerate(chunks):
        format_chunks += f'[{i}] \"{chunk["content"]}\"\n'
    return f"""Read the following paragraphs from {source}:\n{format_chunks}\n\n
From the above paragraphs, determine any details that support, refute, or are associated with the claim: {hh_claim}.\n
First, identify the paragraphs that are relevant and provide useful information for comparison against the claim. Then, using only those paragraphs, compare and contrast the claim with the content in the relevant paragraph.
We define meaningful details as any fact that an expert historian studying this area would be interested in discovering in terms of similarities and differences between the content in {source} and the claim.
If the {source} does not include any information related to the claim, this is an interesting difference as well.
Please return only the output of observations in the format of a short paragraph, paying particular attention to both similarities and differences between the claims and paragraphs.
Additionally, for each paragraph chunk that was identified as relevant to the claim, please list these bracketed numbers at the end of the response (ex: 'response [i][j][k]')."""


def HH_COMBINE_PROMPT(hh_claim, gha_details, tat_details):
    return f"""Combine the obsevations from the General History of Africa textbook and The African Times news articles about the following claim: {hh_claim}.\n
From the General History of Africa, we observe the following related to the claim: {gha_details}.\n
From The African Times, we observe the following related to the claim: {tat_details}.\n
Combine the two observations into a coherent paragraph without losing any relevant details from either source."""

if __name__ == '__main__':
    # print(GENERALIZE_HIGH_LEVEL_HYPOTHESES(["note1", "note2", "note3"]))
    # print(FIND_COMPARE_PROMPT("silk road", ["The silk road was hot", "The silk road had many bandits"], "The Silk Road facilitated significant cultural exchanges between different civilizations.", "similarities"))
    # print(FIND_COMPARE_PROMPT("silk road", ["The silk road was hot", "The silk road had many bandits"], "The Silk Road facilitated significant cultural exchanges between different civilizations.", "differences"))
    prompt = HH_COMPARE_PROMPT(
        "The introduction of alcohol by European traders had a devastating impact on African societies, contributing significantly to the decline of coastal tribes.",
        [{'document_title': 'The social repercussions of colonial rule: demographic aspects', 'section_title': 'The clashing forces of demographic change up to and beyond 1880', 'content': 'These were the major forces determining population change but there were undoubtedly others. Commerce was one, although whether such activities brought prosperity and the ability to buy food in times of need and perhaps some health care in the few places where it existed to a greater degree than it brought disease arising from increased contact with strangers is debatable. By 1880 cash crops included the cotton of Egypt, cloves in Zanzibar, sugar in Natal and an increasing area of groundnuts (peanuts) in Senegal, while in Algeria a European settler economy largely based on wheat and wine was being established. One aspect of trade almost certainly did have a deleterious effect on health, and that is the flow of strong alcoholic drink into the continent. There were two reasons for the trade: firstly that alcohol could be produced cheaply in Europe and sold for immense profits; secondly, in economies without widely accepted mediums of exchange, there were real problems about what goods would be accepted in return for the produce of Africa.$^{43}$ Mary Kingsley found the trade spirit pure and likely to do less harm than cannabis,$^{44}$ a view shared by a committee that investigated the liquor trade in içoç.$^{45}$ Spirits were distributed on a huge scale, frequently as wages. In 1894 half the total government revenue and 95 per cent of the customs duties of the Niger Coast Protectorate were derived from spirits; by 1894 the governmental income from this source totalled nearly £2 million.$^{46}$ Although the Brussels Act of 1892 tried unsuccessfully to limit the trade in the Congo (now Zaire), it was not successfully regulated in tropical Africa until the eve of the First World War.', 'last_edit_date': None, 'url': None, 'num_tokens': 0, 'block_metadata': None, 'similarity_score': 0.666, 'probability_score': 0.052},
         {'document_title': 'The Niger delta and the Cameroon region',
          'section_title': 'The Niger delta > The Igbo hinterland',
          'content': 'The predominantly disruptive character of the slave trade may be shown in different ways. First, the manner in which slaves were procured tended to destroy social and political structures. Social outcasts, offenders against the law, were sold into slavery. A few persons were sold in times of famine or for debt. But the majority of slaves were apparently taken by kidnapping, raiding and wars. The oracle of the Aro is also known to have sold persons it adjudged guilty. But the Aro trade network throughout most of Igboland also obtained many of its slaves through the raids of its mercenary allies, the Abam, Ohaffia, Abiriba, and Edda. Accordingly, the extensive influence exercised by the Aro over Igboland through its oracle did not become an integrative force.$^{9}$ The element of violence inherent in Aro addiction to the slave trade thus distinguished their influence from the earlier ritual influ› ence of the Nri people over wide areas of Igboland.\nIn the economic sphere also, the disruption to normal agricultural activities must have been considerable. In addition, as was the case in the trade between the coastal middlemen and the Europeans, what the Igbo obtained for the slaves taken out was never commensurate with the total loss sustained as a result of the slave trade. Slaves were paid for with salt, fish, spirits, firearms, hats and beads, as well as iron, copper, and brass bars. The metal bars were turned into pewters, ritual bells, state swords, leg-rings, and other ornaments. But these supplies replaced local industries, and the Awka smiths turned their backs on local sources of metal. Import› ation of salt and cloth also undermined local industries.',
          'last_edit_date': None, 'url': None, 'num_tokens': 0, 'block_metadata': None, 'similarity_score': 0.612,
          'probability_score': 0.049},
         {'document_title': 'The countries of the Zambezi basin',
          'section_title': 'The slave trade and incorporation into the capitalist world economy',
          'content': "rapidly becoming desert. About midday they came upon a large party of Ajawa [Yao], who were just returning from a successful raid. The smoke of burning villages was seen in the distance. A long train of captives carried the plunder, and their bitter cry was heard, even above the triumphant utterances of the Ajawa women, who came out... to welcome back the visitors. 53 Chikunda forays in the homelands of the Chewa, Tonga and Nsenga and as far north as the Lunda of Kazembe, and Arab-Swahili attacks against the people living in the Lake Malawi area produced similar turmoil and decay.$^{54}$ In the most extreme instances, entire regions were depopulated. One British official recanted in 1861 that 'An Arab who lately returned from Lake Nyasa informed me that he travelled for seventeen days through a country covered with ruined towns and villages ... where no living soul is to be seen.' 55 This loss of many of the most productive members of the society reinforced the rural dislocation. Although the evidence is uneven, data from the Zambezi region, the Shire valley and the Lake Malawi region suggest that famines recurred with great regularity,$^{56}$ which often necessi› tated the exchange of slaves for food, further intensifying the population drain. Whatever the case, the unstable conditions and threats of new raids prevented the resurgence of the rural economy.",
          'last_edit_date': None, 'url': None, 'num_tokens': 0, 'block_metadata': None, 'similarity_score': 0.622,
          'probability_score': 0.05}
        ],
        "General History of Africa textbook",
        True
    )
    print(prompt)

