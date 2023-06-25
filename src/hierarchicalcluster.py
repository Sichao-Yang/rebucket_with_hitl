
import numpy as np
import json
import copy


def get_data(path):
    with open(path, 'r') as fp:
        data = json.load(fp)
    xs = []
    ys = []
    for k,v in data.items():
        v = list(v)
        v = [x.split(' ') for x in v]
        xs.extend(v)
        ys.extend(len(v)*[int(k)])
    return xs, ys

def prep_data(xs, remove_ids=[], max_K=10000):
    rev_xs = copy.deepcopy(xs)
    # reverse order
    rev_xs = [x[::-1] for x in rev_xs]
    # filter events
    if len(remove_ids) != 0:
        for i, x in enumerate(rev_xs):
            rev_xs[i] = [id for id in x if id not in remove_ids]
    # truncate sequence
    rev_xs = [x[:max_K] for x in rev_xs]
    return rev_xs

def get_cluster(ys):
    ys = np.array(ys)
    clusters_true = []
    for l in list(set(ys)):
        clusters_true.append(np.where(ys==l)[0].tolist())   
    return clusters_true

class SimRebucket:
    def __init__(self, c, o) -> None:
        self.c = c
        self.o = o
        
    def cost(self, i, j, u, v):
        if u[i] == v[j]:
            return np.exp(-1*self.c*min(i,j)) * np.exp(-1*self.o*abs(i-j))
        else:
            return 0

    def __call__(self, u, v):
        m, n = len(u), len(v)
        min_l = min(m, n)
        denum = np.sum(np.exp(np.arange(min_l)*self.c*-1))

        # the matrix size is 1 bigger than [dim_u, dim_v], because it start from [1,1] and ends at [1+dim_u, 1+dim_v]
        M = np.zeros((m+1, n+1))
        for i in range(1, m+1):
            for j in range(1, n+1):
                M[i,j] = max(
                    M[i-1, j-1] + self.cost(i-1, j-1, u, v),
                    M[i-1, j],
                    M[i, j-1]
                )
        return M[m, n] / denum


class HierCluster:
    def __init__(self, distance_threshold, c, o) -> None:
        self.distance_threshold = distance_threshold
        self.sim_fcn = SimRebucket(c, o)
        
    def get_M_dis(self, rev_xs):
        M_dis = np.zeros((len(rev_xs), len(rev_xs)))
        # only a upper triangle matrix is enough
        for i in range(len(rev_xs)):
            for j in range(i+1, len(rev_xs)):
                M_dis[i,j] = 1 - self.sim_fcn(rev_xs[i], rev_xs[j])
        return M_dis

    def get_distance_btw_clusters(self, u, v, M_dis):
        """find the max dist. btw. two clusters"""
        max_dis = 0
        for i in u:
            for j in v:
                if M_dis[i, j] > max_dis:
                    max_dis = M_dis[i, j]
        return max_dis

    def run(self, rev_xs):

        M_dis = self.get_M_dis(rev_xs)
        # cluster start condition: every single sample is a cluster
        clusters = [*range(len(rev_xs))]
        clusters = [[c] for c in clusters]

        while True:
            # find the minimum pair in current iteration
            min_dis = 1e6
            for i in range(len(clusters)):
                for j in range(i+1, len(clusters)):
                    assert i < j, "i<j condition violated! M_dis matrix is only a upper triangle"
                    dis = self.get_distance_btw_clusters(clusters[i], clusters[j], M_dis)
                    if dis <= min_dis:
                        min_pair = (i, j)
                        min_dis = dis
            # check stop criteria
            if min_dis <= self.distance_threshold:
                # update cluster
                i, j = min_pair
                clusters[i]+=clusters[j]
                clusters.pop(j)
                # print(clusters)
            else:
                break
        return clusters


def score_f1(y_true, y_pred):
    def _score_f1(yt, yp):
        # f1 score for a pair of sequences
        yt, yp = set(yt), set(yp)
        p = len(yt.intersection(yp)) / len(yp)
        r = len(yt.intersection(yp)) / len(yt)
        if (p+r) == 0:
            return 0
        return 2*p*r / (p+r)
    
    N = len([y for cluster in y_true for y in cluster])
    score = 0
    # find the max f1 score for each true cluster, then sum them weighed by size of cluster
    for yt in y_true:
        tmp = []
        for yp in y_pred:
            tmp.append(_score_f1(yt, yp))
        score += len(yt)/N*max(tmp)
    return score

# hyper-param optimization algo. in paper, grid search
def hyper_opt(rev_xs, clusters_true):
    cs = np.arange(0,1,0.1)
    os = np.arange(0,1,0.1)
    ds = np.arange(0,0.8,0.1)
    max_score = 0
    for c in cs:
        for o in os:
            for d in ds:
                hc = HierCluster(distance_threshold=d, c=c, o=o)
                clusters_pred = hc.run(rev_xs)
                score = score_f1(clusters_true, clusters_pred)
                if score >= max_score:
                    max_score = score
                    best_param = {'c': c, 'o': o, 'd': d}
                    best_pred = clusters_pred
                    
    # print(best_param)
    # print(best_pred)
    return best_param, best_pred





