import sys
sys.path.insert(0, '..')

import random
import os
import numpy as np
import time
import pickle
import logging
from player import RandomPlayer, MCTSPlayer, HeroLineUpPlayer, RavePlayer
from utils.parser import parse_mcts_exp_parameters, parse_mcts_maxiter_c, parse_rave_maxiter_c


class Draft:
    """
    class handling state of the draft
    """

    def __init__(self, env_path=None, p0_model_str=None, p1_model_str=None):
        if env_path and p0_model_str and p1_model_str:
            self.outcome_model, self.M = self.load(env_path)
            self.state = [[], []]
            self.avail_moves = set(range(self.M))
            self.move_cnt = [0, 0]
            self.player = None  # current player's turn
            self.next_player = 0  # next player turn
            # player 0 will pick first and be red team; player 1 will pick next and be blue team
            self.player_models = [self.construct_player_model(p0_model_str),
                                  self.construct_player_model(p1_model_str)]

    def get_state(self, player):
        return self.state[player]

    def get_player(self):
        return self.player_models[self.next_player]

    def construct_player_model(self, player_model_str):
        if player_model_str == 'random':
            return RandomPlayer(draft=self)
        elif player_model_str.startswith('mcts'):
            max_iters, c = parse_mcts_maxiter_c(player_model_str)
            return MCTSPlayer(name=player_model_str, draft=self, maxiters=max_iters, c=c)
        elif player_model_str == 'hero_lineup':
            return HeroLineUpPlayer(draft=self)
        elif player_model_str.startswith('rave'):
            max_iters, c = parse_rave_maxiter_c(player_model_str)
            return RavePlayer(name=player_model_str, draft=self, maxiters=max_iters, c=c)
        else:
            raise NotImplementedError

    def load(self, env_path):
        with open('../output/{}'.format(env_path), 'rb') as f:
            # outcome model predicts the red team's  win rate
            # M is the number of champions
            outcome_model, M = pickle.load(f)
        return outcome_model, M

    def eval(self):
        assert self.end()
        x = np.zeros((1, self.M))
        x[0, self.state[0]] = 1
        x[0, self.state[1]] = -1
        red_team_win_rate = self.outcome_model.predict_proba(x)[0, 1]
        return red_team_win_rate

    def copy(self):
        """
        make copy of the board
        """
        copy = Draft()
        copy.outcome_model = self.outcome_model
        copy.M = self.M
        copy.state = [self.state[0][:], self.state[1][:]]
        copy.avail_moves = set(self.avail_moves)
        copy.move_cnt = self.move_cnt[:]
        copy.player = self.player
        copy.next_player = self.next_player
        copy.player_models = self.player_models
        return copy

    def move(self, move):
        """
        take move of form [x,y] and play
        the move for the current player
        """
        # player 0 -> place 1,  player 1 -> place -1
        # val = - self.player * 2 + 1
        self.player = self.next_player
        self.next_player = self.decide_next_player()
        self.state[self.player].append(move)
        self.avail_moves.remove(move)
        self.move_cnt[self.player] += 1
        # logger.info('choose move: player {} ({}), move_cnt: {}, move: {}'.format(self.player, self.get_player().name, self.move_cnt[self.player], move))

    def decide_next_player(self):
        """
        determine next player before a move is taken
        """
        move_cnt = self.move_cnt[0] + self.move_cnt[1]
        if move_cnt in [0, 1, 4, 5, 8]:
            return 1
        else:
            return 0

    def get_moves(self):
        """
        return remaining possible draft moves
        (i.e., where there are no 1's or -1's)
        """
        if self.end():
            return set([])
        return set(self.avail_moves)
        # zero_indices = np.argwhere(self.state == 0).tolist()
        # zero_indices = []
        # for i in range(self.M):
        #     if i not in self.state[0] or i not in self.state[1]:
        #         zero_indices.append(i)
        # logger.info('get moves: player {} ({}), move_cnt: {}, moves: {}'.format(self.player, self.get_player().name, self.move_cnt[self.player], zero_indices))
        # return zero_indices

    def end(self):
        """
        return True if all players finish drafting
        """
        if self.move_cnt[0] == 5 and self.move_cnt[1] == 5:
            return True
        return False

    def print_state(self):
        # logger.info('player 0 ({}), move {}'.format(self.player_models[0].name, self.move_cnt[0]))
        # logger.info(np.argwhere(self.state == 1))
        # logger.info('player 1 ({}), move {}'.format(self.player_models[1].name, self.move_cnt[1]))
        # logger.info(np.argwhere(self.state == -1))
        # logger.info('---------------------------------------')
        pass

    def print_move(self, match_id, move_duration, move_id):
        move_str = 'match {} player {} ({}) move_id {}, move_cnt {}, duration: {:.3f}' \
            .format(match_id, self.player, self.player_models[self.player].name, move_id,
                    self.move_cnt[self.player], move_duration)
        logger.warning(move_str)
        return move_str


def experiment(match_id, p0_model_str, p1_model_str, env_path):
    t1 = time.time()
    d = Draft(env_path, p0_model_str, p1_model_str)  # instantiate board

    while not d.end():
        p = d.get_player()
        t2 = time.time()
        a = p.get_move()
        d.move(a)
        d.print_state()
        d.print_move(match_id=match_id, move_duration=time.time() - t2, move_id=a)

    final_red_team_win_rate = d.eval()
    duration = time.time() - t1
    exp_str = 'match: {}, time: {:.3F}, red team win rate: {:.5f}' \
        .format(match_id, duration, final_red_team_win_rate)

    return final_red_team_win_rate, duration, exp_str


if __name__ == '__main__':
    random.seed(123)
    np.random.seed(123)

    logger = logging.getLogger('mcts')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.WARNING)

    kwargs = parse_mcts_exp_parameters()

    # outcome predictor load path
    env_path = 'NN_hiddenunit120_dota.pickle' if not kwargs else kwargs.env_path

    # possible player string: random, mcts, hero_lineup
    # red team
    p0_model_str = 'mcts_50_1' if not kwargs else kwargs.p0
    # blue team
    p1_model_str = 'rave_50_1' if not kwargs else kwargs.p1
    num_matches = 100 if not kwargs else kwargs.num_matches

    red_team_win_rates, times = [], []
    for i in range(num_matches):
        wr, t, s = experiment(i, p0_model_str, p1_model_str, env_path)
        red_team_win_rates.append(wr)
        times.append(t)
        s += ', mean WR: {:.5f}\n'.format(np.average(red_team_win_rates))
        logger.warning(s)

    # write header
    test_result_path = 'mcts_result.csv'
    if not os.path.exists(test_result_path):
        with open(test_result_path, 'w') as f:
            line = "num_matches, time, player0, player1, red_team_win_rate, std\n"
            f.write(line)
    # write data
    with open(test_result_path, 'a') as f:
        line = "{}, {:.5f}, {}, {}, {:.5f}, {:.5f}\n". \
            format(num_matches, np.average(times), p0_model_str, p1_model_str,
                   np.average(red_team_win_rates), np.std(red_team_win_rates))
        f.write(line)

    logger.warning('{} matches, {} vs. {}. average time {:.5f}, average red team win rate {:.5f}, std {:.5f}'
                   .format(num_matches, p0_model_str, p1_model_str,
                           np.average(times), np.average(red_team_win_rates), np.std(red_team_win_rates)))
