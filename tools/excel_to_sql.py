import pandas as pd
from sqlalchemy import create_engine

username = 'ailab'
password = 'TheAIdb0'
host = 'localhost'
database = 'chatcare'

def connect_db():
    connection_str = f"mysql+pymysql://{username}:{password}@{host}/{database}"
    engine = create_engine(connection_str)

    return engine

def delete_db(engine, db_name):
    with engine.connect() as connection:
        connection.execute(f"DELETE FROM {db_name}")

def excel_df(file_path):
    sheet1_df = pd.read_excel(file_path, sheet_name='病种')
    sheet2_df = pd.read_excel(file_path, sheet_name='操作')

    df1 = pd.DataFrame()
    cols = sheet1_df.columns
    df1['disease'] = sheet1_df['疾病名称']
    df1['treatment'] = sheet1_df['治疗方式']
    df1['preface'] = sheet1_df['开场白']
    df1['status'] = sheet1_df['预后情况']
    df1['solutions'] = sheet1_df['护理方案']
    if '饮食' in cols:
        df1['diet'] = sheet1_df['饮食']

    df2 = pd.DataFrame()
    df2['name'] = sheet2_df['名称']
    df2['category'] = sheet2_df['类型']
    df2['text'] = sheet2_df['描述']
    df2['image_link'] = sheet2_df['图片']
    df2['video_link'] = sheet2_df['视频']
    df2['operation_id'] = sheet2_df['序号']

    df1.fillna('None', inplace=True)
    df2.fillna('None', inplace=True)
    df2.loc[df2['category']=='None', 'category'] = -1

    return df1, df2


if __name__ == '__main__':
    import sys
    file_path = sys.argv[1]
    db1_name = 'care_disease'
    db2_name = 'care_operation'
    # file_path = '护理AI地图 2.0.xlsx'

    engine = connect_db()
    delete_db(engine, db1_name)
    delete_db(engine, db2_name)
    df1, df2 = excel_df(file_path)

    df1 = df1.replace([',', '.', '?', '!', ' '], ['，', '。', '？', '！', ''])
    df2 = df2.replace([',', '.', '?', '!', ' '], ['，', '。', '？', '！', ''])

    df1.to_sql(name=db1_name, con=engine, if_exists='append', index=False)
    df2.to_sql(name=db2_name, con=engine, if_exists='append', index=False)

