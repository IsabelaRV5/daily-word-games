from App.game import Game
from App.spellingBeeLetters import spellingBee_letters
from App.dictionary import valid_words

class SpellingBee(Game) :
  MAX_LETTERS= 7
  MIN_WORD_LENGTH= 4
  LETTER_SCORE_THRESHOLD= 5
  SCORES = {
    "Beginner": 0,
    "Good-Start": 2,
    "Moving-Up": 5,
    "Good": 8,
    "Solid": 15,
    "Nice": 25,
    "Great": 40,
    "Amazing": 51,
    "Genius": 71,
    "Queen-Bee": 101
  }


  ### CONSTRUCTOR ###
  def __init__(self, game_id, day) :
    super().__init__(game_id, "spellingBee", day)
    self.letters= self.get_daily_letters()
    self.center_letter= self.letters[0]
    self.guesses= []
    self.score= 0
    self.tier= self.get_tier()


	### GET DAILY LETTERS ###
  def get_daily_letters(self) :
    return spellingBee_letters[str(self.day)]


  ### GET/SET TIER BASED ON SCORE ###
  def get_tier(self) :
    curr_tier= "Beginner"

    for tier, min_score in self.SCORES.items() :
      if self.score >= min_score :
        curr_tier= tier
      else :
        break
    return curr_tier


  ### MAKE A MOVE ###
  def make_move(self, user_guess) :
    if self.is_over :
      return {"error": "game already finished"}
    
    self.status= "in_progress"
    guess= user_guess.upper()

    error= self.check_guess(guess)
    if error :
      return error
    self.guesses.append(guess)

    # scoring
    if len(guess) < self.LETTER_SCORE_THRESHOLD :
      self.score+= 1
    else :
      self.score+= len(guess)

    # pangram bonus!
    is_pangram= self.is_pangram(user_guess)
    if is_pangram :
      self.score+= 7

    # update tier
    self.tier= self.get_tier()

    # end game if score is 101 (and tier is queen bee)
    if self.score >= 101 :
      self.end_game()

    result= {
      "status" : self.status,
      "is_over": self.is_over,
      "guess": guess,
      "score": self.score,
      "tier": self.tier,
      "pangram": is_pangram
    }
    
    return result


  ### GUESS VALIDATION ###
  def check_guess(self, user_guess) :
    if not user_guess :
      return {"error": "word cannot be empty!"}
    
    if self.center_letter not in user_guess :
      return {"error": f"word must contain the center letter: {self.center_letter}"}
    
    for letter in user_guess :
      if letter not in self.letters :
        return {"error": f"word must only contain the displayed letters: {self.letters}"}
      
    if not self.is_valid_word(user_guess) :
      return {"error": "invalid word!"}
    
    if user_guess in self.guesses :
      return {"error": "word already guessed!"}
    
    if len(user_guess) < self.MIN_WORD_LENGTH :
      return {"error": f"word must be at least {self.MIN_WORD_LENGTH} letters long!"}
    
    return None


  ### CHECKS IF GUESS IS A VALID WORD ###
  def is_valid_word(self, guess) :	
    return guess in valid_words
  

  ### CHECKS IF GUESS IS A PANGRAM ###
  def is_pangram(self, guess) :
    for l in self.letters :
      if l not in guess :
        return False
    return True
  

  ### GET GAME STATE ###
  def get_state(self) :
    state= {
      "status": self.status,
      "letters": self.letters,
      "tier": self.tier,
      "score": self.score,
      "guesses": self.guesses,
      "is_over" : self.is_over
    }
    return state
