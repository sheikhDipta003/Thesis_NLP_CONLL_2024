# given an integer, return roman literals

def int_to_roman(num):
    # Define the Roman numeral symbols and their corresponding values
    roman_numerals = {
        1: 'I',
        4: 'IV',
        5: 'V',
        9: 'IX',
        10: 'X',
        40: 'XL',
        50: 'L',
        90: 'XC',
        100: 'C',
        400: 'CD',
        500: 'D',
        900: 'CM',
        1000: 'M'
    }
    result = ''
    # Iterate through the keys in reverse order
    for value in sorted(roman_numerals.keys(), reverse=True):
        # Repeat the Roman numeral symbol while the number is greater than or equal to the value
        while num >= value:
            result += roman_numerals[value]
            num -= value
    return result

# Example usage:
# print(int_to_roman(354))  # Output: CCCLIV


def roman_to_int(roman):
    # Define the mapping of Roman numeral symbols to their corresponding values
    roman_numerals = {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100,
        'D': 500,
        'M': 1000
    }
    result = 0
    prev_value = 0
    # Iterate over each character in the Roman numeral string in reverse order
    for symbol in reversed(roman):
        value = roman_numerals[symbol]
        # If the value of the current symbol is greater than or equal to the previous symbol, add it to the result
        if value >= prev_value:
            result += value
        # Otherwise, subtract it from the result
        else:
            result -= value
        prev_value = value
    return result

# Example usage:
# print(roman_to_int('XXIV'))  # Output: 24

import random

# generate random numbers to be used to choose sentences in the file
def prepareRandom(end_range, sample_size=40):
    # end_range: the number of lines in the training set
    # how many samples will be fetched
    start_range = 0
    rand_lines = {}
    kount = sample_size
    i=0
    while True:
      random_number = random.randint(start_range, end_range)
      if random_number in rand_lines:
        continue
      rand_lines[random_number] = random_number
      i = i+1
      # print(random_number);
      if (i==kount):
        break;

    return rand_lines;

def find_roman_answer(roman_dict, llm_answer):
    sorted_dict = dict(sorted(roman_dict.items(), key=lambda item: item[1], reverse=True))
    for key in sorted_dict:
      # print(f"Key: {key}, Value: {sorted_dict[key]}")
      if llm_answer.find(key) !=-1:
        return key
    return -1

