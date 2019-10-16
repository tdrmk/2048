import g2048


def solver(game: g2048.G2048):
    def scoring_function(changed, score_inc, operation_stats):
        if not changed:
            return -1
        return operation_stats[g2048.MERGE] + score_inc

    scores = {
        g2048.LEFT: scoring_function(*game.move_stats(g2048.LEFT)),
        g2048.RIGHT: scoring_function(*game.move_stats(g2048.RIGHT)),
        g2048.UP: scoring_function(*game.move_stats(g2048.UP)),
        g2048.DOWN: scoring_function(*game.move_stats(g2048.DOWN)),
    }

    chosen_direction = max(list(scores), key=lambda direction: scores[direction])
    print(f'[AI] DIRECTION: {chosen_direction} SCORE:{scores[chosen_direction]}')
    return chosen_direction
