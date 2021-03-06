import optparse
import sys
from data_mangle.cv_fold_sparse_reader import CVFoldSparseReader
from data_mangle.cv_fold_lol_sparse_reader import CVFoldLoLSparseReader
from data_mangle.cv_fold_dense_reader import CVFoldDenseReader
from utils import constants


def parse_ml_parameters():
    if len(sys.argv) < 2:
        print('no argument set. use default.')
        return None

    parser = optparse.OptionParser(usage="usage: %prog [options]")
    # FM
    parser.add_option("--fm_order", dest="fm_order", type="int", default=0)
    parser.add_option("--fm_rank", dest="fm_rank", type="int", default=0)
    parser.add_option("--fm_epoch", dest="fm_epoch", type="int", default=0)
    parser.add_option("--fm_reg", dest="fm_reg", type="float", default=0.0)
    parser.add_option("--fm_featconfig", dest="fm_featconfig", type="string", default='')
    # NN
    parser.add_option("--nn_hidden", dest="nn_hidden", type="int", default=0)
    parser.add_option("--nn_featconfig", dest="nn_featconfig", type="string", default='')
    #GBDT
    parser.add_option("--gbdt_featconfig", dest="gbdt_featconfig", type="string", default='')
    parser.add_option("--gbdt_ntree", dest="gbdt_ntree", type="int", default=100)
    parser.add_option("--gbdt_lr", dest="gbdt_lr", type="float", default=0.1)
    parser.add_option("--gbdt_maxdepth", dest="gbdt_maxdepth", type="int", default=3)
    parser.add_option("--gbdt_minsampleleaf", dest="gbdt_minsampleleaf", type="int", default=1)
    # general
    parser.add_option("--density", dest='density', type='string', default='')
    parser.add_option("--dataset", dest='dataset', type='string', default='')
    parser.add_option("--fold", dest='fold', type='int', default=3)
    parser.add_option("--seed", dest='seed', type='int', default=718)
    (kwargs, args) = parser.parse_args()
    return kwargs


def parse_reader(dataset, feature_config, density, fold=10, seed=None):
    if dataset == 'lol':
        if density == 'sparse':
            reader = CVFoldLoLSparseReader(data_path=constants.lol_pickle, folds=fold,
                                           feature_config=feature_config, seed=seed)
        else:
            raise NotImplementedError
    elif dataset == 'lol2':
        if density == 'dense':
            reader = CVFoldDenseReader(data_path=constants.lol2_pickle, folds=fold,
                                       feature_config=feature_config, seed=seed)
    elif dataset == 'dota':
        if density == 'dense':
            reader = CVFoldDenseReader(data_path=constants.dota_pickle, folds=fold,
                                       feature_config=feature_config, seed=seed)
        elif density == 'sparse':
            reader = CVFoldSparseReader(data_path=constants.dota_pickle, folds=fold,
                                        feature_config=feature_config, seed=seed)
        else:
            raise NotImplementedError
    elif dataset == 'dota2':
        if density == 'dense':
            reader = CVFoldDenseReader(data_path=constants.dota2_pickle, folds=fold,
                                       feature_config=feature_config, seed=seed)
        elif density == 'sparse':
            reader = CVFoldSparseReader(data_path=constants.dota2_pickle, folds=fold,
                                        feature_config=feature_config, seed=seed)
        else:
            raise NotImplementedError
    elif dataset == 'dota3':
        if density == 'dense':
            reader = CVFoldDenseReader(data_path=constants.dota3_pickle, folds=fold,
                                       feature_config=feature_config, seed=seed)
        elif density == 'sparse':
            reader = CVFoldSparseReader(data_path=constants.dota3_pickle, folds=fold,
                                        feature_config=feature_config, seed=seed)
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError
    return reader


def parse_mcts_exp_parameters():
    if len(sys.argv) < 2:
        print('no argument set. use default.')
        return None

    parser = optparse.OptionParser(usage="usage: %prog [options]")

    parser.add_option("--num_matches", dest="num_matches", type="int", default=0)
    parser.add_option("--p0", dest="p0", type="string", default='')
    parser.add_option("--p1", dest="p1", type="string", default='')
    parser.add_option("--env_path", dest="env_path", type="string", default='')
    (kwargs, args) = parser.parse_args()
    return kwargs


def parse_mcts_maxiter_c(player_str):
    assert player_str.startswith('mcts')
    _, maxiter, c = player_str.split('_')
    return int(maxiter), float(c)


def parse_rave_maxiter_c_k(player_str):
    assert player_str.startswith('rave')
    _, maxiter, c, k = player_str.split('_')
    return int(maxiter), float(c), float(k)

