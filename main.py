import sentence_analyzer
from sentence_analyzer import *
from verb_scanner import find_verb_details


if __name__ == '__main__':
    text = 'من کتابم را به کتابخانه خواهم برد.'
    extracted_info = sentence_analyzer.analyze(text)
    for key in extracted_info:
        print(key, extracted_info[key])
