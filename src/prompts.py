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