# import .minesweeper as ms
import random
import itertools

from typing import List, Tuple, Set
from minesweeper import minesweeper as ms
import logging

logger = logging.getLogger(__name__)

def tuplelist_to_str(tl : List[Tuple[int, int]]) -> str:
    return ', '.join(['({:d},{:d})'.format(x, y) for x, y in tl])

class AlgorithmAlpha(object):
    def __init__(self, config: ms.GameConfig):
        super().__init__()
        self.width = config.width
        self.height = config.height
        self.exposed_squares = dict()
        self.flags = set()
    
    def update(self, new_squares: List[ms.Square]) -> List[Tuple[int,int]]:
        for square in new_squares:
            self.exposed_squares[(square.x, square.y)] = square

        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x,y) not in self.exposed_squares:
                break
        return [], [(x, y)]

class AlgorithmBeta(object):
    def __init__(self, config: ms.GameConfig):
        super().__init__()
        self.width = config.width
        self.height = config.height
        
        self.exposed_squares = dict()
        self.flags = set()
        self.safe_choices = set()

    def reset(self):
        self.exposed_squares.clear()
        self.flags.clear()
        self.safe_choices.clear()

    def _is_outside_board(self, x, y):
        if x < 0 or x >= self.width:
            return True
        if y < 0 or y >= self.height:
            return True
        return False
    
    def neighours(self, x, y):
        for dx, dy in itertools.product([-1, 0, 1], repeat=2):
            if dx == 0 and dy == 0:
                continue
            if not self._is_outside_board(x + dx, y + dy):
                yield x+dx, y+dy
    
    def check_neighbors(self, x, y):
        """The number of mines and unexposed squares around (x,y)"""
        marked_mines, unexposed_squares = 0, set()
        for nx, ny in self.neighours(x, y):
            if (nx ,ny) in self.flags:
                marked_mines += 1
                continue
            
            # We should also consider the squares in the safe choice list, as they can
            # be treated as exposed althrough we don't know its value(num_mines) yet.
            if (nx ,ny) not in self.exposed_squares and (nx, ny) not in self.safe_choices:
                unexposed_squares.add((nx ,ny))
        return marked_mines, unexposed_squares

    def update_flags(self) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """Returns an set of coordinates of newly found mines."""
        original_num_of_safe_choices = len(self.safe_choices)
        original_num_of_flags = len(self.flags)
        
        for (x, y), num_mines in self.exposed_squares.items():
            if num_mines == 0: continue
            marked_mines, unexposed_squares = self.check_neighbors(x, y)
            
            if not unexposed_squares: continue
            # Best case, all mines are recovered, only need to add the remaining neighbors
            # to save list.
            logger.debug('Processing ({:d}, {:d}), mines/total: {:d}/{:d}, unexposed: {:s}'
                         .format(
                             x, y,
                             marked_mines,
                             num_mines,
                             tuplelist_to_str(sorted(unexposed_squares))
                             )
                         )
            if marked_mines == num_mines:
                logger.debug("Nice, all mines are found, add remaining squares to safe list")
                self.safe_choices.update(unexposed_squares)
            elif marked_mines + len(unexposed_squares) == num_mines:
                # All unexposed squares are real mines. mark them.
                logger.debug("Good, these unexposed squares are actually mines, add them to flags")
                for mx, my in unexposed_squares:
                    self.flags.add((mx, my))
                    
        # If we find some new mines or safe choices, that means some of our 
        # judgements may be outdated. We run this process recursively to get
        # the optimal results.
        if original_num_of_safe_choices != len(self.safe_choices) or original_num_of_flags != len(self.flags):
            logger.debug("Recursively apply update_flags...")
            self.update_flags()
        return self.flags, self.safe_choices
    
    def update(self, new_squares: List[ms.Square]) -> Tuple[Set[Tuple[int,int]], Set[Tuple[int,int]]]:
        for square in new_squares:
            self.exposed_squares[(square.x, square.y)] = square.num_mines
            if (square.x, square.y) in self.safe_choices:
                self.safe_choices.remove((square.x, square.y))

        ## My awesome AI implementation.
        # First we will try to find as many MINES as possible.
        # self.safe_choices.clear()
        # self.safe_choices = self.safe_choices - set(new_squares.keys())
        flags, safe_choices = self.update_flags()
        
        return flags, safe_choices

