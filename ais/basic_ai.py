# import .minesweeper as ms
import random

from typing import List, Tuple
from minesweeper import minesweeper as ms

class BasicAI(ms.AI):
    def __init__(self):
        self.width = 0
        self.height = 0
        self.exposed_squares = set()
        
    def reset(self, config: ms.GameConfig):
        self.width = config.width
        self.height = config.height
        self.exposed_squares.clear()
        
    def next(self) -> Tuple[int, int]:
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x,y) not in self.exposed_squares:
                break
        return x, y
            
    def update(self, result: ms.MoveResult):
        for square in result.new_squares:
            self.exposed_squares.add((square.x, square.y))