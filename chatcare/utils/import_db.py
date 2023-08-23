from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, DataType,
    Collection,
    utility
)
import pandas as pd
import argparse
from chatcare.embeddings.embedding_bge import bge

_HOST = '127.0.0.1'
_PORT = '19530'
_VECTOR_FIELD_NAME = 'vector_field'
_DIM = 768
_METRIC_TYPE = 'L2'
_INDEX_TYPE = 'HNSW'
_M = 32
_EFCONSTRUCTION = 128
_EF = 16
_NPROBE = 16
_TOPK = 3


# Create a Milvus connection
def create_connection():
    print(f"\nCreate connection...")
    connections.connect(host=_HOST, port=_PORT)
    print(f"\nList connections:")
    print(connections.list_connections())


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



# Create a collection named 'demo'
def create_collection(collection_name):
    field_id = FieldSchema(name="id", dtype=DataType.INT64,
                           description="int64", is_primary=True)
    field_vec = FieldSchema(name=_VECTOR_FIELD_NAME,
                            dtype=DataType.FLOAT_VECTOR,
                            description="float vector", dim=_DIM,
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


def connect_db(name):
    create_connection()
    if utility.has_collection(name):
        collection = Collection(name)
    else:
        collection = create_collection(name)
    #collection.load()
    return collection


def import_data(collection, name, excel_file, import_mode):
    id_start = 0
    excel_data = pd.read_excel(excel_file)

    if import_mode == "append":
        # get the latest id when appending
        if not collection.is_empty:
            collection.load()
            id_start = collection.query(expr="id>=0")[-1]['id']
    elif import_mode == "all":
        if not collection.is_empty:
            collection.drop()
            collection = create_collection(name)

    questions = list(excel_data['question'])
    data = [
        list(range(id_start, id_start+len(excel_data))),    # id
        [bge.encode_queries(q) for q in questions],         # vector_id
        questions,                                          # question
        list(excel_data['answer'])                          # answer
    ]
    primary_key = data[0]

    collection.insert(data, primary_keys=primary_key)
    collection.flush()

    if id_start == 0:
        get_entity_num(collection)
        create_index(collection, _VECTOR_FIELD_NAME)

    print("Finish inserting")


if __name__ == '__main__':
    # python import_db.py excel.xlsx append --db_name name
    parser = argparse.ArgumentParser(description="Import Excel data into Milvus")
    parser.add_argument("excel_file", help="Path to the Excel file")
    parser.add_argument("import_mode", choices=["append", "all"], help="Import mode: 'append' or 'all'")
    parser.add_argument("--db_name", help="Name of the Milvus database", default='care_qa')

    args = parser.parse_args()
    # print(args)
    create_connection()
    collection = connect_db(args.db_name)

    import_data(collection, args.db_name, args.excel_file, args.import_mode)
    
