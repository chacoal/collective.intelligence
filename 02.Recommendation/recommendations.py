"""
-*- coding: utf-8 -*-
"""
from math import sqrt

critics={
    'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
        'The Night Listener': 3.0 },
    'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
        'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
        'You, Me and Dupree': 3.5 },
    'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
        'Superman Returns': 3.5, 'The Night Listener': 4.0 },
    'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
        'The Night Listener': 4.5, 'Superman Return': 4.0, 'You, Me and Dupree': 2.5 },
    'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
        'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
        'You, Me and Dupree': 2.0 },
    'Jack Mathews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
        'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5 },
    'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0 }
}

# Euclidean distance.
def sim_distance(prefs, person1, person2):
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    if len(si) == 0: return 0

    sum_of_squares = sum([pow(prefs[person1][item]-prefs[person2][item],2)
                          for item in prefs[person1] if item in prefs[person2]])

    return 1/(1+sum_of_squares)

# Pearson's correlation coefficient
def sim_pearson(prefs, p1, p2):
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1
    n=len(si)
    if n==0: return 0

    # sum of all prefs, p1 n p2
    sum1=sum([prefs[p1][it] for it in si])
    sum2=sum([prefs[p2][it] for it in si])

    # sum of sqrt in si
    sum1Sq=sum([pow(prefs[p1][it] ,2) for it in si])
    sum2Sq=sum([pow(prefs[p2][it] ,2) for it in si])

    # sum of product
    pSum=sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # calculate pearson's
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0: return 0

    r=num/den

    return r

def sim_tanimoto(prefs, person1, person2):
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    if len(si) == 0: return 0

    na=float(len(prefs[person1]))
    nb=float(len(prefs[person2]))
    nc=float(len(si))

    return nc/(na+nb+nc)

def topMatchers(prefs, person, n=5, similarity=sim_pearson):
    scores=[(similarity(prefs, person, other), other)
            for other in prefs if other != person]

    scores.sort()
    scores.reverse()
    return scores[:n]

def getRecommendations(prefs, person, similarity=sim_pearson):
    totals={}
    simSums={}
    for other in prefs:
        if other==person: continue
        sim=similarity(prefs, person, other)

        if sim<=0: continue

        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item]==0:
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim
                simSums.setdefault(item,0)
                simSums[item]+=sim

    rankings=[(total/simSums[item], item) for item, total in totals.items()]

    return sorted(rankings, reverse=True)

def _pair(prefs):
    for person in prefs:
        for item in prefs[person]:
            yield person, item

def transformPrefs(prefs):
    result={}
    for person, item in _pair(prefs):
        result.setdefault(item, {})
        result[item][person]=prefs[person][item]
    return result

def calculateSimilarItems(prefs, n=10):
    result={}
    itemPrefs=transformPrefs(prefs)
    c=0
    for item in itemPrefs:
        c+=1
        if c%100==0: print "%d / %d" % (c, len(itemPrefs))
        scores=topMatchers(itemPrefs, item, n=n, similarity=sim_distance)
        result[item]=scores
    return result

def getRecommendedItems(prefs, itemMatch, user):
    userRatings=prefs[user]
    scores={}
    totalSim={}

    for (item, rating) in userRatings.items():
        for (similarity, item2) in itemMatch[item]:
            if item2 in userRatings: continue
            scores.setdefault(item2, 0)
            scores[item2]+=similarity*rating

            totalSim.setdefault(item2, 0)
            totalSim[item2]+=similarity

    rankings=[(score/totalSim[item], item) for item, score in scores.items()]

    rankings.sort()
    rankings.reverse()

    return rankings

def loadMovieLens(path='./data/movielens'):
    movies={}
    for line in open(path+'/u.item'):
        (id, title) = line.split('|')[0:2]
        movies[id]=title
    prefs={}
    for line in open(path+'/u.data'):
        (user,movieid,rating,ts) = line.split('\t')
        prefs.setdefault(user, {})
        prefs[user][movies[movieid]]=float(rating)

    return prefs

