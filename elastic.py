import uuid
from elasticsearch import Elasticsearch


def connect_elasticsearch():
    _es = None
    _es = Elasticsearch(
        ["https://c-c9qbvn9fqt1e60l616u1.rw.mdb.yandexcloud.net:9200"],
        basic_auth=("admin", "tMwQHCgwPHWcyvQ9XXwwMc38"),
        verify_certs=False
    )
    if _es.ping():
        print("ES connected")
    else:
        print("Could not connect to ES!")
    return _es


def insert_org(es, url, p_class):
    response = es.index(
        index='yandex_catalogue',
        id=uuid.uuid4(),
        body={"url": url,
              "class": p_class}
    )
    return response


def insert_product(es, body):
    response = es.index(
        index='yandex_products',
        id=uuid.uuid4(),
        body=body
    )
    return response


def match_all_orgs(es):
    all_org = es.search(index="yandex_catalogue", query={"match_all": {}})
    return all_org