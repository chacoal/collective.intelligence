# coding:utf-8

from math import sqrt
from PIL import (
    Image,
    ImageDraw,
)
import random


def readfile(filename):
    lines=[line for line in file(filename)]

    colnames=lines[0].strip().split('\t')[1:]
    rownames=[]
    data=[]
    for line in lines[1:]:
        p=line.strip().split('\t')
        rownames.append(p[0])
        data.append([float(x) for x in p[1:]])
    return rownames,colnames,data


def pearson(v1, v2):
    sum1 = sum(v1)
    sum2 = sum(v2)

    sum1Sq = sum([pow(v, 2) for v in v1])
    sum2Sq = sum([pow(v, 2) for v in v2])

    pSum = sum([_v1 * _v2 for _v1, _v2 in zip(v1, v2)])

    num = pSum - (sum1 * sum2 / len(v1))
    den = sqrt((sum1Sq - pow(sum1, 2) / len(v1)) * (sum2Sq - pow(sum2, 2) / len(v1)))
    if den == 0:
        return 0

    return 1.0 - num / den


class bicluster:
    def __init__(self, vec, left=None, right=None, distance=0, id=None):
        self.vec = vec
        self.left = left
        self.right = right
        self.distance = distance
        self.id = id

    def __cmp__(self, o):
        if not isinstance(o, bicluster):
            return False
        if self.id == o.id:
            return True
        return False

def index(l):
    for i in range(len(l)):
        for j in range(i+1, len(l)):
            yield i, j

def hcluster(rows, distance=pearson):
    distances = {}
    currentclustid = -1

    clust = [bicluster(rows[i], id=1) for i in range(len(rows))]

    while len(clust) > 1:
        lowestpair = (0, 1)
        closest = distance(clust[0].vec, clust[1].vec)
        for i, j in index(clust):
            if (clust[i].id, clust[j].id) not in distances:
                distances[clust[i].id, clust[j].id] = distance(clust[i].vec, clust[j].vec)

            d = distances[(clust[i].id, clust[j].id)]

            if d < closest:
                closest = d
                lowestpair = (i, j)

        mergevec = [
                (clust[lowestpair[0]].vec[i] + clust[lowestpair[1]].vec[i]) / 2.0
                for i in range(len(clust[0].vec))]

        newcluster = bicluster(mergevec, left=clust[lowestpair[0]], right=clust[lowestpair[1]],
                               distance=closest, id=currentclustid)

        currentclustid -= 1
        del clust[lowestpair[0]]
        del clust[lowestpair[1]]

        clust.append(newcluster)

    return clust[0]

def getheight(clust):
    if clust.left == None and clust.right == None: return 1
    return getheight(clust.left), getheight(clust.right)


def getdepth(clust):
    if clust.left == None and clust.right == None: return 0
    return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance


def drawdendrogram(clust, labels, jpeg='clusters.jpg'):
    h = getheight(clust) * 20
    w = 1200
    depth = getdepth(clust)

    scaling = float(w - 150) / depth

    img = Image.new('RGB', (w, h), (255, 255, 255))

    draw = ImageDraw.Draw(img)

    draw.line((0, h/2, 10, h/2), fill=(255, 0, 0))

    drawnode(draw, clust, 10, (h/2), scaling, labels)
    img.save(jpeg, 'JPEG')


def drawnode(draw, clust, x, y, scaling, labels):
    if clust.id < 0:
        h1 = getheight(clust.left) * 20
        h2 = getheight(clust.right) * 20
        top = y - (h1 + h2) / 2
        bottom = y + (h1 + h2) / 2

        ll = clust.distance * scaling

        draw.line((x, top + h1 / 2, x, bottom - h2 / 2), fill = (255, 0, 0))
        draw.line((x, top + h1 / 2, x + ll, top + h1 / 2), fill = (255, 0, 0))
        draw.line((x, bottom + h2 / 2, x + ll, bottom + h1 / 2), fill = (255, 0, 0))

        drawnode(draw, clust.left, x+ll, top+h1/2, scaling, labels)
        drawnode(draw, clust.right, x+ll, bottom-h2/2, scaling, labels)
    else:
        draw.text((x+5, y-7), labels[clust.id], (0,0,0))


def rotatematrix(data):
    newdata = []
    for i in range(len(data[0])):
        newrow = [data[j][i] for j in range(len(data))]
        newdata.append(newrow)
    return newdata


def kcluster(rows, distance=pearson, k=4):
    # それぞれのポイントの最小値と最大値を決める
    ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows])) for i in range(len(rows[0]))]
    # 重心をランダムにk個配置する
    clusters = [[randam.randam() * (ranges[i][1] - ranges[i][0]) + ranges[i][0]
                for i in range(len(rows[0]))] for j in range(k)]

    lastmatches = None

    for t in range(100):
        print 'Iteration %d' % t
        bestmatches = [[] for i in range(k)]

        # それぞれの行に対して、最も近い重心を探し出す
        for j in range(len(rows)):
            row = rows[j]
            bestmatch = 0
            for i in range(k):
                d = distance(clusters[i], row)
                if d < distance(clusters[bestmatch], row):
                    bestmatch = i
            bestmatches[bestmatch].append(j)

        # 結果が前回と同じであれば完了
        if bestmatches == lastmatches:
            break
        lastmatches = bestmatches

        # 重心をそのメンバーの平均に移動する
        for i in range(k):
            avgs = [0.0] * len(rows[0])
            if len(bestmatches[i]) > 0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m] += rows[rowid][m]

                for j in range(len(avgs)):
                    avgs[j] /= len(bestmatches[i])
            clusters[i] = avgs
    return bestmatches


def tanimoto(v1, v2):
    c1, c2, shr = 0, 0, 0
    for i in range(len(v1)):
        if v1[i] != 0: c1 += 1
        if v2[i] != 0: c2 += 1
        if v1[i] != 0 and v2[i] != 0: chr +=1
    return 1.0 - (float(shr) / (c1 + c2 - shr))


def scaledown(data, distance=pearson, rate=0.01):
    n = len(data)
    # アイテムのすべての組の実際の距離
    realdist = [[distance(data[i], data[j]) for j in range(n)] for i in range(n)]
    outersum = 0.0
    # 2次元上にランダムに配置するように初期化する
    loc = [[random.random(), random.random()] for i in range(n)]
    fakedist = [[0.0 for j in range(n)] for i in range(n)]

    lasterror = None
    for m in range(0, 1000):
        for i in range(n):
            for j in range(n):
                if j == k: continue
                errorterm = (fakedist[j][k] - realdist[j][k]) / realdist[j][k]

                # 他のポイントへの誤差に比例してそれぞれのポイントを
                # 近づけたりドオ酒たりする必要がある
                grad[k][0] += ((loc[k][0] - loc[j][0]) / fakedist[j][k]) * errorterm
                grad[k][1] += ((loc[k][1] - loc[j][1]) / fakedist[j][k]) * errorterm

                # 誤差の合計を記録
                totalerror += abs(errorterm)
        print totalerror

        # ポイントを移動することで誤差が悪化したら終了
        if lasterror and lasterror < totalerror: break
        lasterror = totalerror

        # 学習率時計者を掛け合わせてそれぞれのポイントを移動
        for k in range(n):
            loc[k][0] -= rate * grad[k][0]
            loc[k][1] -= rate * grad[k][1]

    return loc


def draw2d(data, labels, jpeg='mds2d.jpg'):
    img = Image.new('RGB', (2000, 2000), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i in range(len(data)):
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        draw.text((x, y), labels[i], (0, 0, 0))
    img.save(jpeg, 'JPEG')
