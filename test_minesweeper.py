import unittest
import minesweeper as ms


class MineSweeperTestCase(unittest.TestCase):

    def flip(self, array):
        # boards are stored [x][y] but easier to visualize as [y][x] so we flip dimensions
        return [list(a) for a in zip(*array)]

    def reinit_game(self, game, mines):
        game.mines = mines
        game.counts = [[0 for y in range(game.height)] for x in range(game.width)]
        game.exposed = [[False for y in range(game.height)] for x in range(game.width)]
        game._explosion = False
        game._num_exposed_squares = 0
        game.num_moves = 0
        game._init_counts()

    def test_place_mines(self):
        game = ms.Game(ms.GameConfig(100, 100, 800))
        self.assertEqual(800, sum([row.count(True) for row in game.mines]))

    def test_init_counts(self):
        game = ms.Game(ms.GameConfig(5, 4, 4))
        mines = self.flip([
            [True,  False, False, False, False],
            [False, False, False, True,  False],
            [False, False, False, True,  False],
            [False, False, True,  False, False]
        ])
        counts = self.flip([
            [0, 1, 1, 1, 1],
            [1, 1, 2, 1, 2],
            [0, 1, 3, 2, 2],
            [0, 1, 1, 2, 1]
        ])
        self.reinit_game(game, mines)
        self.assertEqual(counts, game.counts)

    def test_select(self):
        game = ms.Game(ms.GameConfig(3, 3, 2))
        board = self.flip([
            [False, True,  False],
            [False, False, False],
            [False, False, True]
        ])
        self.reinit_game(game, board)

        #expose only same square
        result = game.select(1, 1)
        self.assertEqual(ms.GameStatus.PLAYING, result.status)
        self.assertEqual(1, len(result.new_squares))
        self.assertTrue(ms.Square(1, 1, 2) in result.new_squares)

        #expose neighbors
        result = game.select(0, 2)
        self.assertEqual(ms.GameStatus.PLAYING, result.status)
        self.assertEqual(3, len(result.new_squares))
        self.assertTrue(ms.Square(0, 2, 0) in result.new_squares)
        self.assertTrue(ms.Square(0, 1, 1) in result.new_squares)
        self.assertTrue(ms.Square(1, 2, 1) in result.new_squares)

        #select square already selected or exposed
        with self.assertRaises(ValueError):
            game.select(0, 2)

        #select outside the board
        with self.assertRaises(ValueError):
            game.select(2, 3)

        #boom
        result = game.select(1, 0)
        self.assertEqual(ms.GameStatus.DEFEAT, result.status)

        #select after game over
        with self.assertRaises(ValueError):
            game.select(2, 0)

    def test_game_over(self):
        game = ms.Game(ms.GameConfig(3, 3, 1))
        mines = self.flip([
            [False, False, True],
            [False, False, False],
            [False, False, False]
        ])
        self.reinit_game(game, mines)

        #not over before we start
        self.assertFalse(game.game_over)

        #over after explosion
        result = game.select(2, 0)
        self.assertEqual(ms.GameStatus.DEFEAT, result.status)
        self.assertTrue(game.game_over)

        #over when all the squares have been revealed
        self.reinit_game(game, mines)
        result = game.select(0, 0)
        self.assertEqual(ms.GameStatus.VICTORY, result.status)
        self.assertEqual(8, len(result.new_squares))
        self.assertTrue(game.game_over)

    def test_result(self):
        game = ms.Game(ms.GameConfig(3, 3, 1))
        mines = self.flip([
            [False, False, True],
            [False, False, False],
            [False, False, False]
        ])
        self.reinit_game(game, mines)

        #over after explosion
        game.select(2, 0)
        result = game.result
        self.assertFalse(result.victory)
        self.assertEqual(1, result.num_moves)

    def test_state(self):
        game = ms.Game(ms.GameConfig(3, 3, 3))
        mines = self.flip([
            [False, False, True],
            [False, False, False],
            [True,  False, True]
        ])
        self.reinit_game(game, mines)

        game.select(0, 0)
        expected = self.flip([
          [0,    1,    None],
          [1,    3,    None],
          [None, None, None]
        ])

        state = game.state
        for x in [0, 1, 2]:
            for y in [0, 1, 2]:
                self.assertEqual(expected[x][y], state[x][y])
