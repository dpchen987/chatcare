import pandas as pd
from itertools import product
import random


def read_in_true(file_name):
    df = pd.read_excel(file_name)
    df = df[~(df['病种'].isna()) & ~(df['照护内容'].isna())]

    return df


def fillin_template(disease):
    questions = ['如何', '怎样', '怎么']
    cares = ['照护', '照顾']
    points = ['要点', '内容', '步骤', '具体步骤']

    tem1 = [f'{disease}应该{i[0]}{i[1]}' for i in list(product(questions, cares))]
    tem2 = [f'{i[0]}{i[1]}{disease}病人' for i in list(product(questions, cares))]
    tem3 = [f'{i[0]}{disease}病人有哪些{i[1]}' for i in list(product(cares, points))]
    tem4 = [f'{i[0]}{disease}病人的{i[1]}有哪些' for i in list(product(cares, points))]
    tem5 = [f'{i}病人都需要注意什么' for i in cares]
    temp6 = [disease]

    return tem1 + tem2 + tem3 + tem4 + tem5 + temp6


# 生成正样本
def generate_true(file_name):
    df = read_in_true(file_name)
    true_li = []
    for i in range(len(df)):
        disease = df.iloc[i, 2]
        #     procedure = df.iloc[i,6]
        true_li += fillin_template(disease)

    return true_li


# 从txt文件中取出新闻题目作为负样本
def generate_false(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        data = file.read().split('\n')
    false_li = [i for i in data if len(i)>8 and '#' not in i]

    return false_li


def generate_train(fn_t, fn_f, train_fn):
    true_li = generate_true(fn_t)
    false_li = generate_false(fn_f)
    res_li = [f'1 {i}' for i in true_li] + [f'0 {i}' for i in false_li]
    random.shuffle(res_li)

    with open(train_fn, 'w', encoding='utf-8') as file:
        # Write each combination as a line in the file
        for i in res_li:
            file.write(f'{i}\n')

    return 0


if __name__ == '__main__':
    from sys import argv
    # python generate_classification_train.py file_name_true.xlsx file_name_false.txt output_file
    fn_t, fn_f, train_fn = argv[1], argv[2], argv[3]
    generate_train(fn_t, fn_f, train_fn)

