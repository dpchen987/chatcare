# key: label of classification
# value: intention meta
intentions = {
    0: {
        'intent': '无关',
        'slots': []
    },
    1: {
        'intent': '查询疾病护理方案',
        'slots': ['疾病名称', '治疗方式']
    },
    2: {
        'intent': '查询护理操作',
        'slots': ['操作名称']
    }
}
