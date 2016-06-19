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

# 進捗用カウンタ
count = 0
# 暫定検索サイト数(調整したい場合はここ)
sites = 10
# 検索スレッド数(多すぎると帯域を占有してまともにブラウジングできなくなるので注意)
threads_size = 2

class MC:
    # UbuntuにおけるNEologdのインストール先(ディストリビューションごとにここを変更)
    m = MeCab.Tagger(' -d /usr/lib/mecab/dic/mecab-ipadic-neologd')

    # NEologdの実行結果における名前、品詞、品詞の詳細、活用形、名詞の種類、読みがななどの分類
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

    # キャラクター名取得用の正規表現
    pattern1 = re.compile("\<(.*)\><(.*)\>(.*)\((.*)\)\<(.*)\>\<(.*)\>")
    pattern2 = re.compile("(.*)（(.*)）")
    pattern3 = re.compile("\<(.*)\>(.*)\<(.*)\>")
    pattern5 = re.compile("\<(.*)\>(.*)（(.*)）\<(.*)\>")
    pattern6 = re.compile("(.*)（(.*)）/(.*)")
    pattern7 = re.compile("(.*)/(.*)")
    pattern8 = re.compile("(.*)（(.*)）<(.*)\>\<(.*)\>\[(.*)\]\<(.*)\>")

    # HTMLから取得された文字列から作品名を抽出するための正規表現
    title_r1 = re.compile("\<td\>\<b\>\<a href(.*)\>(.*)\</a\>\</b\>\</td\>")
    title_r2 = re.compile("\<li\>\<a href(.*)\>(.*)\</a\>(.*)")
    # HTMLから取得された文字列からキャラクター名を抽出するための正規表現
    character_r = re.compile("\<dt\>(.*)\<(.*)\>")

    # 五十音順作品名用リスト
    hiragana = ["あ行", "か行", "さ行", "た行", "な行", "は行", "ま行", "や行", "ら行",
                "わ・を・ん行", "アルファベット",]

# 名前に正規表現を利用して正確なキャラクター名を返す関数
def namefilter(name):
    # 名前の半角・全角スペースを除去
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
        # 2つの名前が取得された場合長い方を採用
        if len(tmp1) > len(tmp2):
            tmp_name = tmp1
        else:
            tmp_name = tmp2
    elif pattern7:
        tmp1 = pattern7.group(1)
        tmp2 = pattern7.group(2)
        # 2つの名前が取得された場合長い方を採用
        if len(tmp1) > len(tmp2):
            tmp_name = tmp1
        else:
            tmp_name = tmp2
    elif pattern2:
        tmp_name = pattern2.group(1)
            
    return tmp_name

# キャラクターを検索しリストとして返す関数
def charactersearcher(title, page):
    # キャラクター名のリスト
    characters = []
    # 出力リスト
    tmp_pairs = []
    # 改行で区切る
    lines = page.split('\n')
    # 行番号用変数
    line_num = 0  
    
    for line in lines:
        # 現在調べている行に「声 - 」が含まれていればその上の行を出力用リストに加える
        if line.find('声 - ') > -1:
            character_m = MC.character_r.search(lines[line_num-1])
            if character_m:
                tmp_character = character_m.group(1)
                characters.append(tmp_character)
        line_num += 1 

    # 得られたキャラクター名を整形する
    for character in characters:
        tmp_pairs.append((namefilter(character), title))

    return tmp_pairs

# 暫定キャラクター名を取得し、作品名と関連付けを行う関数
def titleconnector(pairs, titles, spt, num):
    # グローバル変数を書き込み可にする
    global count

    # 分散処理用の変数の領域内で回す
    for i in range(spt*num, spt*(1+num)):
        try:
            # 第一回のURL検索
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
                        # 第二階のURL検索
                        characters_url = "https://ja.wikipedia.org/wiki/"+titles[i].replace(' ', '_')+"の登場人物一覧"
                        htmldata = urllib2.urlopen(characters_url)
                        page = htmldata.read()
                        htmldata.close()
                        break
                    except urllib2.URLError, err2:
                        try:
                            # 第三回のURL検索
                            characters_url = "https://ja.wikipedia.org/wiki/"+titles[i].replace(' ', '_')
                            htmldata = urllib2.urlopen(characters_url)
                            page = htmldata.read()
                            htmldata.close()
                            break
                        except urllib2.URLError, err3:
                            # 作品のキャラクターが用意された正規表現で見つからなかったケース
                            exist_flag = False
                            break
                        except SocketError as e:
                            # アクセス制限をかけられたら操作を再度やり直す
                            print(titles[i].replace(' ', '_')+": Connection reset by peer, trying again...")                        
                    except SocketError as e:
                        # アクセス制限をかけられたら操作を再度やり直す
                        print(titles[i].replace(' ', '_')+": Connection reset by peer, trying again...")
                except SocketError as e:
                    # アクセス制限をかけられたら操作を再度やり直す
                    print(titles[i].replace(' ', '_')+": Connection reset by peer, trying again...")
            
            if exist_flag:
                # 登場人物が記載されているURLが存在すればリストに追加
                pairs.extend(charactersearcher(titles[i], page))                
            else:
                print("falured "+titles[i])
                exist_flag = True
            count += 1
            print(str(100.0*count/sites)+"% done!")
        except UnboundLocalError, err:
            # リストか文字列の関係で例外が発生された場合
            count += 1
            print("falured "+titles[i])

