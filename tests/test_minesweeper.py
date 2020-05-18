import pytest

import minesweeper as ms


def flip(array):
    # boards are stored [x][y] but easier to type as [y][x] so we flip dimensions
    return [list(a) for a in zip(*array)]


@pytest.fixture
def game1():
    mines = flip([
        [True,  False, False, False, False],
        [False, False, False, True,  False],
        [False, False, False, True,  False],
        [False, False, True,  False, False]
    ])
    return ms.Game(ms.GameConfig(5, 4, 4), mines)


@pytest.fixture
def game2():
    mines = flip([
        [False, True,  False],
        [False, False, False],
        [False, False, True]
    ])
    return ms.Game(ms.GameConfig(3, 3, 2), mines)


@pytest.fixture
def game3():
    mines = flip([
        [False, False, False],
        [False, False, False],
        [False, False, True]
    ])
    return ms.Game(ms.GameConfig(3, 3, 1), mines)


@pytest.fixture
def game4():
    mines = flip([
        [False, False, True],
        [False, False, False],
        [True,  False, True]
    ])
    return ms.Game(ms.GameConfig(3, 3, 3), mines)


def test_game_init_for_total_mine_count():
    game = ms.Game(ms.GameConfig(100, 100, 800))
    assert 800 == sum(row.count(True) for row in game.mines)


def test_game_init_for_neighbor_mine_counts(game1):
    counts = flip([
        [-1, 1, 1, 1, 1],
        [1, 1, 2, -1, 2],
        [0, 1, 3, -1, 2],
        [0, 1, -1, 2, 1]
    ])
    assert counts == game1.counts


def test_select_expose_only_selected_square(game2):
    result = game2.select(1, 1)
    assert not game2.game_over
    assert ms.GameStatus.PLAYING == result.status
    assert 1 == len(result.new_squares)
    assert ms.Square(1, 1, 2) in result.new_squares


def test_select_expose_multiple_squares(game2):
    result = game2.select(0, 2)
    assert not game2.game_over
    assert ms.GameStatus.PLAYING == result.status
    assert 4 == len(result.new_squares)
    assert ms.Square(0, 2, 0) in result.new_squares
    assert ms.Square(0, 1, 1) in result.new_squares
    assert ms.Square(1, 1, 2) in result.new_squares
    assert ms.Square(1, 2, 1) in result.new_squares


def test_select_with_square_outside_board(game2):
    with pytest.raises(ValueError):
        game2.select(2, 3)
    assert 0 == game2.num_moves


def test_select_with_already_exposed_square(game2):
    game2.select(0, 2)
    with pytest.raises(ValueError):
        game2.select(1, 1)
    assert 1 == game2.num_moves


def test_select_when_game_is_already_over(game2):
    game2.select(1, 0)
    with pytest.raises(ValueError):
        game2.select(0, 0)
    assert game2.game_over


def test_select_with_mine(game2):
    result = game2.select(1, 0)
    assert game2.game_over
    assert 1 == len(result.new_squares)
    assert ms.Square(1, 0, -1) in result.new_squares


def test_select_with_victory(game3):
    result = game3.select(0, 0)
    assert 8 == len(result.new_squares)
    assert game3.game_over


def test_game_result_when_game_over(game3):
    game3.select(0, 0)
    assert game3.result.victory
    assert 1 == game3.result.num_moves


def test_game_result_when_not_over(game2):
    game2.select(0, 0)
    with pytest.raises(ValueError):
        game2.result


def test_game_result_after_quitting(game2):
    game2.select(0, 0)
    game2.quit()
    assert not game2.result.victory
    assert 1 == game2.result.num_moves


def test_game_over_after_quit(game2):
    game2.select(0, 0)
    game2.quit()
    assert game2.game_over


def test_status_at_beginning_of_game(game2):
    assert ms.GameStatus.PLAYING == game2.status


def test_status_after_mine_explosion(game2):
    game2.select(1, 0)
    assert ms.GameStatus.DEFEAT == game2.status


def test_status_after_victory(game3):
    game3.select(0, 0)
    assert ms.GameStatus.VICTORY == game3.status


def test_status_after_quitting(game2):
    game2.select(0, 0)
    game2.quit()
    assert ms.GameStatus.QUIT == game2.status


def test_state_at_start(game4):
    expected = flip([
        [None, None, None],
        [None, None, None],
        [None, None, None]
    ])
    assert expected == game4.state


def test_state_after_a_move(game4):
    expected = flip([
        [0,    1,    None],
        [1,    3,    None],
        [None, None, None]
    ])
    game4.select(0, 0)
    assert expected == game4.state


def test_flags(game1):
    game1.flags = [(0, 1)]
    assert isinstance(game1.flags, set)
    assert 1 == len(game1.flags)


def test_square_eq_with_match():
    assert ms.Square(0, 0, 0) == ms.Square(0, 0, 0)
    assert ms.Square(5, 7, 3) == ms.Square(5, 7, 3)


def test_square_eq_with_no_match():
    assert ms.Square(5, 7, 3) != ms.Square(5, 8, 3)
    assert ms.Square(5, 7, 3) != ms.Square(4, 7, 3)
    assert ms.Square(5, 7, 3) != ms.Square(5, 7, 1)


def test_square_eq_with_wrong_type():
    assert ms.Square(1, 2, 3) != 72


def test_run_games():
    config = ms.GameConfig()
    ai = ms.RandomAI()
    results = ms.run_games(config, 2, ai)
    assert 2 == len(results)
