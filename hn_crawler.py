import requests
from bs4 import BeautifulSoup
from functools import lru_cache
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

thread = 12627852

def clean_text(data):
    try:
        clean_text = BeautifulSoup(data['text'], "html.parser").text
        data['text'] = clean_text
        return data
    except KeyError:
          return {}

@lru_cache(maxsize=5000)
def fetch_hn_data(thread):
    url = "https://hacker-news.firebaseio.com/v0/item/{}.json".format(thread)
    r = requests.get(url)
    assert r.status_code == 200
    data = r.json()
    data = clean_text(data)
    return data
data = fetch_hn_data(thread)


es = Elasticsearch()
# es.indices.delete(index='hn')

mappings = {
    "mappings" : {
        "post" : {
            "properties" : {
                "time" : {
                    "type" : "date",
                    "format" : "strict_date_optional_time||epoch_millis"
                }
            }
        }
    }
}
es.indices.create(index='hn', body=mappings)

def format_data_for_action(post_id):
    data = fetch_hn_data(post_id)
    #if the text field is not present, the post has been deleted
    if not data:
        return {}
    return {
        '_index': 'hn',
        '_type': 'post',
        '_id': post_id,
        '_source': data
    }

acts = [format_data_for_action(r) for r in data['kids'] if format_data_for_action(r)]
list(parallel_bulk(es, acts))

query = {"query" : {
        "bool" : {
            "must" : [{
                "match": {'text' : 'san francisco'}},
                {"match": {'text' : 'machine learning'}}
            ]

        }

    }}

#sanity check
print(es.search(index='hn', body=query)['hits']['total'])
