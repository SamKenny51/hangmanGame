import string
from bs4 import BeautifulSoup
import requests
import random
import re
import math
from collections import Counter

def fetchWord(word_length):
    """
    takes int argument: word_length
    returns str: word, dict: word_counter, str: definition
    """
    letters = list(string.ascii_lowercase)
    vowels = ['a','e','i','o','u']
    letters = [i + v for i in letters for v in vowels]

    # Create a word from consonant+vowel pairs
    word = ''
    for i in range(word_length):
        word += random.choice(letters)
    
    url = f'https://www.dictionary.com/misspelling?term={word}&s=t'
    response = requests.get(url)
        
    soup_word = BeautifulSoup(response.text, 'lxml')
    word = soup_word.find('h2', class_='spell-suggestions-subtitle css-6gthty e19m0k9k0').find('a').text
    word_counter = Counter(word)
    
    def_url = f'https://www.dictionary.com/browse/{word}'
    def_response = requests.get(def_url)
    soup_def = BeautifulSoup(def_response.text, 'lxml')
    definition = soup_def.find('span', class_='one-click-content css-1p89gle e1q3nk1v4').text

    return word, word_counter, definition

def blurDefinition(word, definition):
    """ regular expression to censor spoiler words """
    return re.sub(word,len(word)*"*", definition)

class Picture(object):

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
        for i in range(ySize-2):
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
        rstring = ''
        for line in self.picture:
            rstring += line
        return rstring

    def addText(self, text, xPos, yPos, justify="Left", wrap=False):
        '''
        Add text to picture at (xPos, yPos)
        TODO: include right and center justify options and wordwrap functionality
        '''
        words = text.split(' ')
        xPos_0 = xPos
        for word in words:
            if xPos + len(word) > self.xSize - self.right_margin:
                xPos = xPos_0
                yPos += 1
                if yPos == self.ySize - 2:
                    break
            if yPos <= len(self.picture):
                self.picture[yPos] = self.picture[yPos][:xPos] + word + " " + self.picture[yPos][(xPos+len(word)+1):]
                xPos += len(word) + 1
        
    def addLine(self, from_xPos, from_yPos, to_xPos, to_yPos, style):
        '''
        Add a line to picture starting at from 
        '''            
        if from_xPos == to_xPos:
            for yPos in range(from_yPos,to_yPos+1):
                self.addDot(from_xPos, yPos, '#')
        else:
            dx = to_xPos - from_xPos
            dy = to_yPos - from_yPos
            xStep = dx/math.sqrt(dx**2 + dy**2)
            yStep = dy/math.sqrt(dx**2 + dy**2)
            xPos, yPos = from_xPos, from_yPos
            while round(xPos) != to_xPos:
                #print(xPos, yPos)
                self.addDot(round(xPos), round(yPos), '#')
                xPos += xStep
                yPos += yStep
            self.addDot(round(xPos), round(yPos), '#')

    def addDot(self, xPos, yPos, style='#'):
        self.picture[yPos] = self.picture[yPos][:xPos] + style + self.picture[yPos][xPos+1:]

if __name__ == '__main__':
    pict = Picture(50,25)
    pict.addText("H A N G M A N", 3, 2)
    pict.addLine(0,16,49,16,'#')
    pict.addLine(25,0,25,16,'#')
    pict.addText("Incorrect Guesses", 28, 2)

    while True:
        
        word, word_counter, definition = fetchWord(4)
        blurred_def = blurDefinition(word, definition)
        hidden_word = "_ "*(len(word)-1) + "_"
        pict.addText(hidden_word, 3, 4)
        pict.addText("Hint: "+blurred_def,3,18)
        print(pict)
        
        nGuesses = 10
        incorrect = ''
        while nGuesses >= 1:
            player_letter = input("Pick a letter (a-z)! ")
            if len(player_letter) == 0:
                continue
            elif word_counter[player_letter[0].lower()] > 0:
                word_counter[player_letter] = 0
                i = 0
                for c in word:
                    if player_letter == c:
                        hidden_word = hidden_word[:i] + player_letter + hidden_word[(i+1):]
                    i += 2
                pict.addText(hidden_word, 3, 4)
            else:
                print("Wrong!")
                incorrect += player_letter + " "
                pict.addText(incorrect, 28, 4)
                nGuesses -= 1
                
            print(pict)
            if nGuesses == 0:
                print(f"Game Over! The word was {word}!")
                break

            if ''.join(hidden_word.split(" ")) == word:
                print("Well done! You win!")
                break

        playAgain = input("Would you like to play again? (y/n) ")
        if playAgain != 'y':
            break
        
        pict.addText(len(hidden_word)*" ", 3, 4)
        pict.addText("Hint: "+len(blurred_def)*" ", 3,18)
        pict.addText(len(blurred_def)*" ", 3,19)
        pict.addText(len(blurred_def)*" ", 3,20)
        pict.addText(len(incorrect)*" ", 28,4)
