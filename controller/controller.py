from model.model import Board, Bag, Player, Letter, Word
from config import global_variables as gv


def get_player_index():
    player_index = gv.ROUND_NUMBER - 1
    while True:
        if player_index < len(gv.PLAYERS):
            break
        else:
            player_index -= len(gv.PLAYERS)
    return player_index


def start_game():
    """Function that start the game"""
    gv.BOARD = Board()
    gv.BAG = Bag()
    for i in range(gv.NUMBER_OF_PLAYERS):
        gv.PLAYERS.append(Player(gv.BAG))
        gv.PLAYERS[i].set_name(gv.PLAYERS_NICKNAMES[i])


def turn(player):
    """if is true direction of word is horizontal, else direction is vertical"""
    direction_horizontal = True
    used_other_word = False
    word_to_play = ''
    temp_actual_word_with_coords = ''
    new_word = ''
    break_letters = ''

    if not gv.ACTUAL_WORD_WITH_COORDS:
        return 0

    if (gv.SKIPPED_TURNS < 6) or (player.rack.get_rack_length() == 0 and gv.BAG.get_remaining_tiles() == 0):

        """if user place only one letter and attach to board letters"""
        if len(gv.ACTUAL_WORD_WITH_COORDS) == 1:
            y = gv.ACTUAL_WORD_WITH_COORDS[0].get_y()
            x = gv.ACTUAL_WORD_WITH_COORDS[0].get_x()
            if_get_letter = False

            if y != 14 and not if_get_letter:
                if gv.BOARD.get_board_array()[y + 1][x] is not None:
                    """If connect to the letter on the top"""
                    gv.ACTUAL_WORD_WITH_COORDS.append(gv.BOARD.get_board_array()[y + 1][x])
                    if_get_letter = True
            if y != 0 and not if_get_letter:
                if gv.BOARD.get_board_array()[y - 1][x] is not None:
                    """If connect to the letter on the bottom"""
                    gv.ACTUAL_WORD_WITH_COORDS.append(gv.BOARD.get_board_array()[y - 1][x])
                    if_get_letter = True
            if x != 14 and not if_get_letter:
                if gv.BOARD.get_board_array()[y][x + 1] is not None:
                    """If connect to the letter on the right"""
                    gv.ACTUAL_WORD_WITH_COORDS.append(gv.BOARD.get_board_array()[y][x + 1])
                    """If connect to the letter on the left"""
                    if_get_letter = True
            if x != 0 and not if_get_letter:
                if gv.BOARD.get_board_array()[y][x - 1] is not None:
                    gv.ACTUAL_WORD_WITH_COORDS.append(gv.BOARD.get_board_array()[y][x - 1])
                    if_get_letter = True
            if not if_get_letter:
                """The letter doesn't connect with anything"""
                return 0

        if gv.ACTUAL_WORD_WITH_COORDS[0].get_x() == gv.ACTUAL_WORD_WITH_COORDS[1].get_x():
            direction_horizontal = False
        elif gv.ACTUAL_WORD_WITH_COORDS[0].get_y() == gv.ACTUAL_WORD_WITH_COORDS[1].get_y():
            direction_horizontal = True
        else:
            """not valid word"""
            return 0

        """Check all letters if they are in one line"""
        if direction_horizontal:
            row_num = gv.ACTUAL_WORD_WITH_COORDS[0].get_y()
            for letter in gv.ACTUAL_WORD_WITH_COORDS:
                if not letter.get_y() == row_num:
                    return 0
        else:
            col_num = gv.ACTUAL_WORD_WITH_COORDS[0].get_x()
            for letter in gv.ACTUAL_WORD_WITH_COORDS:
                if not letter.get_x() == col_num:
                    return 0

        if direction_horizontal:
            """word in horizontal direction"""

            """Sort letters by x-coordinate"""
            gv.ACTUAL_WORD_WITH_COORDS.sort(key=lambda letter: letter.get_x())
            row_number = gv.ACTUAL_WORD_WITH_COORDS[0].get_y()

            temp_actual_word_with_coords = gv.ACTUAL_WORD_WITH_COORDS.copy()
            """Check if letters that user placed stand next to each other"""
            for l, letter_in_word in enumerate(temp_actual_word_with_coords):

                """if it is a last user letter"""
                if l == len(temp_actual_word_with_coords) - 1:
                    word_to_play += letter_in_word.get_value()

                elif letter_in_word.get_x() + 1 != gv.ACTUAL_WORD_WITH_COORDS[l + 1].get_x():
                    """
                    If they are not next to each other, check if the user used a letter that is already on the board
                    """

                    index_before_break = letter_in_word.get_x()
                    index_after_break = temp_actual_word_with_coords[l + 1].get_x()

                    """Iterates over a break"""
                    break_letters = ''
                    for j in range(index_before_break + 1, index_after_break):

                        """Check if something place in break is between letters"""
                        if gv.BOARD.get_board_array()[row_number][j] is not None:
                            break_letters += gv.BOARD.get_board_array()[row_number][j].get_value()
                            gv.ACTUAL_WORD_WITH_COORDS.append(
                                Letter(row_number, j, gv.BOARD.get_board_array()[row_number][j].get_value())
                            )
                        else:
                            """Lack of continuity. INVALID WORD"""
                            return 0

                    """Combine user letters with letters on the board"""
                    new_word = word_to_play + break_letters + letter_in_word.get_value()
                    word_to_play = new_word
                    used_other_word = True

                    """letter is not last and dont have break, common case"""
                else:
                    word_to_play += letter_in_word.get_value()

            """Check if user used letters from board at start or end of his word"""
            first_coordinate = temp_actual_word_with_coords[0].get_x()
            last_coordinate = temp_actual_word_with_coords[-1].get_x()

            """if additional letter at start of his word"""
            i = 1
            if first_coordinate > 0:
                while True:
                    if gv.BOARD.get_board_array()[row_number][first_coordinate - i] is not None:
                        word_to_play = gv.BOARD.get_board_array()[row_number][
                                           first_coordinate - i].get_value() + word_to_play
                        gv.ACTUAL_WORD_WITH_COORDS.append(
                            Letter(
                                row_number,
                                first_coordinate - i,
                                gv.BOARD.get_board_array()[row_number][first_coordinate - i].get_value()
                            )
                        )
                        used_other_word = True
                        i += 1
                    else:
                        break

            """If additional letter at end of his word"""
            i = 1
            if last_coordinate < 14:
                while True:
                    if gv.BOARD.get_board_array()[row_number][last_coordinate + i] is not None:
                        word_to_play = word_to_play + gv.BOARD.get_board_array()[row_number][
                            last_coordinate + i].get_value()

                        gv.ACTUAL_WORD_WITH_COORDS.append(
                            Letter(
                                row_number,
                                last_coordinate + i,
                                gv.BOARD.get_board_array()[row_number][last_coordinate + i].get_value()
                            )
                        )
                        used_other_word = True
                        i += 1
                    else:
                        break
                gv.ACTUAL_WORD_WITH_COORDS.sort(key=lambda letter: letter.get_x())

        else:
            """word in vertical direction"""

            """Sort letters by y-coordinate"""
            gv.ACTUAL_WORD_WITH_COORDS.sort(key=lambda letter: letter.get_y())
            col_number = gv.ACTUAL_WORD_WITH_COORDS[0].get_x()

            temp_actual_word_with_coords = gv.ACTUAL_WORD_WITH_COORDS.copy()
            """Check if letters that user placed stand next to each other"""
            for l, letter_in_word in enumerate(temp_actual_word_with_coords):

                """if it is a last user letter"""
                if l == len(temp_actual_word_with_coords) - 1:
                    word_to_play += letter_in_word.get_value()

                elif letter_in_word.get_y() + 1 != temp_actual_word_with_coords[l + 1].get_y():
                    """
                    If they are not next to each other, check if the user used a letter that is already on the board
                    """

                    index_before_break = letter_in_word.get_y()
                    index_after_break = temp_actual_word_with_coords[l + 1].get_y()

                    """Iterates over a break"""
                    break_letters = ''
                    for j in range(index_before_break + 1, index_after_break):

                        """Check if something place in break is between letters"""
                        if gv.BOARD.get_board_array()[j][col_number] is not None:
                            break_letters += gv.BOARD.get_board_array()[j][col_number].get_value()
                            gv.ACTUAL_WORD_WITH_COORDS.append(
                                Letter(j, col_number, gv.BOARD.get_board_array()[j][col_number].get_value())
                            )
                        else:
                            """Lack of continuity. INVALID WORD"""  # TODO check
                            return 0

                    """Combine user letters with letters on the board"""
                    new_word = word_to_play + break_letters + letter_in_word.get_value()
                    word_to_play = new_word
                    used_other_word = True

                    """letter is not last and dont have break, common case"""
                else:
                    word_to_play += letter_in_word.get_value()

            """Check if user used letters from board at start or end of his word"""
            first_coordinate = temp_actual_word_with_coords[0].get_y()
            last_coordinate = temp_actual_word_with_coords[-1].get_y()

            """if additional letter at start of his word"""
            i = 1
            if first_coordinate > 0:
                while True:
                    if gv.BOARD.get_board_array()[first_coordinate - i][col_number] is not None:
                        word_to_play = gv.BOARD.get_board_array()[first_coordinate - i][
                                           col_number].get_value() + word_to_play
                        gv.ACTUAL_WORD_WITH_COORDS.append(
                            Letter(
                                first_coordinate - i,
                                col_number,
                                gv.BOARD.get_board_array()[first_coordinate - i][col_number].get_value()
                            )
                        )
                        used_other_word = True
                        i += 1
                    else:
                        break

            """If additional letter at end of his word"""
            i = 1
            if last_coordinate < 14:
                while True:
                    if gv.BOARD.get_board_array()[last_coordinate + i][col_number] is not None:
                        word_to_play = word_to_play + gv.BOARD.get_board_array()[last_coordinate + i][
                            col_number].get_value()
                        gv.ACTUAL_WORD_WITH_COORDS.append(
                            Letter(
                                last_coordinate + i,
                                col_number,
                                gv.BOARD.get_board_array()[last_coordinate + i][col_number].get_value()
                            )
                        )
                        used_other_word = True
                        i += 1
                    else:
                        break
            gv.ACTUAL_WORD_WITH_COORDS.sort(key=lambda letter: letter.get_y())

        """Initialize word"""
        word = Word(player, word_to_play, used_other_word)

        """If word is correct then points are added"""
        if word.check_words():
            word_score = word.calculate_word_score()
            return word_score
        return 0
