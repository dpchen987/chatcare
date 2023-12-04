from ezmysql import ConnectionSync
from chatcare2.config import params


db = ConnectionSync(
    params.db_host,
    params.db_name,
    params.db_user,
    params.db_pass,
    params.db_port,
)

entity2field = {
    1: {
        '疾病名称': 'disease',
        '治疗方式': 'treatment_display',
    },
    2: {
        '操作名称': 'name',
    }
}

category_order = {
    '观测指标': 1,
    '专科照护': 2,
    '功能训练': 3,
    '饮食营养': 4,
}


def sort_category(c):
    return category_order.get(c[0], 0)


def search_disease(entities):
    where = [f'{entity2field[1][e["type"]]} = "{e["name"]}"' for e in entities]
    where = ' AND '.join(where)
    sql = f'select preface, solutions from care_disease where {where}'
    print(f'{sql = }')
    data = db.get(sql)
    if not data:
        names = '，'.join([e['name'] for e in entities])
        msg = f'对不起，我的知识库里面目前没有【{names}】相关的护理方案'
        return msg, []
    msg = data['preface']
    if not msg:
        disease, treatment = '', ''
        for e in entities:
            if e['type'] == '疾病名称':
                disease = e['name']
                continue
            if e['type'] == '治疗方式':
                treatment = e['name']
        msg = f'{disease}的{treatment}的护理方案如下：'
    sql = f"select name, category, text, image_link, video_link from care_operation where operation_id in ({data['solutions']})"
    print(f'{sql = }')
    data = db.query(sql)
    details = {}
    for d in data:
        if d['image_link'] != 'None':
            d['image_link'] = d['image_link'].split(',')
        else:
            d['image_link'] = []
        if d['video_link'] != 'None':
            d['video_link'] = d['video_link'].split(',')
        else:
            d['video_link'] = []
        # fix link
        for i, lk in enumerate(d['image_link']):
            if not lk.startswith('http'):
                d['image_link'][i] = '/static/' + lk
        for i, lk in enumerate(d['video_link']):
            if not lk.startswith('http'):
                d['video_link'][i] = '/static/' + lk
        print(d)
        category = d.pop('category')
        if category in details:
            details[category].append(d)
        else:
            details[category] = [d]
    zz = sorted(details.items(), key=sort_category)
    return msg, zz


def search_operation(entities):
    sql = f'select name, text, image_link, video_link from care_operation where name="{entities[0]["name"]}"'
    d = db.get(sql)
    if d['image_link'] != 'None':
        d['image_link'] = d['image_link'].split(',')
    else:
        d['image_link'] = []
    if d['video_link'] != 'None':
        d['video_link'] = d['video_link'].split(',')
    else:
        d['video_link'] = []
    data = [(d['name'], [d])]
    msg = f"{entities[0]['name']} 的操作方法：\n{d['text']}"
    return msg, data


def search_mysql(intent_id, entities):
    if intent_id == '1':
        return search_disease(entities)
    if intent_id == '2':
        return search_operation(entities)


def update_link():
    sql = 'select id, image_link, video_link from care_operation'
    data = db.query(sql)
    for d in data:
        if d['image_link'].strip() != 'None':
            url = 'https://chatcare.oss-cn-shanghai.aliyuncs.com/img/' + d['image_link'].split('/')[-1]
            sql = f'update care_operation set image_link="{url}" where id={d["id"]}'
            print(sql)
            db.execute(sql)
        if d['video_link'].strip() != 'None':
            url = 'https://chatcare.oss-cn-shanghai.aliyuncs.com/video/' + d['video_link'].split('/')[-1]
            sql = f'update care_operation set video_link="{url}" where id={d["id"]}'
            print(sql)
            db.execute(sql)
    print('done')


if __name__ == '__main__':
    update_link()

