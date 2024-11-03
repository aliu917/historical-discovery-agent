def RERANK_PROMPT(subject, retrieved_content):
    return f"""I'm looking for information about {subject} in a series of documents. 
Extract the sections of the following text that reference this subject, along with surrounding context needed to understand the section.
Conduct the extraction verbatim.

{retrieved_content}"""


def RERANK_DOCS_PROMPT(subject, retrieved_content):
    return f"""I'm looking for information about the topic "{subject}" in a series of documents. All documents are already known to be related to African history, and I am looking for specific mentions of this topic or closely synonymous topics in the document content. 
From the list of section ID and section content below, identify the rows where the section content references this topic.
Return a list containing each section ID and section content pair in the following format, but with the section content only containing the surrounding context needed to understand the topic.

{retrieved_content}"""


def FIND_SIMILAR_TOPIC_PROMPT(subject):
    return f"""I'm looking for information about the topic "{subject}" in a series of documents. All documents are already known to be related to African history, so we do not have to search for general Africa keywords unless they are referring to a more specific region of Africa that would help narrrow down the search.
    Please provide some additional key words or phrases related to this topic that I can search for in my document vector database. Make sure to identify the key topical words which make the topic unique and suggest some synonymous searches.
    Return the words as a single string list. Make sure not to include words that may have other very different meanings and cause false negative search matches.
    Here is an example:
    Topic: impact of wealth on African trade
    Response: riches, money, power imbalance, trade goods
    
    Topic: {subject}
    Response: """

def COMPARE_TEXTS_PROMPT(subject, gha_textbook, african_times_docs):
    return f"""I have two historical sources that discuss {subject} in African history. The first is a general history textbook, with the following text: 

General History of Africa: {gha_textbook}

Another source is letters submitted to the African times, with the following text:

Letters to African Times: {african_times_docs}
     
Identify meaningful differences in perspective between these two sources. How do the African times letters provide nuance to the more general statements made by the General History of Africa?"""


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
Include references to specific details from the passage.
Here is an example:
Passage: This ancient trade network not only facilitated the exchange of goods like silk and spices but also played a crucial role in cultural, technological, and religious exchanges between East and West. The interactions along the Silk Road shaped civilizations and influenced the development of art, science, and philosophy across continents. There are so many fascinating stories, from the journeys of merchants to the impact of ideas like Buddhism and Islam spreading along these routes!
Response:
1. Cultural exchange: The Silk Road facilitated significant cultural exchanges between different civilizations.
2. Technological Transfer: Innovations and technologies were shared and spread along the Silk Road, influencing various societies.
3. Religious Influence: Major religions, such as Buddhism and Islam, were disseminated through interactions on the Silk Road.
4. Economic Impact: The trade of goods like silk and spices had a substantial economic impact on the civilizations involved.
5. Artistic Development: The exchange of ideas and materials contributed to the development of art across different cultures.
6. Interconnectedness of Civilizations: The Silk Road illustrates how interconnected various regions of the world were, even in ancient times.
7. Merchant Journeys: The journeys of merchants along the Silk Road were significant in shaping trade practices and routes.

Passage: {chunk}
Response:
"""


def COLLECT_HIGH_LEVEL_HYPOTHESES(response_list):
    response_list_str = "\n".join(response_list)
    return f"""For the following list of detailed claims deduced from a primary source text, we want to search for similar topics and claims in a larger
