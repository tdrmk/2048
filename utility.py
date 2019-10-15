from copy import deepcopy
from random import shuffle

LEFT = 'LEFT'
RIGHT = 'RIGHT'
UP = 'UP'
DOWN = 'DOWN'

def solver(game):
    game_1 = deepcopy(game)
    game_1.move_left()
    game_2 = deepcopy(game)
    game_2.move_right()
    game_3 = deepcopy(game)
    game_3.move_up()
    game_4 = deepcopy(game)
    game_4.move_down()

    scores = {LEFT: game_1.score, RIGHT: game_2.score, UP: game_3.score, DOWN: game_4.score}
    directions = [LEFT, RIGHT, UP, DOWN]
    shuffle(directions)
    return max(directions , key=lambda direction: scores[direction])
