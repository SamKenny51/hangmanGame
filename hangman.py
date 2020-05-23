""" DOCSTRING: A Simple Text-based Hangman Game """

import string
import random
import re
import math
from collections import Counter
from bs4 import BeautifulSoup
import requests

def fetch_word(word_length):
    """
    takes int argument: word_length
    returns str: word, dict: word_counter, str: definition
    """
    _letters = list(string.ascii_lowercase)
    _vowels = ['a', 'e', 'i', 'o', 'u']
    _letters = [i + v for i in _letters for v in _vowels]

    # Create a word from consonant+vowel pairs
    _word = ''.join([random.choice(_letters) for _ in range(word_length)])

    _url = f'https://www.dictionary.com/misspelling?term={_word}&s=t'
    _response = requests.get(_url)

    _soup_word = BeautifulSoup(_response.text, 'lxml')
    _sug_head = _soup_word.find('h2', class_='spell-suggestions-subtitle css-6gthty e19m0k9k0')
    _word = _sug_head.find('a').text
    _word_counter = Counter(_word)

    _def_url = f'https://www.dictionary.com/browse/{_word}'
    _def_response = requests.get(_def_url)
    _soup_def = BeautifulSoup(_def_response.text, 'lxml')
    _definition = _soup_def.find('span', class_='one-click-content css-1p89gle e1q3nk1v4').text

    return _word, _word_counter, _definition

def blur_definition(_word, _definition):
    """ regular expression to censor spoiler words """
    _new_def = re.sub(word, len(word)*"*", definition)
    if _word[-1] == 'd':
        _new_def = re.sub(_word[:-1], (len(_word)-1)*"*", _new_def)
    if _word[-1] == 'y':
        _new_def = re.sub(_word[:-1], (len(_word)-1)*"*", _new_def)
    if _word[-2:] == 'ly':
        _new_def = re.sub(_word[:-2], (len(_word)-2)*"*", _new_def)
    if _word[-2:] == 'er':
        _new_def = re.sub(_word[:-1], (len(_word)-2)*"*", _new_def)
    return _new_def

def create_hidden_string(_word, _char_set):
    """ Create a censored version of word """
    _new_string = ''
    for _c in _word:
        if _c in _char_set:
            _new_string += '_ '
        else:
            _new_string += _c + ' '
    return _new_string[:-1]

class Picture:
    '''
    A simple class for making text user interfaces
    '''
    def __init__(self, xSize=50, ySize=50, style='#'):
        '''
        Picture Class constructor
        Creates picture of dimensions xSize * ySize with style string as a border
        '''
        if xSize < 2:
            self.xSize = 2
        else:
            self.xSize = xSize
        if ySize < 2:
            self.ySize = 2
        else:
            self.ySize = ySize

        self.picture = [xSize * style + '\n']
        for _ in range(ySize-2):
            self.picture.append(style + ' ' * (xSize-2) + style  + '\n')
        self.picture.append(xSize * style)
        self.top_margin = 2
        self.left_margin = 3
        self.right_margin = 3

    def __str__(self):
        '''
        String representation of Picture Object
        Printed to screen when print( Picture ) is called
        '''
        return ''.join(self.picture)

    def add_text(self, text, xPos, yPos):
        '''
        Add text to picture at (xPos, yPos)
        TODO: include right and center justify options and wordwrap functionality
        '''
        _words = text.split(' ')
        xPos_0 = xPos
        for _word in _words:
            if xPos + len(_word) > self.xSize - self.right_margin:
                xPos = xPos_0
                yPos += 1
                if yPos == self.ySize - 2:
                    break
            if yPos <= len(self.picture):
                self.picture[yPos] = (self.picture[yPos][:xPos] + _word + " " +
                                      self.picture[yPos][(xPos+len(_word)+1):])
                xPos += len(_word) + 1

    def add_line(self, from_xPos, from_yPos, to_xPos, to_yPos, style='#'):
        '''
        Add a line to picture starting at from
        '''
        if from_xPos == to_xPos:
            for yPos in range(from_yPos, to_yPos+1):
                self.add_dot(from_xPos, yPos, style)
        else:
            dx = to_xPos - from_xPos
            dy = to_yPos - from_yPos
            xStep = dx/math.sqrt(dx**2 + dy**2)
            yStep = dy/math.sqrt(dx**2 + dy**2)
            xPos, yPos = from_xPos, from_yPos
            while round(xPos) != to_xPos:
                #print(xPos, yPos)
                self.add_dot(round(xPos), round(yPos), style)
                xPos += xStep
                yPos += yStep
            self.add_dot(round(xPos), round(yPos), style)

    def add_dot(self, xPos, yPos, style='#'):
        '''
        Add a single dot based on style to the Picture interface at (xPos,yPos)
        '''
        self.picture[yPos] = self.picture[yPos][:xPos] + style + self.picture[yPos][xPos+1:]

if __name__ == '__main__':
    char_set = [chr(i+97) for i in range(26)]
    pict = Picture(50, 25)
    pict.add_text("H A N G M A N", 3, 2)
    pict.add_line(0, 16, 49, 16, '#')
    pict.add_line(25, 0, 25, 16, '#')
    pict.add_text("Incorrect Guesses", 28, 2)

    while True:
        word, word_counter, definition = fetch_word(4)
        blurred_def = blur_definition(word, definition.lower())
        hidden_word = create_hidden_string(word, char_set)
        pict.add_text(hidden_word, 3, 4)
        pict.add_text("Hint: "+blurred_def, 3, 18)
        print(pict)

        NGUESSES = 10
        INCORRECT = ''
        while NGUESSES >= 1:
            player_letter = input("Pick a letter (a-z)! ")
            if len(player_letter) == 0 or player_letter not in char_set:
                continue

            if word_counter[player_letter[0].lower()] > 0:
                word_counter[player_letter] = 0
                i = 0
                for c in word:
                    if player_letter == c:
                        hidden_word = hidden_word[:i] + player_letter + hidden_word[(i+1):]
                    i += 2
                pict.add_text(hidden_word, 3, 4)
            else:
                print("Wrong!")
                INCORRECT += player_letter + " "
                pict.add_text(INCORRECT, 28, 4)
                NGUESSES -= 1

            print(pict)
            if NGUESSES == 0:
                print(f"Game Over! The word was {word}!")
                break

            if ''.join(hidden_word.split(" ")) == word:
                print("Well done! You win!")
                break

        playAgain = input("Would you like to play again? (y/n) ")
        if playAgain != 'y':
            break

        pict.add_text(len(hidden_word)*" ", 3, 4)
        pict.add_text("Hint: "+len(blurred_def)*" ", 3, 18)
        pict.add_text(len(blurred_def)*" ", 3, 19)
        pict.add_text(len(blurred_def)*" ", 3, 20)
        pict.add_text(len(INCORRECT)*" ", 28, 4)
