def RERANK_PROMPT(subject, retrieved_content):
    return f"""I'm looking for information about {subject} in a series of documents. Extract the sections of the following text that reference this subject. Conduct the extraction verbatim.

{retrieved_content}"""