textbook corpora. Group similar hypotheses into an overarching topic header that can be used to formulate a higher level claim that we can search for,
either to prove or refute from a different source text. 
Output the response as the overarching header text along with the original hypotheses that are grouped within it.
The same hypothesis can fall under multiple header texts if relevant. Make sure each original hypothesis falls under at least 
one topic header. Please return the hypothesis texts verbatim.
Here is an example:
List of hypotheses: 
The Silk Road facilitated significant cultural exchanges between different civilizations.
Innovations and technologies were shared and spread along the Silk Road, influencing various societies.
Major religions, such as Buddhism and Islam, were disseminated through interactions on the Silk Road.
The trade of goods like silk and spices had a substantial economic impact on the civilizations involved.
The exchange of ideas and materials contributed to the development of art across different cultures.
The Silk Road illustrates how interconnected various regions of the world were, even in ancient times.
The journeys of merchants along the Silk Road were significant in shaping trade practices and routes.
Response:
Header: Cultural Exchange in Ancient Trade Networks
Hypothesis: The Silk Road facilitated significant cultural exchanges between different civilizations.
Hypothesis: The exchange of ideas and materials contributed to the development of art across different cultures.
Hypothesis: The Silk Road illustrates how interconnected various regions of the world were, even in ancient times.
Header: Technological Innovations along the Silk Road
Hypothesis: Innovations and technologies were shared and spread along the Silk Road, influencing various societies.
Header: Religious Diffusion via Trade Networks
Hypothesis: Major religions, such as Buddhism and Islam, were disseminated through interactions on the Silk Road.
Header: Economic Impact of the Silk Road on Empires
Hypothesis: The trade of goods like silk and spices had a substantial economic impact on the civilizations involved.
Header: Role of Merchants in Cross-Cultural Exchange
Hypothesis: The Silk Road illustrates how interconnected various regions of the world were, even in ancient times.
Hypothesis: The journeys of merchants along the Silk Road were significant in shaping trade practices and routes.

List of hypotheses:
{response_list_str}
Response:
"""


def EXTRACT_HIGH_LEVEL_HYPOTHESES(response_list, n=5):
    response_list_str = "\n".join(response_list)
    return f"""For the following list of detailed claims deduced from a primary source text, determine at most {n} high-level topic headers that can encompass all claims.
We want a short list of headers that are specific enough to be non-overlapping but are general enough to cover all claims, so that every claim can be attributed to at least one header.
Here is an example:
List of claims: 
The Silk Road facilitated significant cultural exchanges between different civilizations.
Innovations and technologies were shared and spread along the Silk Road, influencing various societies.
Major religions, such as Buddhism and Islam, were disseminated through interactions on the Silk Road.
The trade of goods like silk and spices had a substantial economic impact on the civilizations involved.
The exchange of ideas and materials contributed to the development of art across different cultures.
The Silk Road illustrates how interconnected various regions of the world were, even in ancient times.
The journeys of merchants along the Silk Road were significant in shaping trade practices and routes.
Response:
Topic 1: Information Exchange in Ancient Trade Networks
Topic 2: Economic Impact of the Silk Road on Empires

List of claims:
{response_list_str}
Response:
"""


def REMAP_HIGH_LEVEL_HYPOTHESES(response_list, hh_claim):
    response_list_str = "\n".join(response_list)
    return f"""For the following list of detailed claims deduced from a primary source text, determine which of them are related to the higher-level topic header.
Here is an example:
List of claims: 
The Silk Road facilitated significant cultural exchanges between different civilizations.
Innovations and technologies were shared and spread along the Silk Road, influencing various societies.
Major religions, such as Buddhism and Islam, were disseminated through interactions on the Silk Road.
The trade of goods like silk and spices had a substantial economic impact on the civilizations involved.
The exchange of ideas and materials contributed to the development of art across different cultures.
The Silk Road illustrates how interconnected various regions of the world were, even in ancient times.
The journeys of merchants along the Silk Road were significant in shaping trade practices and routes.
High-level topic header: Information Exchange in Ancient Trade Networks
Response:
Claim: The Silk Road facilitated significant cultural exchanges between different civilizations.
Claim: Innovations and technologies were shared and spread along the Silk Road, influencing various societies.
Claim: Major religions, such as Buddhism and Islam, were disseminated through interactions on the Silk Road.
Claim: The exchange of ideas and materials contributed to the development of art across different cultures.

List of claims:
{response_list_str}
High-;evel topic header: {hh_claim}
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

if __name__ == '__main__':
    # print(GENERALIZE_HIGH_LEVEL_HYPOTHESES(["note1", "note2", "note3"]))
    print(FIND_COMPARE_PROMPT("silk road", ["The silk road was hot", "The silk road had many bandits"], "The Silk Road facilitated significant cultural exchanges between different civilizations.", "similarities"))
    print(FIND_COMPARE_PROMPT("silk road", ["The silk road was hot", "The silk road had many bandits"], "The Silk Road facilitated significant cultural exchanges between different civilizations.", "differences"))

