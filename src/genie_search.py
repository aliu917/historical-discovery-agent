import requests

POST_URL = "https://search.genie.stanford.edu/"

# Ignore title and concluding chapters
GHA_IGNORE = [
    "GENERAL HISTORY OF AFRICA VI",
    "Members of the International Scientific Committee for the Drafting of a General History of Africa",
    "GENERAL HISTORY OF AFRICA VII",
]


def post_request(collection, query, num_blocks=10, rerank=True, num_blocks_to_rerank=10):
    if isinstance(query, list):
        query_list = query
    else:
        query_list = [query]

    data = {
        "query": query_list,
        "rerank": rerank,
        "num_blocks_to_rerank": num_blocks_to_rerank,
        "num_blocks": num_blocks,
    }

    response = requests.post(POST_URL + collection, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"POST request failed for query {query} with status code: {response.status_code}")
        print("Response content:", response.text)


def african_times_request(query, num_blocks=10, rerank=True, num_blocks_to_rerank=10):
    return post_request("the_african_times", query, num_blocks, rerank, num_blocks_to_rerank)


def gha_request(query, num_blocks=20, rerank=True, num_blocks_to_rerank=20):
    results = post_request("general_history_of_africa", query, num_blocks, rerank, num_blocks_to_rerank)
    if isinstance(query, list):
        for i, q in enumerate(query):
            results[i]['results'] = list(filter(lambda x: print("x: ", x), results[i]['results']))
    else:
        results[0]['results'] = list(filter(lambda x: x['title'] not in GHA_IGNORE, results[0]['results']))
    return results


if __name__ == '__main__':
    response_json = african_times_request("role of alcohol in africa", 10)
    print("african times")
    for result in response_json[0]['results']:
        print(result)
    print()
    response_json = gha_request("alcohol", 10)
    print("gha")
    for result in response_json[0]['results']:
        print(result)
