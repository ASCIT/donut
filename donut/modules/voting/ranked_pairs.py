from collections import OrderedDict
from itertools import product

WINNERS_TO_LIST = 3


def winners(responses):
    """
    Returns the list of ranked-pairs winners based on responses.
    Takes as input a list of rankings, e.g. [
        ['A', 'B', 'NO'], # A then B then NO
        ['C', 'A'],       # A then C
        ['NO']            # NO
    ]
    """
    all_candidates = set(vote for response in responses for vote in response)
    tallies = {  # mapping of pairs (A, B) of candidates
        pair: 0  # to numbers of responders who ranked A above B
        for pair in product(all_candidates, repeat=2)
    }
    for response in responses:
        response_dict = OrderedDict.fromkeys(response)
        response = list(response_dict)
        for i, A in enumerate(response[:-1]):
            for B in response[i + 1:]:
                tallies[A, B] += 1
        for candidate in all_candidates:  # assume voter put all unpicked candidates lower
            if candidate not in response_dict:
                for vote in response:
                    tallies[vote, candidate] += 1

    def tally_ranking(pair):
        """
        The keyfunction which implements the 'ranking' in ranked pairs.
        Sorts pairs by highest in favor, or if equal, fewest opposed.
        """
        A, B = pair
        return (-tallies[A, B], tallies[B, A])

    possible_pairs = sorted(tallies, key=tally_ranking)
    # Vertices reachable from A in win graph
    lower = {A: set([A]) for A in all_candidates}
    # Vertices A is reachable from in win graph
    higher = {A: set([A]) for A in all_candidates}
    for A, B in possible_pairs:
        if A not in lower[B]:  # if we don't already have B > A, set A > B
            for s in higher[A]:  #     if s > ... > A
                for t in lower[B]:  #  and          B > ... > t
                    lower[s].add(t)  # then s > ... > t
                    higher[t].add(s)
    winners = sorted(all_candidates, key=lambda A: len(higher[A]))
    return winners[:WINNERS_TO_LIST]
