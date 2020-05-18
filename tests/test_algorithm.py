import pytest

from ais import AlgorithmBeta
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
def algo_case1():
    """ Four flags and one exposed.
           0 1 2 3 4  (x)
        0 [x . . . .]
        1 [1 . . x .]
        2 [. . . x .]
        3 [. . x . .]
       (y)
    """
    algo =  AlgorithmBeta(ms.GameConfig(5, 4, 4))
    algo.flags = {(0,0), (3,1), (3,2), (2,3)}
    algo.exposed_squares = {(0, 1) : 1}
    return algo

@pytest.fixture
def algo_case2():
    """ Four flags and two exposed.
           0 1 2 3 4  (x)
        0 [x . . . .]
        1 [1 2 . x .]
        2 [. . . x .]
        3 [. . x . .]
       (y)
    """
    algo =  AlgorithmBeta(ms.GameConfig(5, 4, 4))
    algo.flags = {(0,0), (3,1), (3,2), (2,3)}
    algo.exposed_squares = {(0, 1):1, (1,1):2}
    return algo

@pytest.fixture
def algo_case3():
    """ Four flags and four exposed. case3
           0 1 2 3 4  (x)
        0 [x . 2 . 1]
        1 [1 . . x .]
        2 [. . . x .]
        3 [. . x . 1]
       (y)
    """
    algo =  AlgorithmBeta(ms.GameConfig(5, 4, 4))
    algo.flags = {(0,0), (3,1), (3,2), (2,3)}
    algo.exposed_squares = {(0,1):1, (2,0):2, (4,0):1, (4,3):1}
    return algo

def test_algo_neighours(algo_case1):
    algo = algo_case1
    assert set(algo.neighours(0, 0)) == {(1,0), (0,1), (1,1)}
    assert set(algo.neighours(0, 1)) == {(0,0), (0,2), (1,0), (1,1), (1,2)}
    assert set(algo.neighours(1, 1)) == {(0,0), (0,1), (0,2), (1,0), (1,2), (2,0), (2,1), (2,2)}
    assert set(algo.neighours(0, 3)) == {(0,2), (1,2), (1,3)}
    assert set(algo.neighours(4, 0)) == {(3,0), (3,1), (4,1)}
    assert set(algo.neighours(4, 3)) == {(3,2), (4,2), (3,3)}
    
def test_algo_check_neighbors_case1(algo_case1):
    algo = algo_case1
    """ Four flags and one exposed.
           0 1 2 3 4  (x)
        0 [x . . . .]
        1 [1 . . x .]
        2 [. . . x .]
        3 [. . x . .]
       (y)
    """
    test_cases = [
        # column 0
        ((0,1), 1, {(1,0), (1,1), (1,2), (0,2)}),
        ((0,2), 0, {(1,1), (1,2), (1,3), (0,3)}),
        ((0,3), 0, {(0,2), (1,2), (1,3)}),
        # column 1
        ((1,0), 1, {(1,1), (2,0), (2,1)}),
        ((1,1), 1, {(1,0), (2,0), (2,1), (2,2), (1,2), (0,2)}),
        ((1,2), 1, {(1,1), (2,1), (0,2), (2,2), (0,3), (1,3)}),
        ((1,3), 1, {(0,2), (1,2), (2,2), (0,3)}),
        # column 2
        ((2,0), 1, {(1,0), (3,0), (1,1), (2,1)}),
        ((2,1), 2, {(1,0), (2,0), (3,0), (1,1), (1,2), (2,2)}),
        ((2,2), 3, {(1,1), (2,1), (1,2), (1,3), (3,3)}),
        # column 3
        ((3,0), 1, {(2,0), (4,0), (2,1), (4,1)}),
        ((3,3), 2, {(2,2), (4,2), (4,3)}),
        # colum 4
        ((4,0), 1, {(3,0), (4,1)}),
        ((4,1), 2, {(3,0), (4,0), (4,2)}),
        ((4,2), 2, {(4,1), (3,3), (4,3)}),
        ((4,3), 1, {(4,2), (3,3)}),
    ]
    
    for (x,y), expected_marked_mines, expected_unexposed in test_cases:
        marked_mines, unexposed = algo.check_neighbors(x, y)
        assert marked_mines == expected_marked_mines
        assert set(unexposed) == expected_unexposed
    
