from BeautifulSoup import BeautifulSoup
import urllib2
import re
chare = re.compile(r'[!-\.&]')
itemowners = {}

# ignore patterns
dropwrds = ['a', 'new', 'some', 'more', 'my', 'own', 'the', 'many', 'other', 'another']

currentuser = 0
for i in range(1, 51):
    c = urllib2.urlopen(
        'http://member.zebo.com/Main?event_key=USERSEARCH&wiowiw=wiw&keyword=car&page=%d' % (i))
    soup = BeautifulSoup(c)
    for td in soup('td'):
        if ('class' in dict(td.attrs) and td['class'] == 'bgverdanasmall'):
            items = [re.sub(chare, '', str(a.countents[0]).lower()).strip() for a in td('a')]
            for item in items:
                # 余計な単語を除去
                txt = ' '.join([t for t in item.split(' ') if not t in dropwrds])
                if len(txt) < 2: continue
                itemowners.setdefault(txt, {})
                itemowners[txt][currentuser] = 1
            currentuser += 1

