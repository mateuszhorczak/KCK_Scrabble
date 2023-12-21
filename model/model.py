from random import shuffle

from config import global_variables as gv


class Letter:
    def __init__(self, y, x, value):
        self.y = y
        self.x = x
        self.value = value

    def get_y(self):
        return self.y

    def get_x(self):
        return self.x

    def get_value(self):
        return self.value


class Tile:
    def __init__(self, letter):
        self.letter = letter.upper()
        if self.letter in gv.LETTER_VALUES:
            self.score = gv.LETTER_VALUES[self.letter]
        else:
            self.score = 0

    def get_letter(self):
        return self.letter

    def get_score(self):
        return self.score


class Bag:
    def __init__(self):
        self.bag = []
        self.initialize_bag()

    def add_to_bag(self, tile, quantity):
        for i in range(quantity):
            self.bag.append(tile)

    def initialize_bag(self):
        self.add_to_bag(Tile("A"), 9)
        self.add_to_bag(Tile("B"), 2)
        self.add_to_bag(Tile("C"), 2)
        self.add_to_bag(Tile("D"), 4)
        self.add_to_bag(Tile("E"), 12)
        self.add_to_bag(Tile("F"), 2)
        self.add_to_bag(Tile("G"), 3)
        self.add_to_bag(Tile("H"), 2)
        self.add_to_bag(Tile("I"), 9)
        self.add_to_bag(Tile("J"), 1)
        self.add_to_bag(Tile("K"), 1)
        self.add_to_bag(Tile("L"), 4)
        self.add_to_bag(Tile("M"), 3)
        self.add_to_bag(Tile("N"), 6)
        self.add_to_bag(Tile("O"), 8)
        self.add_to_bag(Tile("P"), 2)
        self.add_to_bag(Tile("Q"), 1)
        self.add_to_bag(Tile("R"), 6)
        self.add_to_bag(Tile("S"), 4)
        self.add_to_bag(Tile("T"), 6)
        self.add_to_bag(Tile("U"), 4)
        self.add_to_bag(Tile("V"), 2)
        self.add_to_bag(Tile("W"), 2)
        self.add_to_bag(Tile("X"), 1)
        self.add_to_bag(Tile("Y"), 2)
        self.add_to_bag(Tile("Z"), 2)
        shuffle(self.bag)

    def take_from_bag(self):
        # Removes a tile from the bag and returns it to the user. This is used for replenishing the rack.
        return self.bag.pop()

    def get_remaining_tiles(self):
        # Returns the number of tiles left in the bag.
        return len(self.bag)


class Rack:
    """
    Creates each player's 'dock', or 'hand'. Allows players to add, remove and replenish the number of tiles in their 
    hand.
    """

    def __init__(self, bag):
        # Initializes the player's rack/hand. Takes the bag from which the racks tiles will come as an argument.
        self.rack = []
        self.bag = bag
        self.initialize()

    def add_to_rack(self):
        # Takes a tile from the bag and adds it to the player's rack.
        self.rack.append(self.bag.take_from_bag())

    def initialize(self):
        # Adds the initial 7 tiles to the player's hand.
        for i in range(7):
            self.add_to_rack()

    def get_rack_str(self):
        # Displays the user's rack in string form.
        return ", ".join(str(item.get_letter()) for item in self.rack)

    def get_rack_arr(self):
        # Returns the rack as an array of tile instances
        return self.rack

    def get_letters_from_rack_arr(self):
        # Return the letters in array
        arr = []
        for item in self.rack:
            arr.append(item.get_letter())
        return arr

    def append_letter(self, tile):
        self.rack.append(tile)

    def remove_from_rack(self, tile):
        # Removes a tile from the rack (for example, when a tile is being played).
        self.rack.remove(tile)

    def get_rack_length(self):
        # Returns the number of tiles left in the rack.
        return len(self.rack)

    def replenish_rack(self):
        # Adds tiles to the rack after a turn such that the rack will have 7 tiles (assuming a proper number of tiles
        # in the bag).
        while self.get_rack_length() < 7 and self.bag.get_remaining_tiles() > 0:
            self.add_to_rack()


class Player:
    """
    Creates an instance of a player. Initializes the player's rack, and allows you to set/get a player name.
    """

    def __init__(self, bag):
        # Initializes a player instance. Creates the player's rack by creating an instance of that class.
        # Takes the bag as an argument, in order to create the rack.
        self.name = ""
        self.rack = Rack(bag)
        self.score = 0

    def set_name(self, name):
        # Sets the player's name.
        self.name = name

    def get_name(self):
        # Gets the player's name.
        return self.name

    def get_rack_str(self):
        # Returns the player's rack.
        return self.rack.get_rack_str()

    def get_rack_arr(self):
        # Returns the player's rack in the form of an array.
        return self.rack.get_rack_arr()

    def get_letters_from_rack_arr(self):
        # Returns the player's letters in array
        return self.rack.get_letters_from_rack_arr()

    def append_letter(self, tile):
        return self.rack.append_letter(tile)

    def increase_score(self, increase):
        # Increases the player's score by a certain amount. Takes the increase (int) as an argument and adds it to 
        # the score.
        self.score += increase

    def get_score(self):
        # Returns the player's score
        return self.score


class Board:
    """
    Creates the scrabble board.
    """

    def __init__(self):
        # Creates a 2-dimensional array that will serve as the board.
        self.board = [[None for _ in range(15)] for _ in range(15)]

    def get_board_array(self):
        # Returns the 2-dimensional board array.
        return self.board


class Word:
    def __init__(self, player, word, used_other_word):
        self.word = word.upper()
        self.player = player
        self.used_other_word = used_other_word

    def check_words(self):
        if gv.DICTIONARY is None:
            gv.DICTIONARY = open("dic.txt").read().splitlines()

        """If word not in dictionary"""
        if self.word not in gv.DICTIONARY:
            return False

        """If player use other word to create his word"""
        if not self.used_other_word and gv.BOARD.get_board_array()[7][7] is None:
            return False

        if gv.BOARD.get_board_array()[7][7] is None:
            contains_start_field = False
        else:
            contains_start_field = True

            """If word contains start field (8, 8)"""
            if not contains_start_field:
                return False

        return True

    def calculate_word_score(self):
        word_score = 0

        """If letter place in letter premium spot"""
        for letter in gv.ACTUAL_WORD_WITH_COORDS:
            if (letter.get_y(), letter.get_x()) in gv.TRIPLE_LETTER_SCORE:
                word_score += gv.LETTER_VALUES[letter.get_value()] * 3

            elif (letter.get_y(), letter.get_x()) in gv.DOUBLE_LETTER_SCORE:
                word_score += gv.LETTER_VALUES[letter.get_value()] * 2

            else:
                word_score += gv.LETTER_VALUES[letter.get_value()]

        """If letter place in word premium spot"""
        for letter in gv.ACTUAL_WORD_WITH_COORDS:
            if (letter.get_y(), letter.get_x()) in gv.TRIPLE_WORD_SCORE:
                word_score *= 3

            if (letter.get_y(), letter.get_x()) in gv.DOUBLE_WORD_SCORE:
                word_score *= 2

        self.player.increase_score(word_score)
        return word_score
