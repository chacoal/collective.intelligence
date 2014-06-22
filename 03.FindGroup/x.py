# coding: shift_jis
import feedparser

def dict_print(s, h):
    for k, v in h.items():
        print s, k
        if not v: print 'null'
        if isinstance(v, dict):
            dict_print(s + s, v)
        elif isinstance(v, list):
            list_print(s + s, v)
        else:
            print v.decode('utf-8')
            print s + s, str(v)


def list_print(s, l):
    for v in l:
        if not v: print 'null'
        if isinstance(v, dict):
            dict_print(s + s, v)
        elif isinstance(v, list):
            list_print(s + s, v)
        else:
            print s + s, str(v)

for k, v in feedparser.parse('http://feeds.rebuild.fm/rebuildfm').items():
    print k
    if isinstance(v, dict):
        dict_print(' ', v)
    elif isinstance(v, list):
        list_print(' ', v)
    else:
        print ' ', v
