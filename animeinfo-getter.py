# -*- coding: utf-8 -*-
import re
import csv
import MeCab

class MC:
    name = 0
    speech = 1
    detail_speech = 2
    speech_type = 3
    name_type = 4
    irr_conjugation = 5
    connection = 6
    origin = 7
    rigid_pronounce = 8
    actual_pronounce = 9



m = MeCab.Tagger(' -d /usr/lib/mecab/dic/mecab-ipadic-neologd')

# 検索単語
text = '''
10日放送の「中居正広のミになる図書館」（テレビ朝日系）で、SMAPの中居正広が、篠原信一の過去の勘違いを明かす一幕があった。
'''

elements = m.parse(text).split('\n')

# 要素数(2個以上だったら排除)
print(len(elements))

element2 = re.split(u'\t|,', elements[0])

f = open('data.csv', 'ab')
csvWriter = csv.writer(f)

# CSVファイルへ書き込み
for num in range(0, 5):
    listData = []
    tmp_ele = re.split(u'\t|,', elements[num])
    # 単語名
    listData.append(tmp_ele[MC.name])
    # メタ情報
    listData.append(tmp_ele[MC.rigid_pronounce])
    csvWriter.writerow(listData)

f.close()
    
