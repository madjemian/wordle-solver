from typing import Dict, List, Tuple
import sys
import time

INTERACTIVE = False
PROBABILITY_CACHE = {}

def load_word_file(filename: str) -> List[str]:
  """Load the words from the file filename into a list."""
  with open(filename, 'r') as f:
    words = f.readlines()
    words = [word.strip().lower() for word in words if word.strip() != '']
  return words

def load_words() -> List[str]:
  """Load the words from the file words.txt into a list."""
  return load_word_file('words.txt')

def load_used_words() -> List[str]:
  """Load the words from the file usedwords.txt into a list."""
  return load_word_file('usedwords.txt')

def character_probabilities(words: List[str], chars: List[str]) -> Dict[str, float]:
  """Calculate the probability of each character appearing in the words."""
  return {char: sum(
    [1 if char in word else 0 for word in words])/len(words) for char in chars}

def character_position_probabilities(words: List[str], chars: List[str]) -> Dict[int, Dict[str, float]]:
  """Calculate the probability of each character appearing in each position."""
  return {i: {char: sum(
    [1 if char == word[i] else 0 for word in words])/len(words)
    for char in chars} for i in range(5)}

def valid_word(
    word: str,
    guessed_words: List[str],
    position_chars: List[str],
    must_have_chars: List[str]) -> bool:
  """Check if a word is a valid guess"""
  # these are the words we already guessed
  if word in guessed_words:
    return False

  # can this character be in this position?
  for i, char in enumerate(word):
    if char not in position_chars[i]:
      return False

  for char in must_have_chars:
    if char not in word:
      return False

  return True

def choose_next_guess(
    words: List[str],
    position_chars: List[str],
    must_have_chars: str,
    guessed_words: List[str]
    ) -> str:
  """Choose the next word to guess."""
  global PROBABILITY_CACHE
  available_chars = list(set(''.join(position_chars)))
  # filter the list to only include words that are valid
  filtered_words = [word for word in words if valid_word(
    word, guessed_words, position_chars, must_have_chars)]
  guess_key = '_'.join(position_chars)
  if PROBABILITY_CACHE.get(guess_key):
    char_probs = PROBABILITY_CACHE[guess_key]['char_probs']
    char_position_probs = PROBABILITY_CACHE[guess_key]['char_position_probs']
  else:
    char_probs = character_probabilities(filtered_words, available_chars)
    char_position_probs = character_position_probabilities(filtered_words, available_chars)
    # cache the results to save time when testing
    PROBABILITY_CACHE[guess_key] = {
      'char_probs': char_probs,
      'char_position_probs': char_position_probs
    }

  # if the list is long, don't use words that have duplicate letters since it won't give
  # us as much useful information
  filtered_with_doubles = filtered_words
  if len(filtered_words) > 100:
    filtered_words = [word for word in filtered_words if len(set(word)) == len(word)]

  # score the words based on character probabilities and character position probabilities
  word_scores = [(word,
    sum([char_probs[char]*char_position_probs[i][char] for i, char in enumerate(word)])
    )
    for word in filtered_words]
  word_scores.sort(key=lambda x: x[1], reverse=True)
  if INTERACTIVE:
    print('\tChoosing next guess...')
    print(f'\tRemaining words: {len(filtered_with_doubles)}')
    print(f'\tTop {min(3, len(word_scores))} words: {word_scores[:3]}')
  return word_scores[0][0]

def parse_feedback(feedback: str, guess: str, position_chars: List[str], must_have_chars: str) -> Tuple[List[str], str]:
  """Parse the feedback from the guess"""
  new_position_chars = [chars for chars in position_chars]
  new_must_have_chars = must_have_chars
  for i, char in enumerate(feedback):
    if char == '_':
      new_position_chars = [charlist.replace(guess[i], '') for charlist in new_position_chars]
    elif (char == '#'):
      new_position_chars[i] = new_position_chars[i].replace(guess[i], '')
      new_must_have_chars += guess[i]
    elif (char == '!'):
      new_position_chars[i] = guess[i]
      new_must_have_chars += guess[i]
  return new_position_chars, new_must_have_chars



def main():
  print('Welcome to MattGPT Wordle Solver!')
  all_words = load_words()
  used_words = load_used_words()
  word_list = [word for word in all_words if word not in used_words]
  print(f'Total Words: {len(all_words)}')
  print(f'Words Already Used by NYT: {len(used_words)}')
  position_chars = ['abcdefghijklmnopqrstuvwxyz' for i in range(5)]
  success = False
  attempts = 0
  guessed_words = []
  must_have_chars = ''
  while not success:
    attempts += 1
    guess = choose_next_guess(word_list, position_chars, must_have_chars, guessed_words)
    guessed_words.append(guess)
    print(f'Guess {attempts}: {guess}')
    feedback = input('Input feedback\n\t_ for incorrect character\n\t# for incorrect position\n\t! for correct position)\n')
    if (feedback == '!!!!!'):
      success = True
    else:
      position_chars, must_have_chars = parse_feedback(feedback, guess, position_chars, must_have_chars)
  print(f'Solved in {attempts} attempts.')
  pass

def test():
  print('Leave one out testing mode...')
  start = time.time()
  all_words = load_words()
  guesses = 0
  failures = 0
  for i, word in enumerate(all_words):
    test_word = word
    guess_count = guess_the_word(all_words, test_word)
    guesses += guess_count
    if guess_count > 6:
      failures += 1
    if i > 0 and i % 1000 == 0:
      print(f'Completed {i} words. average guesses: {guesses/i:.2f}, failures: {failures} ({failures/i:.1%})')

  end = time.time()
  print(f'Completed {len(all_words)} words in {(end-start)/60:.2f} minutes ({(end-start)/len(all_words)*1000:.3f} milliseconds per word).')
  print(f'Average guesses: {guesses/len(all_words):.2f}')
  print(f'Failures: {failures} ({failures/len(all_words):.1%})')
  pass

def guess_the_word(available_words: List[str], test_word: str) -> int:
  """Guess the word and return number of guesses it took"""
  position_chars = ['abcdefghijklmnopqrstuvwxyz' for i in range(5)]
  success = False
  attempts = 0
  guessed_words = []
  must_have_chars = ''
  while not success:
    attempts += 1
    guess = choose_next_guess(available_words, position_chars, must_have_chars, guessed_words)
    guessed_words.append(guess)
    feedback = ''
    for i, char in enumerate(guess):
      if char == test_word[i]:
        feedback += '!'
      elif char in test_word:
        feedback += '#'
      else:
        feedback += '_'
    if (feedback == '!!!!!'):
      success = True
    else:
      position_chars, must_have_chars = parse_feedback(feedback, guess, position_chars, must_have_chars)
  return attempts


if __name__ == '__main__':
  if len(sys.argv) == 1:
    INTERACTIVE = True
    main()
  else:
    # model testing mode
    test()
