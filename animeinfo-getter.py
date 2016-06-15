# -*- coding: utf-8 -*-
import MeCab
m = MeCab.Tagger(' -d /usr/lib/mecab/dic/mecab-ipadic-neologd')

text = '''
10日放送の「中居正広のミになる図書館」（テレビ朝日系）で、SMAPの中居正広が、篠原信一の過去の勘違いを明かす一幕があった。
'''
print(m.parse(text))
