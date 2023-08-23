import time

from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, DataType,
    Collection,
    utility
)

from chatcare.config import params

# Const names
_VECTOR_FIELD_NAME = 'vector_field'

# Index parameters
_METRIC_TYPE = 'L2'
_INDEX_TYPE = 'HNSW'
_M = 32
_EFCONSTRUCTION = 128
_EF = 16
_NPROBE = 16

_COLLECTION = None


# Create a Milvus connection
def create_connection():
    connections.connect(host=params.milvus_host, port=params.milvus_port)
    print(f'{connections.list_connections() = }')


# Create a collection named 'demo'
def create_collection(collection_name):
    field_id = FieldSchema(name="id", dtype=DataType.INT64,
                           description="int64", is_primary=True)
    field_vec = FieldSchema(name=_VECTOR_FIELD_NAME, dtype=DataType.FLOAT_VECTOR,
                            description="float vector", dim=params.embed_dim,
                            is_primary=False)
    field_q = FieldSchema(name="question",
                          dtype=DataType.VARCHAR, max_length=64)
    field_a = FieldSchema(name="answer",
                          dtype=DataType.VARCHAR, max_length=8192)
    schema = CollectionSchema(fields=[field_id, field_vec, field_q, field_a],
                              description="Care QA knowledge")
    collection = Collection(name=collection_name, data=None, schema=schema)
    print("\ncollection created:", collection_name)
    return collection


def has_collection(name):
    return utility.has_collection(name)


# Drop a collection in Milvus
def drop_collection(name):
    collection = Collection(name)
    collection.drop()
    print("\nDrop collection: {}".format(name))


# List all collections in Milvus
def list_collections():
    print("\nlist collections:")
    print(utility.list_collections())


def get_entity_num(collection):
    print("\nThe number of entity:")
    print(collection.num_entities)


def create_index(collection, filed_name):
    index_param = {
        "index_type": _INDEX_TYPE,
        "params": {"M": _M, "efConstruction": _EFCONSTRUCTION},
        "metric_type": _METRIC_TYPE}
    collection.create_index(filed_name, index_param)
    print("\nCreated index:\n{}".format(collection.index().params))


def drop_index(collection):
    collection.drop_index()
    print("\nDrop index sucessfully")


def load_collection(collection):
    collection.load()


def release_collection(collection):
    collection.release()


def set_properties(collection):
    collection.set_properties(properties={"collection.ttl.seconds": 1800})


def search_vec(collection, vector_field, search_vectors, topk):
    search_param = {
        "data": search_vectors,
        "anns_field": vector_field,
        "param": {"metric_type": _METRIC_TYPE, "params": {"ef": _EF}},
        "output_fields": ['answer'],
        "limit": topk}
    results = collection.search(**search_param)
    return results


def init():
    create_connection()
    if not has_collection(params.milvus_collection_name):
        msg = ("no collection for search, "
               "please create collection and index firstly")
        raise ValueError(msg)
    collection = Collection(params.milvus_collection_name)
    collection.load()
    return collection


def kb_search(embed, topk=1):
    global _COLLECTION
    if _COLLECTION is None:
        b = time.time()
        _COLLECTION = init()
        print('====== init for search,', time.time() - b)
    result = search_vec(_COLLECTION, _VECTOR_FIELD_NAME, embed, topk)
    return result
