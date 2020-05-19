import logging
import minesweeper as ms
import ais as myai
import concurrent.futures

levels = [
    [8,8,10],
    [16,16,40],
    [30,16,99]
]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
MAX_THREADS = 12
num_games = 1
config = ms.GameConfig(*levels[0])
ai = myai.BasicAI(myai.AlgorithmBeta(config))
viz = ms.PyGameVisualizer(pause='key', next_game_prompt=True)
    

def main():
    print("This will play a single game and then quit.")
    print("The minesweeper window needs focus to capture a key press.")
    print()

    # results = ms.run_games(config, num_games, ai)
    results = ms.run_games(config, num_games, ai, threads=MAX_THREADS)
    print('\n\nResults:')
    print('-------------------------')

    num_wins = 0
    for i, result in results:
        num_wins += result.victory == True
        print('Game {:2d}: {:3d} steps, {:s}'.format(i, result.num_moves,'win' if result.victory else 'failed'))

    ratio = num_wins / num_games
    print('-------------------------')
    print('Ratio: {:.2f}'.format(ratio))

if __name__ == '__main__':
    main()