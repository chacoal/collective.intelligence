# -*- coding:utf-8 -*-
import urllib2
import re
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
        cur = self.con.execute(
            "select rowid from %s where %s='%s'" % (table, field, value))
        res = cur.fetchone()
        if res is None:
            cur = self.con.execute(
                "insert into %s (%s) values ('%s')" % (table, field, value))
            return cur.lastrowid
        else:
            return int(res[0])

    def addtoindex(self, url, soup):
        """
        個々のページをインデックスする
        """
        if self.isindexed(url):
            return
        print 'Indexing ' + url

        # 個々の単語を取得する
        text = self.gettextonly(soup)
        words = self.separatewords(text)

        # URL id を取得する
        urlid = self.getentryid('urllist', 'url', url)

        # それぞれの単語と、このurlのリンク
        for i in range(len(words)):
            word = words[i]
            if word in ignorewords:
                continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute("insert into wordlocation(urlid, wordid, location)\
                              values (%d, %d, %d)" % (urlid, wordid, i))

    def gettextonly(self, soup):
        """
        HTMLのページからタグの無い状態でテキストを抽出する
        """
        v = soup.string
        if v is None:
            c = soup.contents
            resulttext = ''
            for t in c:
                subtext = self.gettextonly(t)
                resulttext += subtext + '\n'
            return resulttext
        else:
            return v.strip()

    def separatewords(self, text):
        """
        空白以外の文字で単語を分割する
        """
        splitter = re.compile(r'\W*')
        return [s.lower() for s in splitter.split(text) if s]

    def isindexed(self, url):
        """
        URL が既にインデックスされていたらTrueを返す
        """
        u = self.con.execute(
            "select rowid from urllist where url = '%s'" % url).fetchone()
        if u is not None:
            # URLが実際にクロールされているかどうかチェックする
            v = self.con.execute(
                'select\
                   *\
                 from\
                   wordlocation\
                 where\
                   urlid = %d' % u[0])\
                .fetchone()
            if v is not None:
                return True
        return False

    def addlinkref(self, urlFrom, urlTo, linkText):
        """
        ２つのページの間にリンクを付け加える
        """
        words = self.separatewords(linkText)
        fromid = self.getentryid('urllist', 'url', urlFrom)
        toid = self.getentryid('urllist', 'url', urlTo)
        if fromid == toid:
            return
        print repr(fromid), repr(toid)
        cur = self.con.execute(
            'insert into link(fromid, toid) values (%d, %d)' % (fromid, toid))
        linkid = cur.lastrowid
        print 'words:', words
        for word in words:
            if word in ignorewords:
                continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute(
                'insert into linkwords(linkid, wordid)\
                 values (%d, %d)' % (linkid, wordid))

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
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0]
                        if url[0:4] == 'http' and not self.isindexed(url):
                            newpages.add(url)
                        linkText = self.gettextonly(link)
                        self.addlinkref(page, url, linkText)
            self.dbcommit()
        pages = newpages

    def createindextables(self):
        """
        データベースのテーブルを作る
        """
        self.con.execute('create table if not exists urllist(url)')
        self.con.execute('create table if not exists wordlist(word)')
        self.con.execute('create table if not exists wordlocation(urlid, wordid, location)')
        self.con.execute('create table if not exists link(fromid int, toid int)')
        self.con.execute('create table if not exists linkwords(wordid, linkid)')
        self.con.execute('create index if not exists wordidx on wordlist(word)')
        self.con.execute('create index if not exists urlidx on urllist(url)')
        self.con.execute('create index if not exists wordurlidx on wordlocation(wordid)')
        self.con.execute('create index if not exists urltoidx on link(toid)')
        self.con.execute('create index if not exists urlfromidx on link(fromid)')
        self.dbcommit()

    def drop(self):
        self.con.execute('drop table if exists urllist')
        self.con.execute('drop table if exists wordlist')
        self.con.execute('drop table if exists wordlocation')
        self.con.execute('drop table if exists link')
        self.con.execute('drop table if exists linkwords')
        self.con.execute('drop index if exists wordidx')
        self.con.execute('drop index if exists urlidx')
        self.con.execute('drop index if exists wordurlidx')
        self.con.execute('drop index if exists urltoidx')
        self.con.execute('drop index if exists urlfromidx')
        self.con.execute('vacuum')
        self.dbcommit()
