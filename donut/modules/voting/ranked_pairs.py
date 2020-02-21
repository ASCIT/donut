from itertools import chain, combinations, product


def winners(responses):
    """
    Returns the list of ranked-pairs winners based on responses.
    Takes as input a list of rankings, e.g. [
        [['A'], ['B'], ['NO']], # A, then B, then NO, then C
        [['A', 'C'], ['B']],    # A or C, then B, then NO
        [['NO']]                # NO, then A or B or C
    ]
    """
    all_candidates = set(vote
                         for response in responses for rank in response
                         for vote in rank)
    tallies = {  # mapping of pairs (A, B) of candidates
        pair: 0  # to numbers of responders who ranked A above B
        for pair in product(all_candidates, repeat=2)
    }
    for response in responses:
        ranked = set(vote for rank in response for vote in rank)
        ranks = chain(response, (all_candidates - ranked, ))
        for rank_A, rank_B in combinations(ranks, 2):
            for A in rank_A:
                for B in rank_B:
                    tallies[A, B] += 1

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
    return sorted(all_candidates, key=lambda A: len(higher[A]))
