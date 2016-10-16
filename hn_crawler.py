import requests
from bs4 import BeautifulSoup
from functools import lru_cache
from elasticsearch import Elasticsearch
from elasticsearch import helpers

def clean_text(data):
    try:
        clean_text = BeautifulSoup(data['text'], "html.parser").text
        data['text'] = clean_text
        return data
    except KeyError:
          return {}

def fetch_hn_data(thread, type_='item'):
    url = "https://hacker-news.firebaseio.com/v0/{}/{}.json".format(type_, thread)
    try:
        r = requests.get(url)
        assert r.status_code == 200
        data = r.json()
        if type_ == 'item':
            data = clean_text(data)
    except Exception:
        data = {}
    return data

def find_hiring_thread():
    all_posts = fetch_hn_data('whoishiring', type_='user')['submitted']
    last_three_posts = sorted(all_posts)[-3:]
    for post in last_three_posts:
        data = fetch_hn_data(post)
        if 'is hiring?' in fetch_hn_data(post)['text']:
            break
    return post

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

def update_thread(thread, es=None):
    """Put into the index new child posts"""

    if not es:
        es = Elasticsearch()
    currents_posts = fetch_hn_data(thread)['kids']
    query = {
        "_source": False,
        'query': {
            'term': {"parent": thread}
        }
    }
    older_posts_gen = helpers.scan(es, query)
    old_posts_ids = {int(item['_id']) for item in older_posts_gen}
    new_posts_ids = set(currents_posts) - old_posts_ids
    if new_posts_ids:
        print("There are {} new posts!".format(len(new_posts_ids)))
        actions = [format_data_for_action(r)
            for r in new_posts_ids
            if format_data_for_action(r)]
        list(helpers.parallel_bulk(es, actions))

if __name__ == '__main__':
    es = Elasticsearch()
    assert es.ping(), "Elasticsearch not started properly"
    if not es.indices.exists(index='hn'):
        print('The index does not extis, creating one')
        es.indices.create(index='hn', body=mappings)
    print('Looking for the latests hiring thread...')
    thread = find_hiring_thread()
    print('updating index...')
    update_thread(thread, es)
