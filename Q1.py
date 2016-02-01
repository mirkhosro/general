import numpy as np
import sys
import functools


class Q1Solver:
    """This class solves Q1 and returns the results. Writing a class for this purpose
    may not be the most efficient way of doing things but I just wanted to show off that
    I know OOP ;)"""
    def __init__(self, stop_num, A=1):
        self.CARDS = [A, 2, 4, 8, 16, 32, 64]  # All of our cards
        self.SEEN_CARDS = self.CARDS[:]  # Those cards that are seen at least once
        self.MAX_CARD = np.max(self.SEEN_CARDS)
        self.ODDS = np.float64(1 / len(self.CARDS))
        self.prob = None
        self._stop_num = stop_num

    def _calc_iter(self):
        """This is a naive iterative solver. The only good thing about it is that it
         doesn't face recursion limit but is too slow for N > 25."""
        cur_list = [0] # list of number to go over and compute the new probs
        p = 1 # prob to be added at each step
        while len(cur_list) > 0:
            next_list = []
            p *= self.ODDS
            for sum in cur_list:
                for card in self.SEEN_CARDS:
                    if sum + card >= self._stop_num:
                        self.prob[sum + card - self._stop_num] += p
                    else:
                        next_list.append(sum + card)
            cur_list = next_list

    def _calc_recur_naive(self, sum, p):
        """This is the a naive recursive solver but probably the most obvious one.
        It becomes too slow for N > 25 but cannot be memoized because it doesn't
        return anything."""
        if sum >= self._stop_num:
            self.prob[sum - self._stop_num] += p
            return
        else:
            for n in self.SEEN_CARDS:
                self._calc_recur_naive(sum + n, p * self.ODDS)

    @functools.lru_cache(maxsize=None)
    def _calc_recur(self, sum):
        """This is a more sophisticated recursive solver. Returns probability vectors
         so can be memoized and is almost instant even for N=1000. Only you have to increase
         recursion limit for it to work for larger N"""
        prob = np.zeros(self.MAX_CARD, dtype=np.float64)
        if sum >= self._stop_num:
            prob[sum - self._stop_num] = 1
        else:
            for n in self.SEEN_CARDS:
                prob += self.ODDS * self._calc_recur(sum + n)
        return prob

    def calculate(self, exclude=None, recursive=True):
        self.prob = np.zeros(self.MAX_CARD, dtype=np.float64)
        self.SEEN_CARDS = self.CARDS[:]
        if exclude:
            for x in exclude:
                self.SEEN_CARDS.remove(x)

        if recursive:
            #one = np.float64(1)
            #self._solve_recur_naive(0, one)
            self._calc_recur.cache_clear()
            self.prob = self._calc_recur(0)
        else:
            self._calc_iter()

    def mean_sd(self):
        """Returns mean and sd based on calculated probabilities."""
        if self.prob is not None:
            scores = np.arange(self.MAX_CARD)  # possible score values are 0,1,...,63
            score_mean = np.average(scores, weights=self.prob)
            score_sd = np.sqrt(np.average((scores - score_mean) ** 2, weights=self.prob))
            return score_mean, score_sd


sys.setrecursionlimit(4000)

for N in [21, 1000]:
    print("For N = {}".format(N))
    print("When A = 1")
    s = Q1Solver(N)
    s.calculate()
    print("mean = {} \nsd   = {}".format(*s.mean_sd()))
    # A is the event that score is at least 5
    p_A = s.prob[1:5].sum()
    # calculate the probabilities when 8 is not seen
    s.calculate(exclude=[8])
    # B is the event that 8 is seen at least once
    p_B = 1 - s.prob.sum()
    p_A_minus_B = s.prob[1:5].sum()
    p_A_cond_B = (p_A - p_A_minus_B) / p_B
    print("conditional prob = {}".format(p_A_cond_B))

    print("When A = 11")
    s = Q1Solver(N, A=11)
    s.calculate()
    print("mean = {} \nsd   = {}".format(*s.mean_sd()))
    print()