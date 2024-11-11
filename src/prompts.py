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
* The British Rule in India impoverished the country by exploiting its resources and labor
* Through disarmament, the British treated Indians politically as second class citizens, destroying their morale and identity
* Indians did not view Englishmen as inherently evil, but rather their subjugation by English policies as the evil.

Passage: {chunk}
Response:
""" # TODO: Consider a please don't include commentary statement?


def EXTRACT_COMMON_CLAIMS(response_list):
    response_list_str = "\n".join(response_list)
    return f"""For the following list of detailed claims deduced from a primary source text, you'll see many claims are similar or identical. Identify the repeated claims.
A hypothesis or claim should be a statement that may be argued for or against given evidence. Choose hypotheses that an amateur historian studying the history of Africa would find interesting or novel.
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


def HH_COMPARE_PROMPT(hh_claim, chunks, source):
    format_chunks = ""
    for chunk in chunks:
        format_chunks += f'* {chunk["content"]}\n'
    return f"""Read the following paragraphs from {source}:\n{format_chunks}\n\n
From the above paragraphs, determine any details that support, refute, or are associated with the claim: {hh_claim}.\n
We define meaningful details as any fact that an expert historian studying this area would be interested in discovering in terms of similarities and differences between the content in {source} and the claim.
If the {source} does not include any information related to the claim, this is an interesting difference as well.
Return the output of observations in the format of a short paragraph, paying particular attention to both similarities and differences between the claims and paragraphs."""


def HH_COMBINE_PROMPT(hh_claim, gha_details, tat_details):
    return f"""Combine the obsevations from the General History of Africa textbook and The African Times news articles about the following claim: {hh_claim}.\n
From the General History of Africa, we observe the following related to the claim: {gha_details}.\n
From The African Times, we observe the following related to the claim: {tat_details}.\n
Combine the two observations into a coherent paragraph without losing any relevant details from either source."""

if __name__ == '__main__':
    # print(GENERALIZE_HIGH_LEVEL_HYPOTHESES(["note1", "note2", "note3"]))
    print(FIND_COMPARE_PROMPT("silk road", ["The silk road was hot", "The silk road had many bandits"], "The Silk Road facilitated significant cultural exchanges between different civilizations.", "similarities"))
    print(FIND_COMPARE_PROMPT("silk road", ["The silk road was hot", "The silk road had many bandits"], "The Silk Road facilitated significant cultural exchanges between different civilizations.", "differences"))

