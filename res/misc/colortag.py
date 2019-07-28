#!/usr/bin/env python

import re

'''
string = "This is a <!red>testing</> string. Also, this one here is a <!yellow>redundant, crazy string with multiple " \
         "words.</> Wait, needed <!green>an extra string for debugging.</> Yep, that <!red>broke everything.</> Oh, " \
         "here's <!magenta>ANOTHER FREAKIN' ONE</> just for fun. <!blue>What even is this, anyway?</>"
'''


def decode(string, default_color="white"):
    regex_dict = []
    all_words = []
    colored_words = []
    compiled = []

    regex = re.findall('<!(\w+)>(.*?)</>', string, re.MULTILINE)
    index = 0
    for find in regex:
        for colored_word in find[1].split():
            check = string.find(colored_word, index)
            regex_dict.append([colored_word, find[0], check])
            index = check

    i = 0
    for match in re.finditer('<!(\w+)>(.*?)</>', string, re.MULTILINE):
        # print(match.span(), match.group().split())
        for word in match.group().split():
            color = regex_dict[i][1]
            cleaned_word = regex_dict[i][0]
            colored_words.append([cleaned_word, color, string.find(word, int(match.span()[0]))])
            i += 1

    index = 0
    for word in string.split():
        check = string.find(word, index)
        all_words.append([word, default_color, check])
        index = check

    for a in all_words:
        redundant = False
        for c in colored_words:
            if a[2] == c[2]:
                compiled.append([c[0], c[1]])
                redundant = True
        if not redundant:
            compiled.append([a[0], default_color])

    ''' Testing, ignore these '''
    # print(compiled)
    # for word in compiled:
    #     tc.cprint(word[0], word[1], end=" ")

    return compiled


if __name__ == '__main__':
    decode()

