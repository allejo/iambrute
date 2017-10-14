#!/usr/bin/env python2

from pycipher import Caesar, ColTrans
from collections import OrderedDict
from itertools import permutations

import os
import re
import string

CIPHER  = 'HUKUUEUUYREUYYKGRRGNZZKXNGNOLKXTSAQNZYEGNZTRGTOYALSSEHSYGRVSOOLEGIKVKNZOEJYXT'

# Frequencies of letters in the English language
#  A -> ENGLISH[0]
#  Z -> ENGLISH[25]
ENGLISH = (0.0749, 0.0129, 0.0354, 0.0362, 0.1400, 0.0218, 0.0174, 0.0422,
           0.0665, 0.0027, 0.0047, 0.0357, 0.0339, 0.0674, 0.0737, 0.0243,
           0.0026, 0.0614, 0.0695, 0.0985, 0.0300, 0.0116, 0.0169, 0.0028,
           0.0164, 0.0004)

def letter_frequency(text):
    # For ease, remove all non-letter characters and convert it to lowercase for consistency.
    text = re.sub('[^a-z]', '', text.lower())

    # A dictionary to keep count of how many times each letter is used inside of `text`. They key will be the letter
    # being counted.
    alphabetCount = dict([(c,0) for c in string.lowercase])

    # Cast to float
    totalLetters = len(text) * 1.0

    for char in text:
        alphabetCount[char] += 1

    # Convert the dictionary to a list of items and sort them by the letter
    textLetterCount = alphabetCount.items()
    textLetterCount.sort()

    # Calculate the amount of times the letter has appeared in relation to the cipher's length
    return [ count/totalLetters for (letter,count) in textLetterCount ]

def frequency_delta(source, dest):
    N = 0.0

    for f1, f2 in zip(source, dest):
        N += abs(f1 - f2)

    return N

def decipher_caesar(cipher):
    lowestDelta = 1000 # A ridiculously large initial delta in order to ensure a new lowest delta
    bestRotation = 0
    letterFrequencies = letter_frequency(cipher)

    for shift in range(26):
        currentDelta = frequency_delta(letterFrequencies[shift:] + letterFrequencies[:shift], ENGLISH)

        if currentDelta < lowestDelta:
            lowestDelta = currentDelta
            bestRotation = shift

    return {
        'rotation': bestRotation,
        'plain_text': Caesar(bestRotation).decipher(cipher)
    }

def brute_columnar_transposition(text, keyword):
    possible_orders = permutations(keyword)
    columnPositions = {}

    for order in possible_orders:
        key = ''.join(order)
        columnPositions[key] = ColTrans(key).decipher(text)

    return columnPositions

def build_dictionary():
    with open('10k-english.txt', 'r') as dict_file:
        return dict_file.read().split()

def dictionary_attack(permutations, words, output = 'iambrute.txt'):
    results = {}

    for cols, string in permutations.iteritems():
        results[string] = {
            'cols': cols,
            'words': []
        }

        for _word in words:
            word = _word.strip().upper()

            if len(word) < 3:
                continue

            if word in string:
                results[string]['words'].append(word)

    sortedResults = OrderedDict(sorted(
        results.iteritems(),
        key=lambda x: len(x[1]['words']),
        reverse=True
    ))

    with open(output, 'w') as data_file:
        for k in sortedResults:
            line = "{}: [{}]\n".format(
                ', '.join([ sortedResults[k]['cols'], k ]),
                ', '.join(sortedResults[k]['words'])
            )
            data_file.write(line)

    return results

if __name__ == '__main__':
    break_caesar = decipher_caesar(CIPHER)

    print('Caesar offset: {}'.format(break_caesar['rotation']))
    print('Caesar deciphered: {}'.format(break_caesar['plain_text']))

    permutations = brute_columnar_transposition(break_caesar['plain_text'], '01234567')
    dictionary = build_dictionary()

    dictionary_attack(permutations, dictionary)
