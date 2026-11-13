from abc import ABC, abstractmethod
from datetime import datetime


class Game(ABC) :

  ### CONSTRUCTOR ###
  def __init__(self, game_id, game_type, day) :
    self.game_id= game_id
    self.type= game_type
    self.day = day
    self.status= "in_progress"
    self.is_over= False

  ### END GAME ### 
  def end_game(self) :
    self.is_over= True
    self.status= "finished"

  @abstractmethod
  def make_move(self, move) :
    """must be implemented by subclasses to make a move"""
    pass

  @abstractmethod
  def get_state(self) :
    """must be implemented by subclasses to save game state"""
    pass
