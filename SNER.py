#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string, re

import telnetlib


def get_NEs(text):
    """
    Sends a string to a local Stanford NER Tagger
    http://www-nlp.stanford.edu/software/CRF-NER.shtml

    Returns a list of dictionaries of recognized entities,
    together with a list of their occurrences in the text.

    entities = [{"normalized": "Stanford", 
                 "type":"Location", 
                 "occurrences": ["start": 10
                                 "end": 18]
                 }, 
                 {...}
                ]

    """


    text = text.encode("utf-8")

    tncon = telnetlib.Telnet("127.0.0.1", "9191")
    tncon.write(bytes(text+"\n"))
    tokens = tncon.read_all().split()
    # tokens is a list of tokens like ["word/PERSON", "word/O", "word/LOCATION"]

    #creates a list of tuples from tokens like [("word", "PERSON"), ...]
    tokens = [tuple(token.split("/")) for token in tokens]

    #recreates tupleslist without tokens like ("?", "O", "word", "O",...)
    tokens = [token for token in tokens if token[1] != "O" and token[0] not in string.punctuation]

    persons = [token[0] for token in tokens if token [1] == "PERSON"]
    organizations = [token[0] for token in tokens if token [1] == "ORGANIZATION"]
    locations = [token[0] for token in tokens if token [1] == "LOCATION"]

    entities = []

    if persons:
        entities.extend(loop_over_ngrams(persons, "Person", text))

    if organizations:
        entities.extend(loop_over_ngrams(organizations, "Organization", text))

    if locations:
        entities.extend(loop_over_ngrams(locations, "Location", text))

    # get all occurrences for all entities
    if entities:
        entities = sorted(entities, key=lambda item: item["occurrences"][0]["start"])

    return entities



def create_ngrams(tokens, n):
    ngramslist = []
    for i in range(len(tokens)-n+1):
        ngramslist.append(" ".join(tokens[i:i+n]))
    return ngramslist


def loop_over_ngrams(tokens, tokentype, text):
    """
    Creates entities of length up to four out of found entities,
    and searches for them first, e.g. Federal Reserve Bank.
    If an entity like Federal Reserve exists, it will not be 
    searched for separately.
    """

    def find_tokens(ngrams):
        for ngram in ngrams:
            check = 0
            if tokens_found:
                for tf in tokens_found:
                    if ngram in tf:
                        check += 1
                if check == 0:
                    find_occurrences(ngram)
            else:
                find_occurrences(ngram)


    def find_occurrences(gram):
        occurrences = [{"start":m.start(0), "end":m.end(0)} 
                                    for m in re.finditer(gram, text)]
        if occurrences:
            ngram_entities.append({"normalized": gram,
                                "type": tokentype,
                                "occurrences": occurrences})
            tokens_found.add(gram)


    ngram_entities = []
    tokens_found = set()

    fourgrams = create_ngrams(tokens, 4)
    trigrams = create_ngrams(tokens, 3)
    bigrams = create_ngrams(tokens, 2)

    find_tokens(fourgrams)
    find_tokens(trigrams)
    find_tokens(bigrams)
    find_tokens(tokens)


    return ngram_entities
