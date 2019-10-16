import pygame

import g2048

import utility

OFFSET = 0, 100
WIDTH = 100
SIZE = 4

pygame.init()
font_small = pygame.font.Font(None, WIDTH // 5)
font_medium = pygame.font.Font(None, WIDTH // 2)
font_large = pygame.font.Font(None, WIDTH)
font_xl = pygame.font.Font(None, SIZE * WIDTH // 5)


def key_down(event, key):
    return event.type == pygame.KEYDOWN and event.key == key


BACKGROUND = {
    0: (161, 151, 142),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 95, 59),
    128: (237, 207, 117),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}


def background(value):
    if value in BACKGROUND:
        return BACKGROUND[value]
    return 237, 190, 20


def foreground(value):
    if value in [2, 4]:
        return 119, 110, 101
    return 249, 246, 242


def draw_square(win, value, position, size=0.9 * WIDTH):
    offset = (WIDTH - size) // 2, (WIDTH - size) // 2
    sq_rect = int(WIDTH * position[0] + offset[0] + OFFSET[0]), \
              int(WIDTH * position[1] + offset[1] + OFFSET[1]), int(size), int(size)
    pygame.draw.rect(win, background(value), sq_rect)
    if value:
        text_surf = font_medium.render(str(value), True, foreground(value))
        text_rect = text_surf.get_rect()
        text_rect.center = (int(WIDTH * position[0] + WIDTH // 2 + OFFSET[0]),
                            int(WIDTH * position[1] + WIDTH // 2 + OFFSET[1]))
        win.blit(text_surf, text_rect)


def draw_game_over(win):
    text_surf = font_xl.render('GAME OVER', True, (0, 0, 0))
    text_rect = text_surf.get_rect()
    text_rect.center = (int(SIZE * WIDTH // 2 + OFFSET[0]),
                        int(SIZE * WIDTH // 2 + OFFSET[1]))
    win.blit(text_surf, text_rect)


def draw_score(win, score):
    pygame.draw.rect(win, (119, 110, 101), (SIZE * WIDTH * 9 // 16, WIDTH // 8, SIZE * WIDTH * 6 // 16, WIDTH * 6 // 8))
    text_surf = font_large.render('2048', True, (119, 110, 101))
    text_rect = text_surf.get_rect()
    text_rect.center = (int(SIZE * WIDTH // 4 + OFFSET[0]),
                        int(WIDTH // 2))
    win.blit(text_surf, text_rect)

    text_surf = font_small.render('SCORE', True, (249, 246, 242))
    text_rect = text_surf.get_rect()
    text_rect.center = (int(SIZE * WIDTH * 3 // 4 + OFFSET[0]),
                        int(WIDTH // 4))
    win.blit(text_surf, text_rect)

    text_surf = font_medium.render(str(score), True, (249, 246, 242))
    text_rect = text_surf.get_rect()
    text_rect.center = (int(SIZE * WIDTH * 3 // 4 + OFFSET[0]),
                        int(WIDTH * 5 // 9))
    win.blit(text_surf, text_rect)


def game_animations(win):
    processing = False
    animations = None
    counter = 0
    max_count = 5
    move_limit, merge_limit, new_limit = int(0.6 * max_count), int(0.8 * max_count), int(1.0 * max_count)

    def status():
        return processing

    def begin(_animations):
        nonlocal processing, animations, counter
        if _animations:
            animations = _animations
            counter = 0
            processing = True

    def proceed():
        nonlocal processing, counter
        for value, position in animations[g2048.STAY]:
            draw_square(win, value, position)

        for value, old_position, new_position in animations[g2048.MOVE]:
            if counter > move_limit:
                draw_square(win, value, new_position)
            else:
                f = counter / move_limit
                position = old_position[0] * (1 - f) + new_position[0] * f, \
                           old_position[1] * (1 - f) + new_position[1] * f
                draw_square(win, value, position)

        for value, position in animations[g2048.MERGE]:
            if counter > merge_limit:
                draw_square(win, value, position)
            elif counter > move_limit:
                f = (counter - move_limit) / (merge_limit - move_limit)
                size = 0.9 * WIDTH + 0.1 * WIDTH * f
                draw_square(win, value, position, size)

        for value, position in animations[g2048.NEW]:
            if counter > merge_limit:
                f = (counter - merge_limit) / (new_limit - merge_limit)
                size = 0.3 * WIDTH + 0.6 * WIDTH * f
                draw_square(win, value, position, size)

        counter += 1
        if counter == new_limit:
            processing = False

    return status, begin, proceed


def main_loop():
    win = pygame.display.set_mode((SIZE * WIDTH + 2 * OFFSET[0], SIZE * WIDTH + OFFSET[1]))
    pygame.display.set_caption('2048')
    clock = pygame.time.Clock()
    game = g2048.G2048(SIZE)
    # start, progress, animate = animation(win, font)
    status, begin, proceed = game_animations(win)
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or key_down(event, pygame.K_q):
                run = False
            if not status():
                if key_down(event, pygame.K_r):
                    game.reset()

                if game:
                    if key_down(event, pygame.K_LEFT):
                        # game.move(g2048.LEFT)
                        animations = game.move_left()
                        begin(animations)
                    elif key_down(event, pygame.K_RIGHT):
                        animations = game.move_right()
                        begin(animations)
                    elif key_down(event, pygame.K_UP):
                        animations = game.move_up()
                        begin(animations)
                    elif key_down(event, pygame.K_DOWN):
                        animations = game.move_down()
                        begin(animations)

                    if key_down(event, pygame.K_n):
                        direction = utility.solver(game)
                        if direction == g2048.LEFT:
                            animations = game.move_left()
                            begin(animations)
                        if direction == g2048.RIGHT:
                            animations = game.move_right()
                            begin(animations)
                        if direction == g2048.UP:
                            animations = game.move_up()
                            begin(animations)
                        if direction == g2048.DOWN:
                            animations = game.move_down()
                            begin(animations)

        win.fill((255, 255, 255))
        pygame.draw.rect(win, (119, 110, 101), (OFFSET[0], OFFSET[1], SIZE * WIDTH, SIZE * WIDTH))
        draw_score(win, game.score)
        if not status():
            for pos in game:
                draw_square(win, game[pos], pos)
            if not game:
                draw_game_over(win)
        else:
            for pos in game:
                draw_square(win, 0, pos)
            proceed()

        pygame.display.update()
        clock.tick(120)


if __name__ == '__main__':
    main_loop()
