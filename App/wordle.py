from App.game import Game
from App.wordleWords import wordle_dict
from App.dictionary import valid_words

class Wordle(Game) :
	WORD_LENGTH= 5
	MAX_ATTEMPTS= 6

	### CONSTRUCTOR ###
	def __init__(self, game_id, day) :
		super().__init__(game_id, "wordle", day)
		self.word= self.get_daily_word()
		self.attempts= 0
		self.guesses= {}
		self.won= False


	### GET DAILY WORD ###
	def get_daily_word(self) :
		return wordle_dict[str(self.day)]

	### MAKE A MOVE ###
	def make_move(self, user_guess) :
		if self.is_over :
			return {"error": "game already finished"}
		
		self.status= "in_progress"
		guess = user_guess

		if len(guess) != self.WORD_LENGTH :
			return {"error": "word must be 5 letters long!"}
		elif guess in self.guesses:
			return {"error": "word already guessed!"}
		elif not self.is_valid_word(guess) and guess not in wordle_dict[str(self.day)] :
			return {"error": "invalid word!"}
		
		self.attempts+= 1
		letter_states= self.check_guess(guess)
		self.guesses[guess] = letter_states

		# end game if word is guessed or max attempts reached
		if guess == self.word :
			self.won= True
			self.end_game()
		elif self.attempts >= self.MAX_ATTEMPTS :
			self.end_game()

		result= {
			"guess": guess,
			"letter_states": letter_states,
			"word" : self.word,
			"won" : self.won,
			"is_over": self.is_over,
			"attempts_left": self.MAX_ATTEMPTS - self.attempts
		}
		return result


	### GUESS VALIDATION ###
	def check_guess(self, user_guess) :
		letter_states= []

		for i in range(len(user_guess)) :
			if user_guess[i] == self.word[i] :
				letter_states.append("correct")
			elif user_guess[i] in self.word :
				letter_states.append("present")
			else :
				letter_states.append("absent")

		return letter_states

	def is_valid_word(self, guess) :	
		return guess in valid_words
	
	### GET GAME STATE ###
	def get_state(self) :
		state= {
			"status": self.status,
			"guesses": self.guesses,
			"won": self.won,
			"word": self.word,
      		"is_over": self.is_over,
			"attempts_left": self.MAX_ATTEMPTS - self.attempts
		}
		return state
