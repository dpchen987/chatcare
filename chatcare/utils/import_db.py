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

# # Create a Milvus connection
# def create_connection():
#     print(f"\nCreate connection...")
#     connections.connect(host=_HOST, port=_PORT)
#     print(f"\nList connections:")
#     print(connections.list_connections())


def connect_db(name):
    if utility.has_collection(name):
        collection = Collection(name)
    else:
        print(f'No database named {name}')

    return collection


def import_data(excel_file, import_mode, name):
    col = connect_db(name)
    id_start = 0
    excel_data = pd.read_excel(excel_file)

    if import_mode == "append":
        # get the latest id when appending
        if not col.is_empty:
            id_start = col.query(expr="id>=0")[-1]['id']
    elif import_mode == "all":
        col.delete()

    questions = list(excel_data['question'])
    data = [
        list(range(id_start, id_start+len(excel_data))),    # id
        [bge.encode_queries(q) for q in questions],         # vector_id
        questions,                                          # question
        list(excel_data['answer'])                          # answer
    ]
    col.insert(data)
    col.flush()
    print("Finish inserting")

    return 0


if __name__ == '__main__':
    # python import_db.py excel.xlsx append --db_name name
    parser = argparse.ArgumentParser(description="Import Excel data into Milvus")
    parser.add_argument("excel_file", help="Path to the Excel file")
    parser.add_argument("import_mode", choices=["append", "all"], help="Import mode: 'append' or 'all'")
    parser.add_argument("--db_name", help="Name of the Milvus database", default='care_qa')

    args = parser.parse_args()
    # print(args)
    import_data(args.excel_file, args.import_mode, args.db_name)

