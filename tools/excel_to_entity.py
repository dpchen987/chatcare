import os
import re
import json
import opencc
import pandas as pd
import argparse

from chatcare.llms.chatglm2_6b import load_model, infer
from chatcare.utils.logger import logger


def load_excel(excel_file: str) -> tuple:
    df_dict = pd.read_excel(excel_file, sheet_name=['病种', '操作'])
    logger.info(f"Load excel file from --> {os.path.abspath(excel_file)}")
    return df_dict['病种'], df_dict['操作']


def extract_ill_label(df, entity):
    """抽取 `疾病类别` """
    df_sub = df[['类别', '疾病名称']]
    df_sub.loc[:, '类别'] = df_sub['类别'].copy().ffill()
    df_gb = df_sub.groupby(by='类别').agg(set).reset_index()
    for idx, df_item in df_gb.iterrows():
        entity.append(
            {
                'name': df_item['类别'],
                'type': '疾病类别',
                'synonym': [],
                'children': [item for item in df_item['疾病名称'] if not pd.isna(item)],
            }
        )
    return entity


def extract_ill_name(df, entity):
    """抽取 `疾病名称` """
    df_sub = df[['疾病名称', '同义词', '治疗方式', '相关词']].dropna(how='all')
    df_gb = df_sub.groupby(by='疾病名称').agg(list).reset_index()
    for idx, df_item in df_gb.iterrows():
        # name
        ill_name = df_item['疾病名称']
        # synonym
        synonym = []
        for item in list(set(df_item['同义词'])):
            if not pd.isna(item):
                data = item.split(',')
                synonym += data
        synonym = list(set(synonym))
        # children
        care_methods = df_item['治疗方式'] + df_item['相关词']
        children = []
        for cm in care_methods:
            if not pd.isna(cm):
                children.extend(re.findall(r'[\u4e00-\u9fa5]+', cm))
        # append
        entity.append(
            {
                'name': ill_name,
                'type': '疾病名称',
                'synonym': synonym,
                'children': children,
            }
        )
    return entity


def extract_treat_method(df, entity):
    """抽取 `治疗方案` """
    df_sub = df[['治疗方式', '相关词']].copy()
    df_sub.dropna(inplace=True)
    df_sub.drop_duplicates(inplace=True)
    entity_synonym = {}
    for idx, df_item in df_sub.iterrows():
        care_methods = df_item['治疗方式']
        related = df_item['相关词']
        synonym = re.findall(r'[\u4e00-\u9fa5]+', related)
        if care_methods in entity_synonym:
            entity_synonym[care_methods].extend(synonym)
        else:
            entity_synonym[care_methods] = synonym
    for k, v in entity_synonym.items():
        entity.append(
            {
                'name': k,
                'type': '治疗方式',
                'synonym': list(set(v)),
                'children': [],
            }
        )
    return entity


def extract_care_method(df, entity):
    """抽取 操作名称 """
    df_sub = df[['名称']].copy()
    for item in df_sub['名称'].drop_duplicates().dropna().tolist():
        entity.append(
            {
                'name': item,
                'type': '操作名称',
                'synonym': [],
                'children': [],
            }
        )
    return entity


def hant_2_hans(hant_str: str):
    """ 繁体转简体 """
    cc = opencc.OpenCC('t2s')
    return cc.convert(hant_str)


def synonym_plus(entity):
    """ 同义词扩充 """
    checkpoint_path = r'/workspace/models/chatglm2-6b-int4'
    model, tokenizer = load_model(checkpoint_path, device='cuda')
    for idx, entity_item in enumerate(entity):
        name = entity_item['name']
        prompt = f"帮我生成关于疾病: {name} 的10个同义词, 请直接返回同义词数组，无需多余内容，用','隔开。"
        # TODO: multi-process decided by gpu
        content = infer(model, tokenizer, prompt)
        synonym = re.findall(r'[\u4e00-\u9fa5]+', content)
        synonym = [hant_2_hans(item) for item in list(set(entity[idx]['synonym'] + synonym))]
        entity[idx]['synonym'] = synonym
        logger.info(f"Do synonym_plus by llm... || {idx + 1}/{len(entity)} || {entity[idx]}")
    return entity


def run(excel_file, json_file='entity.json', is_synonym_plus=False):
    entity = []
    df_ill_kind, df_care_method = load_excel(excel_file)
    extract_ill_name(df_ill_kind, entity)
    extract_ill_label(df_ill_kind, entity)
    extract_treat_method(df_ill_kind, entity)
    extract_care_method(df_care_method, entity)
    if is_synonym_plus:
        synonym_plus(entity)
    json.dump(entity, open(json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    logger.info(f"Generate entity to --> {os.path.abspath(json_file)}")
    return entity


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--excel_file', type=str, default='护理AI地图 2.2.xlsx', help='读取的 excel 文件')
    parser.add_argument('-j', '--json_file', type=str, default='entity.json', help='保存的entity的json文件')
    parser.add_argument('-s', '--synonym_plus', default=False, action='store_true', help="同义词补充")
    args = parser.parse_args()
    run(
        args.excel_file,
        json_file=args.json_file,
        is_synonym_plus=args.synonym_plus
    )
