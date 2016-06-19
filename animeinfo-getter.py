# -*- coding: utf-8 -*-
from threading import Thread
from socket import error as SocketError
import errno
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

    pattern1 = re.compile("\<(.*)\><(.*)\>(.*)\((.*)\)\<(.*)\>\<(.*)\>")
    pattern2 = re.compile("(.*)（(.*)）")
    pattern3 = re.compile("\<(.*)\>(.*)\<(.*)\>")
    pattern5 = re.compile("\<(.*)\>(.*)（(.*)）\<(.*)\>")
    pattern6 = re.compile("(.*)（(.*)）/(.*)")
    pattern7 = re.compile("(.*)/(.*)")
    pattern8 = re.compile("(.*)（(.*)）<(.*)\>\<(.*)\>\[(.*)\]\<(.*)\>")
    
    title_r1 = re.compile("\<td\>\<b\>\<a href(.*)\>(.*)\</a\>\</b\>\</td\>")
    title_r2 = re.compile("\<li\>\<a href(.*)\>(.*)\</a\>(.*)")
    character_r = re.compile("\<dt\>(.*)\<(.*)\>")

    hiragana = ["あ行", "か行", "さ行", "た行", "な行", "は行", "ま行", "や行", "ら行",
                "わ・を・ん行", "アルファベット",]

def namefilter(name):
    tmp_name = name.replace(' ', '').replace('　', '')
    
    pattern1 = MC.pattern1.search(tmp_name)
    pattern2 = MC.pattern2.search(tmp_name)
    pattern3 = MC.pattern3.search(tmp_name)
    pattern5 = MC.pattern5.search(tmp_name)
    pattern6 = MC.pattern6.search(tmp_name)
    pattern7 = MC.pattern7.search(tmp_name)
    pattern8 = MC.pattern8.search(tmp_name)

    if pattern1:
        tmp_name = pattern1.group(3)
    elif pattern8:
        tmp_name = pattern8.group(1)
    elif pattern5:
        tmp_name = pattern5.group(2)
    elif pattern3:
        tmp_name = pattern3.group(2)
    elif pattern6:
        tmp1 = pattern6.group(1)
        tmp2 = pattern6.group(3)
        if len(tmp1) > len(tmp2):
            tmp_name = tmp1
        else:
            tmp_name = tmp2
    elif pattern7:
        tmp1 = pattern7.group(1)
        tmp2 = pattern7.group(2)
        if len(tmp1) > len(tmp2):
            tmp_name = tmp1
        else:
            tmp_name = tmp2
    elif pattern2:
        tmp_name = pattern2.group(1)
            
    return tmp_name

def charactersearcher(title, page):
    characters = []
    tmp_pairs = []
    lines = page.split('\n')    
    line_num = 0  
    
    for line in lines:
        if line.find('声 - ') > -1:
            character_m = MC.character_r.search(lines[line_num-1])
            if character_m:
                tmp_character = character_m.group(1)
                characters.append(tmp_character)
        line_num += 1 
                
    for character in characters:
        tmp_pairs.append((namefilter(character), title))

    return tmp_pairs

count = 0
sites = 10
threads_size = 3

def titleconnector(pairs, titles, spt, num):
    global count
    
    for i in range(spt*num, spt*(1+num)):
        try:
            characters_url = "https://ja.wikipedia.org/wiki/"+titles[i].replace(' ', '_')+"の登場人物"
            exist_flag = True
            print(str(i)+" "+titles[i])
        
            while True:
                try:
                    htmldata = urllib2.urlopen(characters_url)
                    page = htmldata.read()
                    htmldata.close()
                    break
                except urllib2.URLError, err1:
                    try:
                        characters_url = "https://ja.wikipedia.org/wiki/"+titles[i].replace(' ', '_')+"の登場人物一覧"
                        htmldata = urllib2.urlopen(characters_url)
                        page = htmldata.read()
                        htmldata.close()
                        break
                    except urllib2.URLError, err2:
                        try:
                            characters_url = "https://ja.wikipedia.org/wiki/"+titles[i].replace(' ', '_')
                            htmldata = urllib2.urlopen(characters_url)
                            page = htmldata.read()
                            htmldata.close()
                            break
                        except urllib2.URLError, err3:
                            exist_flag = False
                            break
                        except SocketError as e:
                            print("Connection reset by peer, trying again...")                        
                    except SocketError as e:
                        print("Connection reset by peer, trying again...")
                except SocketError as e:
                    print("Connection reset by peer, trying again...")
            
            if exist_flag:
                pairs.extend(charactersearcher(titles[i], page))                
            else:
                print("falured "+titles[i])
                exist_flag = True
            count += 1
            print(str(100.0*count/sites)+"% done!")
        except UnboundLocalError, err:
            count += 1
            print("falured "+titles[i])
       
