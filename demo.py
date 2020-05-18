import logging
import minesweeper as ms
import ais as myai
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

print("This will play a single game and then quit.")
print("The minesweeper window needs focus to capture a key press.")
print()

num_games = 1
config = ms.GameConfig(16,16,40)
ai = myai.BasicAI(myai.AlgorithmBeta(config))
viz = ms.PyGameVisualizer(pause='key', next_game_prompt=True)


results = ms.run_games(config, num_games, ai,viz)
print('\n\nResults:')
print('-------------------------')

num_wins = 0
for i, result in enumerate(results):
    num_wins += result.victory == True
    print('Game {:2d}: {:3d} steps, {:s}'.format(i, result.num_moves,'win' if result.victory else 'failed'))

ratio = num_wins / num_games
print('-------------------------')
print('Ratio: {:.2f}'.format(ratio))