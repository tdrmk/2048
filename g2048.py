from collections import namedtuple
from random import choice
from random import random

# Animation operation to perform
STAY = 'STAY'
MOVE = 'MOVE'
MERGE = 'MERGE'
NEW = 'NEW'

Stay = namedtuple(STAY, ['value', 'position'])
Move = namedtuple(MOVE, ['value', 'from_position', 'to_position'])
Merge = namedtuple(MERGE, ['new_value', 'position'])
New = namedtuple(NEW, ['new_value', 'position'])

LEFT = 'LEFT'
RIGHT = 'RIGHT'
UP = 'UP'
DOWN = 'DOWN'

class G2048:
    def __init__(self, size):
        # Only thing needed to construct the board is size.
        self.size = size
        self.__reset__()

    def __reset__(self):
        self._score = 0
        # Re-tile the board with empty values.
        self.board = {(x, y): 0 for x in range(self.size) for y in range(self.size)}
        # Random set two values
        self[self.next()] = self.tile()
        self[self.next()] = self.tile()

    def __inc_score__(self, inc):
        self._score += inc

    @property
    def score(self):
        return self._score

    def __getitem__(self, position):
        return self.board[position]

    def __setitem__(self, position, value):
        self.board[position] = value

    def __iter__(self):
        return iter(self.board.keys())

    def reset(self):
        self.__reset__()

    def empty(self):
        return len([pos for pos in self if not self[pos]])

    def next(self):
        empty_tiles = [pos for pos in self if not self[pos]]
        if empty_tiles:
            return choice(empty_tiles)
        # If no more empty tiles.
        return None

    @staticmethod
    def tile():
        # Randomly return the next tile to be places on empty location.
        return 2 if random() >= 0.5 else 4

    def __bool__(self):
        # Function check's if any more move is available.
        for x in range(self.size):
            for y in range(self.size):
                if not self[x, y]:
                    # If empty cell possible to continue.
                    return True
                if (x > 0 and self[x - 1, y] == self[x, y]) or (y > 0 and self[x, y - 1] == self[x, y]):
                    # If possibility of merge exists.
                    return True
        return False

    @staticmethod
    def compress(values):
        prev_value, index_returned = 0, 0
        new_values = [0 for _ in values]
        for value in values:
            if not value:
                continue
            elif not prev_value:
                # Just set it to current value
                prev_value = value
            elif prev_value != value:
                # Previous value not equals current value.
                new_values[index_returned], prev_value = prev_value, value
                index_returned += 1
            else:
                # Equal to current value.
                new_values[index_returned], prev_value = prev_value * 2, 0
                index_returned += 1
        if prev_value:
            new_values[index_returned] = prev_value

        return new_values

    @staticmethod
    def compress_with_steps(values):
        prev_index, prev_value, index_returned = 0, 0, 0

        def stay_or_move():
            nonlocal prev_value, prev_index, index_returned
            if prev_index == index_returned:
                return STAY, Stay(prev_value, prev_index)
            return MOVE, Move(prev_value, prev_index, index_returned)

        for index, value in enumerate(values):
            if not value:
                # [EMPTY CELL]: Just go to next value
                continue
            elif not prev_value:
                # Just set it to current value
                prev_index, prev_value = index, value
            elif prev_value != value:
                # Previous value not equals current value.
                yield stay_or_move()
                index_returned += 1
                prev_index, prev_value = index, value
            else:
                # Equal to current value.
                yield stay_or_move()
                yield MOVE, Move(value, index, index_returned)
                yield MERGE, Merge(2 * value, index_returned)
                index_returned += 1
                prev_index, prev_value = 0, 0

        if prev_value:
            yield stay_or_move()

    def move_up(self):
        animations = {STAY: [], MOVE: [], MERGE: [], NEW: []}
        if self:
            changed = False
            for x in range(self.size):
                values = [self[x, y] for y in range(self.size)]
                for operation, rest in self.compress_with_steps(values):
                    if operation == STAY:
                        animations[STAY].append(Stay(rest[0], (x, rest[1])))
                    if operation == MOVE:
                        animations[MOVE].append(Move(rest[0], (x, rest[1]), (x, rest[2])))
                    if operation == MERGE:
                        animations[MERGE].append(Merge(rest[0], (x, rest[1])))
                        self.__inc_score__(rest[0])
                new_values = self.compress(values)
                for y, value in enumerate(new_values):
                    if self[x, y] != value:
                        changed = True
                        self[x, y] = value
            if changed:
                new_position, new_value = self.next(), self.tile()
                animations[NEW].append(New(new_value, new_position))
                self[new_position] = new_value

            return animations

    def move_stats(self, direction):
        # Method to evaluate the stats associated with a move in a given direction.
        score_inc = 0
        operation_stats = {STAY: 0, MOVE: 0, MERGE: 0, NEW: 0}
        changed = False

        for x in range(self.size):
            if direction == UP:
                values = [self[x, y] for y in range(self.size)]
            elif direction == DOWN:
                values = [self[x, y] for y in reversed(range(self.size))]
            elif direction == LEFT:
                values = [self[y, x] for y in range(self.size)]
            else:   # direction == RIGHT
                values = [self[y, x] for y in reversed(range(self.size))]

            for operation, rest in self.compress_with_steps(values):
                if operation == STAY:
                    operation_stats[STAY] += 1
                if operation == MOVE:
                    operation_stats[MOVE] += 1
                    changed = True
                if operation == MERGE:
                    operation_stats[MERGE] += 1
                    score_inc += rest[0]
                    changed = True

        return changed, score_inc, operation_stats

    def move_left(self):
        animations = {STAY: [], MOVE: [], MERGE: [], NEW: []}
        if self:
            changed = False
            for y in range(self.size):
                values = [self[x, y] for x in range(self.size)]
                for operation, rest in self.compress_with_steps(values):
                    if operation == STAY:
                        animations[STAY].append(Stay(rest[0], (rest[1], y)))
                    if operation == MOVE:
                        animations[MOVE].append(Move(rest[0], (rest[1], y), (rest[2], y)))
                    if operation == MERGE:
                        animations[MERGE].append(Merge(rest[0], (rest[1], y)))
                        self.__inc_score__(rest[0])

                new_values = self.compress(values)
                for x, value in enumerate(new_values):
                    if self[x, y] != value:
                        changed = True
                        self[x, y] = value
            if changed:
                new_position, new_value = self.next(), self.tile()
                animations[NEW].append(New(new_value, new_position))
                self[new_position] = new_value

            return animations

    def move_down(self):
        animations = {STAY: [], MOVE: [], MERGE: [], NEW: []}
        if self:
            changed = False
            for x in range(self.size):
                values = [self[x, y] for y in reversed(range(self.size))]
                for operation, rest in self.compress_with_steps(values):
                    if operation == STAY:
                        animations[STAY].append(Stay(rest[0], (x, self.size - rest[1] - 1)))
                    if operation == MOVE:
                        animations[MOVE].append(
                            Move(rest[0], (x, self.size - rest[1] - 1), (x, self.size - rest[2] - 1)))
                    if operation == MERGE:
                        animations[MERGE].append(Merge(rest[0], (x, self.size - rest[1] - 1)))
                        self.__inc_score__(rest[0])

                new_values = reversed(self.compress(values))
                for y, value in enumerate(new_values):
                    if self[x, y] != value:
                        changed = True
                        self[x, y] = value
            if changed:
                new_position, new_value = self.next(), self.tile()
                animations[NEW].append(New(new_value, new_position))
                self[new_position] = new_value

            return animations

    def move_right(self):
        animations = {STAY: [], MOVE: [], MERGE: [], NEW: []}
        if self:
            changed = False
            for y in range(self.size):
                values = [self[x, y] for x in reversed(range(self.size))]
                for operation, rest in self.compress_with_steps(values):
                    if operation == STAY:
                        animations[STAY].append(Stay(rest[0], (self.size - rest[1] - 1, y)))
                    if operation == MOVE:
                        animations[MOVE].append(
                            Move(rest[0], (self.size - rest[1] - 1, y), (self.size - rest[2] - 1, y)))
                    if operation == MERGE:
                        animations[MERGE].append(Merge(rest[0], (self.size - rest[1] - 1, y)))
                        self.__inc_score__(rest[0])

                new_values = reversed(self.compress(values))
                for x, value in enumerate(new_values):
                    if self[x, y] != value:
                        changed = True
                        self[x, y] = value
            if changed:
                new_position, new_value = self.next(), self.tile()
                animations[NEW].append(New(new_value, new_position))
                self[new_position] = new_value

            return animations

    def __repr__(self):
        return '\n'.join([' '.join('%5d' % self[x, y] for x in range(self.size)) for y in range(self.size)])


if __name__ == '__main__':
    game = G2048(4)
