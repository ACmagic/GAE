"""
Use this file to generate input/lol2.pickle
"""
import numpy
import pickle
import time
from data_collect.mypymongo import MyPyMongo


def update_dict(d: dict, key):
    if d.get(key) is None:
        key_id = len(d)
        d[key] = key_id
    return d


def get_data():
    match_id2idx_dict, champion_id2idx_dict = {}, {}
    # M_o records match outcome
    # 1: red team wins, 0: blue team wins
    # M_r_C[z, 0-4] match z, red team, champion idx
    # M_b_C[z, 0-4] match z, blue team, champion idx
    M_o, M_r_C, M_b_C = [], [], []

    for cnt, match in enumerate(mypymongo.db.match.find({}, no_cursor_timeout=True)):
        if cnt % 100 == 0:
            print("process {} match".format(cnt))

        match_id = match['id']
        update_dict(match_id2idx_dict, match_id)

        for team in match['teams']:
            if team['side'] == 'red':
                if team['isWinner']:
                    M_o.append(1)
                else:
                    M_o.append(0)

        red_team_champion_ids, blue_team_champion_ids = [], []

        for participant in match['participants']:
            update_dict(champion_id2idx_dict, participant['championId'])
            if participant['side'] == 'red':
                red_team_champion_ids.append(champion_id2idx_dict[participant['championId']])
            else:
                blue_team_champion_ids.append(champion_id2idx_dict[participant['championId']])

        assert len(red_team_champion_ids) == len(set(red_team_champion_ids))\
            == len(blue_team_champion_ids) == len(set(blue_team_champion_ids)) == 5
        M_r_C.append(red_team_champion_ids)
        M_b_C.append(blue_team_champion_ids)

    Z = len(match_id2idx_dict)
    M = len(champion_id2idx_dict)
    assert cnt == Z - 1

    M_o = numpy.array(M_o)
    M_r_C = numpy.array(M_r_C)
    M_b_C = numpy.array(M_b_C)

    shuffle_idx = numpy.arange(Z)
    numpy.random.shuffle(shuffle_idx)
    M_o = M_o[shuffle_idx]
    M_r_C = M_r_C[shuffle_idx]
    M_b_C = M_b_C[shuffle_idx]

    print('Z: {}, M: {}, pos: {}'.format(Z, M, numpy.sum(M_o)))

    return M_o, M_r_C, M_b_C, match_id2idx_dict, champion_id2idx_dict, Z, M


if __name__ == "__main__":
    start_time = time.time()

    mypymongo = MyPyMongo()

    # NOTE, match_id2idx_dict is not correct after shuffling!!!
    M_o, M_r_C, M_b_C, match_id2idx_dict, champion_id2idx_dict, Z, M = get_data()

    with open("../input/lol2.pickle", "wb") as f:
        pickle.dump((M_o, M_r_C, M_b_C, match_id2idx_dict, champion_id2idx_dict,
                     Z, M), f)

    print("total process time", time.time() - start_time)


