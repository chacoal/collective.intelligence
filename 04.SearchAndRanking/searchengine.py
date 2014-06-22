# -*- coding:utf-8 -*-
import urllib2
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite


ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])


class crawler:
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    def getentryid(self, table, field, value, createnew=True):
        """
        エントリIDを取得したり、それが存在しない場合には追加
        するための補助機能
        """
        return None

    def addtoindex(self, url, soup):
        """
        個々のページをインデックスする
        """
        print 'Indexing %s' % url

    def gettextonly(self, soup):
        """
        HTMLのページからタグの無い状態でテキストを抽出する
        """
        return None

    def separatewords(self, text):
        """
        空白以外の文字で単語を分割する
        """
        return False

    def isindexed(self, url):
        """
        URL が既にインデックスされていたらTrueを返す
        """
        pass

    def addlinkref(self, urlFrom, urlTo, linkText):
        """
        ２つのページの間にリンクを付け加える
        """
        pass

    def crawl(self, pages, depth=2):
        """
        ページのリストを受け取り、与えられた深川で幅優先探索を行い
        ページをインデクシングする
        """

        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urllib2.urlopen(page)
                except:
                    print 'Could not open %s' % page
                    continue
                soup = BeautifulSoup(c.read())
                self.addtoindex(page, soup)

                links = soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)):
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1: continue
                        url = url.split('#')[0]
                        if url[0:4] == 'http' and not self.isindexed(url):
                            newpages.add(url)
                        linkText = self.gettextonly(link)
                        self.addlinkref(page, url, linkText)
            self.dbcommit()
        pages = newpages

    def crateindextables(self):
        """
        データベースのテーブルを作る
        """
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid, wordid, location)')
        self.con.execute('create table link(fromid integer, toid integer')
        self.con.execute('create table linkwords(wordid, linkid')
        self.con.execute('create table wordidx on wordlist(word)')
        self.con.execute('create table urlidx on urllist(url)')
        self.con.execute('create table wordurlidx on wordlocation(wordid)')
        self.con.execute('create table urltoidx on link(toid)')
        self.con.execute('create table urlfromidx on link(fromid)')
        self.dbcommit()
