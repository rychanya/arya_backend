from itertools import chain

from arya_backend.db import MONGO_DB_NAME, client

collection = client.get_database(MONGO_DB_NAME).get_collection("QA")


def parse_highlight(doc):
    def parse_one(highlight):
        texts = highlight["texts"]
        union = "".join([text["value"] for text in texts])
        path = highlight["path"]
        return (texts, union, path)

    def recombine(origin: str, part, highlight):
        def tohighlight(value):
            if value:
                return [{"value": value, "type": "text"}]
            else:
                return []

        if origin == part:
            return highlight
        prefix, _, sufix = origin.partition(part)
        return list(chain(tohighlight(prefix), highlight, tohighlight(sufix)))

    return {
        path: recombine(doc[path], union, texts)
        for texts, union, path in map(parse_one, doc["highlights"])
    }


def search(q: str):
    print('q', q)
    pipeline = [
        {
            "$search": {
                "wildcard": {
                    "path": "question",
                    "query": f"*{q}*",
                },
                "highlight": {"path": "question"},
            }
        },
        {"$limit": 10},
        {
            "$project": {
                "_id": 0,
                "question": 1,
                "score": {"$meta": "searchScore"},
                "highlights": {"$meta": "searchHighlights"},
            }
        },
    ]
    docs = list(collection.aggregate(pipeline=pipeline))
    print(docs)
    for doc in docs:
        doc["highlights"] = parse_highlight(doc)

    return docs
