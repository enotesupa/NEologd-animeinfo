# -*- coding: utf-8 -*-
import urllib2
import time
import math
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

    pattern1 = re.compile("(.*)/(.*)（(.*)）")
    pattern2 = re.compile("(.*)（(.*)）")
    pattern25 = re.compile("(.*)\((.*)\)")
    pattern3 = re.compile("(.*)/(.*)")    
    pattern4 = re.compile("(.*)")

def namefilter(name):    
    pattern1 = MC.pattern1.search(name)
    pattern2 = MC.pattern2.search(name)
    pattern25 = MC.pattern25.search(name)
    pattern3 = MC.pattern3.search(name)
    pattern4 = MC.pattern4.search(name)

    if pattern1:
        tmp1 = pattern1.group(1)
        tmp2 = pattern1.group(2)
        if len(tmp1) > len(tmp2):
            name = tmp1
        else:
            name = tmp2
    elif pattern2:
        name = pattern2.group(1)
    elif pattern25:
        name = pattern25.group(1)
    elif pattern3:
        tmp1 = pattern3.group(1)
        tmp2 = pattern3.group(2)
        if len(tmp1) > len(tmp2):
            name = tmp1
        else:
            name = tmp2
    elif pattern4:
        name = pattern4.group(1)

    return name.replace(' ', '').replace('　', '')


def HTMLparser():
    template_url = "https://www.animecharactersdatabase.com/jp/source.php?id="

    start = time.time()

    for page_id in range(1,10):
        url = template_url + str(page_id)
        htmldata = urllib2.urlopen(url)
        page = htmldata.read()

        # キャラクター検索
        characters = []
        character_recog = re.compile("(.*)\<div class=tile1top\>\<(.*)\>(.*)\<(.*)\>\<(.*)\>")

        lines = page.split('\n')
        
        for line in lines:
            tmp_recog = character_recog.search(line)
            if tmp_recog:
                characters.append(tmp_recog.group(3))


        # タイトル検索
        line_num = 0
        title = ""

        for line in lines:
            line_num += 1
            if line.find('日本語タイトル') > -1:
                title_r = re.compile("(.*)\<(.*)\>\<(.*)\>(.*)\<(.*)\>\<(.*)\>")
                title_m = title_r.search(lines[line_num])
                title = title_m.group(4)
                print("作品名: "+title)
                break

        for character in characters:
            print(namefilter(character))   
        
        #print unicode(htmldata.read(),"utf-8")
        htmldata.close()
    
    elapsed_time = time.time() - start
    print(("elapsed_time:{0}".format(round(elapsed_time,2))) + "[sec]")


if __name__ == "__main__":
    
    # NEologdインストール先指定
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

    
    HTMLparser()
