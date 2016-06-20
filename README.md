# NEologd-animeinfo
[Wikipedia](https://ja.wikipedia.org/wiki/%E6%97%A5%E6%9C%AC%E3%81%AE%E3%83%86%E3%83%AC%E3%83%93%E3%82%A2%E3%83%8B%E3%83%A1%E4%BD%9C%E5%93%81%E4%B8%80%E8%A6%A7 "日本のテレビアニメ作品一覧 - Wikipedia")からアニメ情報を収集し、NEologdに登録されているキャラクター名にメタ情報として付加するプログラムです。
 
構成
------
### ファイル ###
当リポジトリは以下のファイルから構成されています。
 
+   animeinfo-getter.py :
    Python 2.7 の実行ファイル
 
+   result.txt :
    animeinfo-getter.py の出力結果。NEologd に含まれる単語に関するメタ情報のペアを集めたテキストファイル
 
動作環境
----------------
環境導入に関しては以下を参考にしました。
 
+   https://github.com/neologd/mecab-ipadic-neologd/blob/master/README.ja.md
 
開発・動作環境は以下のようになります。
 
+   Ubuntu 16.04
  +   Python 2.7.11
 
実行方法
----------------
まず NEologd のインストール先を確認してください。実行ファイルの `#21` における下記のパスが含まれているコードと異なっているようであれば変更してください。
 
    m = MeCab.Tagger(' -d /usr/lib/mecab/dic/mecab-ipadic-neologd')
 
以下のコマンドで実行してください。
 
    $ python animeinfo-getter.py
 
また必要に応じて実行ファイル内 `#17` における下記の数値を変更することで実行時間の削減も可能です。
 
    threads_size = 2
 
ただし、スレッド数が多すぎると帯域を占有するだけでなく出力結果に悪影響を及ぼす場合もあります。
 
実行結果
----------------
スレッド数を 2 つにして実行した結果です(取得中の標準出力は省略しています)。
 
    $ python animeinfo-getter.py
    ...
    ...
    ...
    elapsed_time:12836.53[sec]
    11858 characters written!
    2972 characters duplicated!
    36951 characters not written!
 
結果として、11,858 名のキャラクターに対して作品名のメタ情報が付加され、重複として無視されたのが 2,972 名、検出された 36,951 名のキャラクター名が NEologd に登録されていなかった事になります。
 
ただし、正規表現による抽出が完全に対応している訳ではないので絶対であるとは言えません。
 
また、経過時間は約 3 時間半でした。安定した接続を確保するため、スレッド数は 2 つにしています。増やせば速くなりますが獲得できるデータ数に悪影響が及ぶ可能性が高いです。
 
関連情報
--------
### 参考サイト
1. [mecab-ipadic-neologd](https://github.com/neologd/mecab-ipadic-neologd/blob/master/README.ja.md "mecab-ipadic-neologd")
2. [日本のテレビアニメ作品一覧 - Wikipedia](https://ja.wikipedia.org/wiki/%E6%97%A5%E6%9C%AC%E3%81%AE%E3%83%86%E3%83%AC%E3%83%93%E3%82%A2%E3%83%8B%E3%83%A1%E4%BD%9C%E5%93%81%E4%B8%80%E8%A6%A7 "日本のテレビアニメ作品一覧 - Wikipedia")
 
ライセンス
----------
Copyright &copy; 2016 enotesupa All Rights Reserved.