# HTMLパーサ
def HTMLparser(pairs):
    # 日本のテレビアニメ作品一覧ページのテンプレート
    template_url = "https://ja.wikipedia.org/wiki/日本のテレビアニメ作品一覧_"
    # 全タイトルのリスト
    titles = []

    # タイトル検索
    for initial in MC.hiragana:
        url = template_url + initial
        page = ""
    
        while True:
            try:
                # ページを開く
                htmldata = urllib2.urlopen(url)
                page = htmldata.read()
                htmldata.close()
                break
            except urllib2.URLError, err:
                print("Connection failed, trying again...")
            except SocketError as e:
                print("Connection reset by peer, trying again...")

        # 得られたHTMLの文字列を改行で区切る
        lines = page.split('\n')
            
        for line in lines:
            title_m = MC.title_r1.search(line)
            if title_m:
                tmp_title = title_m.group(2)
                titles.append(tmp_title)
                print("作品名: "+tmp_title)
            else:
                title_m = MC.title_r2.search(line)
                if title_m:
                    tmp_title = title_m.group(2)
                    titles.append(tmp_title)
                    print("作品名: "+tmp_title)
            
    print("found " + str(len(titles)) + " animations!")

    # 多重起動用スレッドのリスト
    threads = []

    ##### テストモードで起動したいときは以下の変数をコメントアウトしてください #####
    # グローバル変数を書き込み可に
    global sites
    # 調べるアニメの数
    sites = len(titles)
    ##########
    
    # スレッドを起動しキャラクター検索
    for i in range(0, threads_size):
        threads.append(Thread(target=titleconnector, args=(pairs, titles, int(sites/threads_size), i, )))
        threads[i].daemon = True
        threads[i].start()
    for i in range(0, threads_size):
        # 別スレッド終了まで待機
        print("thread "+str(i)+" finished")
        threads[i].join()

# NEologdで単語検索する関数
def NEologdsearch(word):
    # 改行で区切る
    elements = MC.m.parse(word).split('\n')
    for element in elements:
        splitted_element = []
        try:
            # NEologdの実行結果文字列の整形
            splitted_element = re.split(u'\t|,', element)
            if (splitted_element[MC.name] == word) and (splitted_element[MC.speech_type] == "人名"):
                # 入力文字列と出力文字列が一致し、かつ人名であれば真
                return True
        except IndexError, err:
            # 空文字が残った時
            return False

    return False

if __name__ == "__main__":
    # 単語とメタ情報の組の配列
    pairs = []
    # 最終的にペアとなる辞書型配列
    metadict = {}
    # 重複データ用カウンタ
    tmp_written = 0
    # 書き込まれるデータ数
    written = 0
    # NEologdに存在しないデータ数
    non_written = 0

    # HTML解析時間計測開始点
    start = time.time()

    # HTML解析
    HTMLparser(pairs)

    # HTML解析時間計算
    elapsed_time = time.time() - start
    print(("elapsed_time:{0}".format(round(elapsed_time,2))) + "[sec]")

    # 課題用にcsv書き込み機能は停止    
    #f = open('succeeded_data.csv', 'w')
    #nf = open('falured_data.csv', 'w') 
    #csvWriter = csv.writer(f)
    #ncsvWriter = csv.writer(nf)
    
    for pair in pairs:
        # NEologdに単語の存在の問い合わせ
        if NEologdsearch(pair[0]):
            # dictにより重複データは最新のものに上書き
            metadict[pair[0]] = pair[1]
            tmp_written += 1
        else:
            # 存在しなかったデータ書き込み
            nwriteData = []
            # 単語名
            nwriteData.append(pair[0])
            # メタ情報
            nwriteData.append(pair[1])
            #ncsvWriter.writerow(nwriteData)
            non_written += 1

    #nf.close()

    # 課題用フォーマット書き込み
    ftxt = open('result.txt', 'w')   

    # TXTファイルへ書き込み
    for key,value in sorted(metadict.items(), key=lambda x:x[1]):
        writeData = []
        # 単語名
        writeData.append(key)
        # メタ情報
        writeData.append(value)
        #csvWriter.writerow(writeData)
        ftxt.write(writeData[0]+"\t"+writeData[1].replace('　', '_').replace(' ', '_')+"\n")
        written += 1
        
    #f.close()
    ftxt.close()

    print(str(written)+" characters written!")
    print(str(tmp_written-written)+" characters duplicated!")
    print(str(non_written)+" characters not written!")
