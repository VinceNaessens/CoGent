from typing import List
import requests
import json
from api.get_synonyms import get_synonyms

url = 'https://data.collectie.gent/api/graphql HTTP/1.1'
obj_base = {
    "operationName":"getEntities",
    "variables": 
    {
        "limit":25,
        "skip":0,
        "searchValue":
        {
            "value":"panda", ### Search term ###
            "isAsc":False,
            "relation_filter":[],
            "randomize":False,
            "seed":"0.7031277578807555",
            "key":"title",
            "has_mediafile":True,
            "skip_relations":False
        }
    },
    "query":"query getEntities($limit: Int, $skip: Int, $searchValue: SearchFilter!) {\n  Entities(limit: $limit, skip: $skip, searchValue: $searchValue) {\n    count\n    limit\n    results {\n      ...minimalEntity\n      __typename\n    }\n    relations {\n      ...fullRelation\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment minimalEntity on Entity {\n  id\n  object_id\n  type\n  title: metadata(key: [title]) {\n    key\n    value\n    __typename\n  }\n  description: metadata(key: [description]) {\n    key\n    value\n    __typename\n  }\n  primary_mediafile\n  primary_transcode\n  primary_mediafile_info {\n    width\n    height\n    __typename\n  }\n  __typename\n}\n\nfragment fullRelation on Relation {\n  key\n  type\n  label\n  value\n  order\n  __typename\n}\n"
}
headers = {'Content-type': 'application/json'}

obj_base_detail = {
    "operationName":"getEntityById",
    "variables":
    {
        "id":"industriemuseum:V35236-001" ### Search term ###
    },
    "query":"query getEntityById($id: String!) {\n  Entity(id: $id) {\n    ...fullEntity\n    __typename\n  }\n}\n\nfragment fullEntity on Entity {\n  id\n  type\n  title: metadata(key: [title]) {\n    key\n    value\n    __typename\n  }\n  scopeNote: metadata(key: [scopeNote]) {\n    key\n    value\n    __typename\n  }\n  description: metadata(key: [description]) {\n    key\n    value\n    __typename\n  }\n  objectNumber: metadata(key: [object_number]) {\n    key\n    value\n    __typename\n  }\n  metadataCollection(\n    key: [title, description, object_number, scopeNote]\n    label: []\n  ) {\n    ...MetadataCollectionFields\n    __typename\n  }\n  primary_mediafile\n  primary_transcode\n  mediafiles {\n    _id\n    original_file_location\n    transcode_filename\n    thumbnail_file_location\n    mimetype\n    filename\n    metadata {\n      key\n      value\n      __typename\n    }\n    __typename\n  }\n  relations {\n    key\n    type\n    label\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment MetadataCollectionFields on MetadataCollection {\n  label\n  nested\n  data {\n    value\n    unMappedKey\n    label\n    nestedMetaData {\n      ...NestedEntity\n      metadataCollection(\n        key: [title, description, object_number, scopeNote]\n        label: [\"objectnummer\"]\n      ) {\n        label\n        nested\n        data {\n          value\n          unMappedKey\n          label\n          nestedMetaData {\n            ...nestedEndEntity\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment NestedEntity on Entity {\n  id\n  type\n  title: metadata(key: [title]) {\n    key\n    value\n    __typename\n  }\n  description: metadata(key: [description]) {\n    key\n    value\n    __typename\n  }\n  objectNumber: metadata(key: [object_number]) {\n    key\n    value\n    __typename\n  }\n  mediafiles {\n    _id\n    original_file_location\n    transcode_filename\n    filename\n    __typename\n  }\n  relations {\n    key\n    type\n    label\n    value\n    __typename\n  }\n  __typename\n}\n\nfragment nestedEndEntity on Entity {\n  id\n  type\n  title: metadata(key: [title]) {\n    key\n    value\n    __typename\n  }\n  description: metadata(key: [description]) {\n    key\n    value\n    __typename\n  }\n  objectNumber: metadata(key: [object_number]) {\n    key\n    value\n    __typename\n  }\n  metadataCollection(\n    key: [title, description, object_number, scopeNote]\n    label: [\"objectnummer\"]\n  ) {\n    label\n    nested\n    data {\n      value\n      unMappedKey\n      label\n      __typename\n    }\n    __typename\n  }\n  mediafiles {\n    _id\n    original_file_location\n    transcode_filename\n    filename\n    __typename\n  }\n  relations {\n    key\n    type\n    label\n    value\n    __typename\n  }\n  __typename\n}\n"
}

def get_art(basis_word: str) -> List[str]:
    res = get_synonyms(basis_word=basis_word)
    ids = []
    results = []
    for syn in res:
        obj = obj_base
        obj["variables"]["searchValue"]["value"] = syn
        x = requests.post(url, data = json.dumps(obj), headers=headers)
        for result in x.json()["data"]["Entities"]["results"]:
            if result["id"] not in ids:
                result["synonym"] = syn

                obj = obj_base_detail
                obj["variables"]["id"] = result["object_id"]
                details = requests.post(url, data = json.dumps(obj), headers=headers).json()["data"]["Entity"]
                result["details"] = details

                results.append(result)
                ids.append(result["id"])
                
    return results