def test_algo_check_neighbors_case2(algo_case2):
    """ Four flags and two exposed.
           0 1 2 3 4  (x)
        0 [x . . . .]
        1 [1 2 . x .]
        2 [. . . x .]
        3 [. . x . .]
       (y)
    """
    algo = algo_case2
    test_cases = [
        # column 0
        ((0,1), 1, {(1,0), (1,2), (0,2)}),
        ((0,2), 0, {(1,2), (1,3), (0,3)}),
        ((0,3), 0, {(0,2), (1,2), (1,3)}),
        # column 1
        ((1,0), 1, {(2,0), (2,1)}),
        ((1,1), 1, {(1,0), (2,0), (2,1), (2,2), (1,2), (0,2)}),
        ((1,2), 1, {(2,1), (0,2), (2,2), (0,3), (1,3)}),
        ((1,3), 1, {(0,2), (1,2), (2,2), (0,3)}),
        # column 2
        ((2,0), 1, {(1,0), (3,0), (2,1)}),
        ((2,1), 2, {(1,0), (2,0), (3,0), (1,2), (2,2)}),
        ((2,2), 3, {(2,1), (1,2), (1,3), (3,3)}),
        # column 3
        ((3,0), 1, {(2,0), (4,0), (2,1), (4,1)}),
        ((3,3), 2, {(2,2), (4,2), (4,3)}),
        # colum 4
        ((4,0), 1, {(3,0), (4,1)}),
        ((4,1), 2, {(3,0), (4,0), (4,2)}),
        ((4,2), 2, {(4,1), (3,3), (4,3)}),
        ((4,3), 1, {(4,2), (3,3)}),
    ]
    
    for (x,y), expected_marked_mines, expected_unexposed in test_cases:
        marked_mines, unexposed = algo.check_neighbors(x, y)
        assert marked_mines == expected_marked_mines
        assert set(unexposed) == expected_unexposed
    
def test_algo_update_flags_case1(algo_case1):
    algo = algo_case1
    """ Four flags and one exposed.
           0 1 2 3 4  (x)
        0 [x . . . .]
        1 [1 . . x .]
        2 [. . . x .]
        3 [. . x . .]
       (y)
    """
    flags, safe_choices = algo.update_flags()
    assert flags == {(0,0), (2,3), (3,1), (3,2)}
    assert safe_choices == {(1,0), (1,1), (1,2), (0,2)}

def test_algo_update_flags_case2(algo_case2):
    algo = algo_case2
    """ Four flags and one exposed.
           0 1 2 3 4  (x)
        0 [x . . . .]
        1 [1 2 . x .]
        2 [. . . x .]
        3 [. . x . .]
       (y)
    """
    flags, safe_choices = algo.update_flags()
    assert flags == {(0,0), (3,1), (3,2), (2,3)}
    assert safe_choices == {(1,0), (1,2), (0,2)}
    
    
def test_algo_update_flags_case3(algo_case3):
    algo = algo_case3
    """ Four flags and four exposed. case3
           0 1 2 3 4  (x)
        0 [x o 2 o 1]
        1 [1 o M x o]
        2 [o o . x o]
        3 [. . x o 1]
       (y)
       
    Here, M(2,1) is the new discovered `mine`.
    """

    flags, safe_choices = algo.update_flags()
    assert flags == {(0,0), (3,1), (3,2), (2,3), (2,1)}
    assert safe_choices == {(1,0), (1,1), (1,2), (0,2), (3,0), (4,1), (4,2), (3,3)}