def HTMLparser(pairs):
    template_url = "https://ja.wikipedia.org/wiki/日本のテレビアニメ作品一覧_"
    line_num = 0
    titles = []

    # タイトル検索
    for initial in MC.hiragana:
        url = template_url + initial
        page = ""
    
        while True:
            try:
                htmldata = urllib2.urlopen(url)
                page = htmldata.read()
                htmldata.close()
                break
            except urllib2.URLError, err:
                print("Connection failed, trying again...")
            except SocketError as e:
                print("Connection reset by peer, trying again...")
            
        lines = page.split('\n')
            
        for line in lines:
            title_m = MC.title_r1.search(line)
            if title_m:
                tmp_title = title_m.group(2)
                titles.append(tmp_title)
                print("作品名: "+tmp_title)
                line_num += 1
            else:
                title_m = MC.title_r2.search(line)
                if title_m:
                    tmp_title = title_m.group(2)
                    titles.append(tmp_title)
                    print("作品名: "+tmp_title)
                    line_num += 1
            
    print("found " + str(line_num) + " animations!")

    threads = []
    global sites
    sites = line_num
    spt = int(sites/threads_size)
    
    # キャラクター検索
    for i in range(0, threads_size):
        threads.append(Thread(target=titleconnector, args=(pairs, titles, spt, i, )))
        threads[i].daemon = True
        threads[i].start()
    for i in range(0, threads_size):
        threads[i].join()
   

def NEologdsearch(word):    
    elements = MC.m.parse(word).split('\n')
    for element in elements:
        splitted_element = []
        try:
            splitted_element = re.split(u'\t|,', element)
            if (splitted_element[MC.name] == word) and (splitted_element[MC.speech_type] == "人名"):
                return True
        except IndexError, err:
            return False

    return False
        


if __name__ == "__main__":
    # 単語とメタ情報の組の配列
    pairs = []
    metadict = {}
    tmp_written = 0
    written = 0
    non_written = 0

    start = time.time()

    HTMLparser(pairs)

    elapsed_time = time.time() - start
    print(("elapsed_time:{0}".format(round(elapsed_time,2))) + "[sec]")

    nf = open('falured_data.csv', 'w')
    ncsvWriter = csv.writer(nf)
    
    for pair in pairs:
        if NEologdsearch(pair[0]):
            # dictにすることで重複データは最新のものに上書き
            metadict[pair[0]] = pair[1]
            tmp_written += 1
        else:
            nwriteData = []
            # 単語名
            nwriteData.append(pair[0])
            # メタ情報
            nwriteData.append(pair[1])
            # 課題用にcsv書き込み機能は停止
            #ncsvWriter.writerow(nwriteData)
            non_written += 1

    nf.close()

    ftxt = open('result.txt', 'w')        
    f = open('succeeded_data.csv', 'w')
    csvWriter = csv.writer(f)

    # CSVとTXTファイルへ書き込み
    for key,value in sorted(metadict.items(), key=lambda x:x[1]):
        writeData = []
        # 単語名
        writeData.append(key)
        # メタ情報
        writeData.append(value)
        # 課題用にcsv書き込み機能は停止
        #csvWriter.writerow(writeData)
        ftxt.write(writeData[0]+"\t"+writeData[1].replace('　', '_').replace(' ', '_')+"\n")
        written += 1
        
    f.close()
    ftxt.close()

    print(str(written)+" characters written!")
    print(str(tmp_written-written)+" characters duplicated!")
    print(str(non_written)+" characters not written!")
