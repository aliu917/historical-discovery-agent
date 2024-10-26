import requests

POST_URL = "https://search.genie.stanford.edu/the_african_times"


def post_request(query, num_blocks=10, rerank=True, num_blocks_to_rerank=10):
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

    response = requests.post(POST_URL, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"POST request failed for query {query} with status code: {response.status_code}")
        print("Response content:", response.text)


if __name__ == '__main__':
    response_json = post_request("role of alcohol in Africa", 1)
    for result in response_json[0]['results']:
        print(result)