class BasicAI(ms.AI):
    def __init__(self, algo = None):
        self.width = 0
        self.height = 0
        self.num_mines = 0
        self.exposed_squares = dict()
        self.algo = algo
        self.safe_choices = set()
        # Set[Tuple[int, int]]
        self._flags = set() 
    
    @property
    def flags(self):
        return list(self._flags)
    
    def reset(self, config: ms.GameConfig):
        self.width = config.width
        self.height = config.height
        self.num_mines = config.num_mines
        self.exposed_squares.clear()
        self._flags.clear()
        self.algo.reset()
        
    def pretty_print(self):
        """
        e.g.,
            DEBUG:  * 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
            DEBUG:  0 . . . . . . . . . . . . 1   1 1
            DEBUG:  1 . . . . . . . . . . . . 1   1 x
            DEBUG:  2 . . . . . . . . . . . 1 2 1 2 1
            DEBUG:  3 . . . . . . . . . . . . 2 x 1
            DEBUG:  4 . . . . . . . . . . . . 4 3 2 1
            DEBUG:  5 . . . . . . 2 x 3 1 2 x x 2 x 1
            DEBUG:  6 . . . . . . 2 1 1   1 2 2 2 1 1
            DEBUG:  7 . . . . . . 2 1
            DEBUG:  8 . . . . . 3 x 2 1 1 1 1
            DEBUG:  9 . . . . . 2 2 x 1 1 x 2 1 1
            DEBUG: 10 . . . . . 1 2 2 2 1 1 2 x 1 1 1
            DEBUG: 11 . . . . . 1 2 x 2 1   1 1 1 1 x
            DEBUG: 12 . . . . . . . 3 x 2 1       1 1
            DEBUG: 13   . . . . . . . 3 x 2 1 1
            DEBUG: 14 . . . 1 . . . . 2 2 3 x 2 1 1 1
            DEBUG: 15 . . . . . . . . 1 1 x 3 x 1 1 x
        
        'x' indicates a mine has been marked.
        '.' indicates an unexposed square.
        numbers indicates mines around it.
        """
        output = []
        output.append(" ".join([" *"] + [str(i%10) for i in range(self.width)]))
        for y in range(self.height):
            line = ['{:2d}'.format(y)] + ["."] * self.width
            for x in range(self.width):
                if (x, y) in self.exposed_squares:
                    num_mine =  self.exposed_squares[(x,y)]
                    line[x+1] = str(num_mine) if num_mine != 0 else " "
                if (x,y) in self._flags:
                    line[x+1] = "x"
                    
            output.append(" ".join(line))
                    
        print("")
        for line in output:
            logger.info(line)
        print("")

    def next(self) -> Tuple[int, int]:
        if self.safe_choices:
            logger.debug('[AI.next] {:d} safe choices: {:s}'.format(len(self.safe_choices), tuplelist_to_str(sorted(self.safe_choices))))
            while self.safe_choices:
                x, y = self.safe_choices.pop()
                logger.debug("Choosing candidate ({:d}, {:d})".format(x ,y))
                if (x ,y) not in self._flags and (x ,y) not in self.exposed_squares:
                    logger.debug("Choosing one from safe list: ({:d}, {:d})".format(x ,y))
                    return (x ,y)

        # When AI can't predict the next safe choice, here we just randomly choice
        # one from those unexposed squares.
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x,y) not in self.exposed_squares and (x, y) not in self._flags:
                break
            logger.warning('Generating a random choice. flags: {:d}/{:d}'.format(len(self._flags), self.num_mines))
        return x, y
            
    def update(self, result: ms.MoveResult):
        if result.status == ms.GameStatus.DEFEAT:
            logger.info("##### NO NO NO! Game over! #####")
            return

        for square in result.new_squares:
            self.exposed_squares[(square.x, square.y)] = square.num_mines
            
        # AI will try its best to make a safe choice.
        flags, new_choices = self.algo.update(result.new_squares)
        self._flags.update(flags)
        self.safe_choices.update(new_choices)

        # Cleans safe choice list.
        self.safe_choices = self.safe_choices - set(self.exposed_squares.keys())
        # Logs current board state.
        self.pretty_print()