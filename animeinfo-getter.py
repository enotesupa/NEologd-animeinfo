# -*- coding: utf-8 -*-
from threading import Thread
import urllib2
import time
import math
import re
import csv
import MeCab

class MC:
    m = MeCab.Tagger(' -d /usr/lib/mecab/dic/mecab-ipadic-neologd')
    
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
    pattern35 = re.compile("(.*)（(.*)） / (.*)（(.*)）")
    pattern4 = re.compile("(.*)")

def namefilter(name):    
    pattern1 = MC.pattern1.search(name)
    pattern2 = MC.pattern2.search(name)
    pattern25 = MC.pattern25.search(name)
    pattern3 = MC.pattern3.search(name)
    pattern35 = MC.pattern35.search(name)
    pattern4 = MC.pattern4.search(name)

    if pattern35:
        tmp1 = pattern35.group(1)
        tmp2 = pattern35.group(3)
        if len(tmp1) > len(tmp2):
            name = tmp1
        else:
            name = tmp2
    elif pattern1:
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

def HTMLparser(pairs, spt, num):
    template_url = "https://www.animecharactersdatabase.com/jp/source.php?id="
    tmp_pairs = []

    for page_id in range(1+spt*num, spt+spt*num+1):
        url = template_url + str(page_id)
        page = ""

        while True:
            try:
                htmldata = urllib2.urlopen(url)
                page = htmldata.read()
                break
            except urllib2.URLError, err:
                print("Connection failed, trying again...")
            except urllib2.HTTPError, err:
                print("Connection failed, trying again...")

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
                print(str(page_id)+" 作品名: "+title)
                break

        for character in characters:
            tmp_pairs.append((namefilter(character), title))
            #print(namefilter(character))   
        
        #print unicode(htmldata.read(),"utf-8")
        htmldata.close()

    pairs.extend(tmp_pairs)

def NEologdsearch(word):
    
    elements = MC.m.parse(word).split('\n')

    for element in elements:
        splitted_element = re.split(u'\t|,', element)
        if (splitted_element[MC.name] == word) and (splitted_element[MC.speech_type] == "人名"):
            return True

    return False
        


if __name__ == "__main__":
    # 単語とメタ情報の組の配列
    pairs = []
    metadict = {}
    tmp_written = 0
    written = 0
    non_written = 0

    threads = []
    # 3スレッド以上だとよくConnection Refuseされる
    threads_size = 2
    # 作品数指定
    sites = 6061
    spt = int(sites/threads_size)

    start = time.time()
    
    for i in range(0, threads_size):
        threads.append(Thread(target=HTMLparser, args=(pairs, spt, i, )))
        threads[i].daemon = True
        threads[i].start()
    for i in range(0, threads_size):
        threads[i].join()

    elapsed_time = time.time() - start
    print(("elapsed_time:{0}".format(round(elapsed_time,2))) + "[sec]")
    
    for pair in pairs:
        if NEologdsearch(pair[0]):
            # dictにすることで重複データは最新のものに上書き
            metadict[pair[0]] = pair[1]
            tmp_written += 1
        else:
            non_written += 1
    
    f = open('data.csv', 'w')
    csvWriter = csv.writer(f)

    # CSVファイルへ書き込み
    for key,value in metadict.items():
        writeData = []
        # 単語名
        writeData.append(key)
        # メタ情報
        writeData.append(value)
        csvWriter.writerow(writeData)
        written += 1
        
    f.close()

    print(str(written)+" characters written!")
    print(str(tmp_written-written)+" characters duplicated!")
    print(str(non_written)+" characters not written!")
