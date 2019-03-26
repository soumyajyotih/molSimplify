import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from keras import backend as K


"""
tools for ML models.
"""


def get_layer_outputs(model, layer_index, input,
                      training_flag=False):
    get_outputs = K.function([model.layers[0].input, K.learning_phase()],
                             [model.layers[layer_index].output])
    nn_outputs = get_outputs([input, training_flag])[0]
    return nn_outputs


def dist_neighbor(fmat1, fmat2, labels, l=5, dist_ref=1):
    dist_mat = pairwise_distances(fmat1, fmat2, 'manhattan')
    dist_mat = dist_mat * 1.0 / dist_ref
    dist_avrg, dist_list, labels_list = [], [], []
    for ele in dist_mat:
        dist_arr = np.round(np.array(ele), 4)
        if not dist_ref == 1:
            _count = (dist_arr < 10).sum()
            _count = l if _count < l else _count
            _count = _count if _count < 300 else 300
        else:
            _count = l
        ind = dist_arr.argsort()[:_count]
        _dist = dist_arr[ind]
        dist_list.append(_dist)
        _labels = np.array([labels[x] for x in ind])
        labels_list.append(_labels)
        if _dist.all() > 1e-4:
            dist_avrg.append(np.mean(_dist[:l]))
        else:
            dist_avrg.append(np.mean(_dist[:l]) * float(l) / (l - 1))
    # print('-----mean: %f, std: %f---' % (np.mean(dist_avrg), np.std(dist_avrg)))
    dist_avrg = np.array(dist_avrg)
    dist_list = np.array(dist_list)
    labels_list = np.array(labels_list)
    return dist_avrg, dist_list, labels_list


def get_entropy(dists, neighbor_targets):
    entropies = []
    _sum = 0
    for ii, _neighbor_targets in enumerate(neighbor_targets):
        p0, p1 = dist_penalty(2), dist_penalty(2)
        for idx, tar in enumerate(_neighbor_targets):
            tar = int(tar)
            d = dists[ii][idx]
            if d <= 10:
                if d != 0:
                    if tar == 0:
                        p0 += dist_penalty(d)
                    elif tar == 1:
                        p1 += dist_penalty(d)
                else:
                    if tar == 0:
                        p0 += 100
                    elif tar == 1:
                        p1 += 100
            _sum = p0 + p1
        p0 = p0 / _sum
        p1 = p1 / _sum
        if p1 == 0 or p0 == 0:
            entropies.append(0)
        else:
            entropies.append(-(p0 * np.log(p0) + p1 * np.log(p1)))
    return np.array(entropies)


def dist_penalty(d):
    return np.exp(-1 * d ** 2)
