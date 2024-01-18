# Wordle Solver

Run `python wordle.py` to run in interactive mode. The program will provide a guess and you give it feedback based on the results from NYT wordle program.

To test the model, run `python wordle.py test` and the program will attempt to solve for every single word in the known dictionary of words. This can take a substantial amount of time, but will let you test the quality of the model by giving you an unlimited number of guess and averaging the number of guesses to solve as well as the count of times where numer of guesses exceeded six (the number of attempts allowed by the NYT game).