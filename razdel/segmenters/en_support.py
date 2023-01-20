#!/usr/bin/env python3

import copy

from razdel.rule import JOIN, Rule
from .common_tokenize import (
    APOSTROPHES,
    Rule2112,
    TokenSplit,
    INT
)

_SPECIAL_EN_TOKENS_BASE = {
    "can't": ["ca", "n't"],
    "cannot": ["can", "not"],
    "didn't": ["did", "n't"],
    "don't": ["do", "n't"],
    "doesn't": ["does", "n't"],
    "won't": ["wo", "n't"],
    "haven't" : ["have", "n't"],
    "hasn't" : ["has", "n't"],
    "hadn't" : ["had", "n't"],
    "isn't": ["is", "n't"],
    "wasn't": ["was", "n't"],
    "aren't": ["are", "n't"],
    "ain't": ["ai", "n't"],
    "weren't": ["were", "n't"],
    "couldn't" : ["could", "n't"],
    "shouldn't": ["should", "n't"],
    "wouldn't": ["would", "n't"],
    "youll": ["you", "ll"],
    "thats": ["that", "s"],
    "theres": ["there", "s"],
    "im": ["i", "m"],
    "ive": ["i", "ve"],
    "hes": ["he", "s"],
    "youre": ["you", "re"],
    "ur": ["u", "r"],
    "wanna": ["wan", "na"],
    "gonna": ["gon", "na"],
    "gotta": ["got", "ta"],
    "outta": ["out", "ta"],
    "sorta": ["sort", "a"],
    # "kinda" is not split in UD_English_(GUM|EWT)
}


_SPECIAL_EN_TOKENS = None
_SPECIAL_EN_PREFIXES = None


def _enhance_special_tokens(token_pairs):
    variants = [("'", ""), ("'", "’")]
    new_variants_dict = {}
    for token, split in token_pairs.items():
        if "'" in token:
            for char, replacee in variants:
                new_split =  [s.replace(char, replacee) for s in split]
                new_variants_dict[token.replace(char, replacee)] = new_split

    return new_variants_dict

def _get_special_en_tokens():
    global _SPECIAL_EN_TOKENS
    if _SPECIAL_EN_TOKENS is None:
        _SPECIAL_EN_TOKENS = copy.copy(_SPECIAL_EN_TOKENS_BASE)
        _SPECIAL_EN_TOKENS.update(_enhance_special_tokens(_SPECIAL_EN_TOKENS_BASE))

    return _SPECIAL_EN_TOKENS

def _get_specian_en_prefixes():
    global _SPECIAL_EN_PREFIXES
    if _SPECIAL_EN_PREFIXES is None:
        temp = []
        for key in _SPECIAL_EN_TOKENS_BASE:
            idx = key.find("'")
            if idx == -1:
                continue
            temp.append(key[:idx])
        _SPECIAL_EN_PREFIXES = frozenset(temp)
    return _SPECIAL_EN_PREFIXES

    




    

class ApostropheRule(Rule2112):
    name = 'apostrophe'

    def delimiter(self, delimiter):
        return delimiter in APOSTROPHES

    def rule(self, left, right):
        if left.normal in _get_specian_en_prefixes() and right.normal == 't':
            #split it later in postproc
            return JOIN


class ApostropheRightJoinRule(Rule):
    def __call__(self, split):
        if split.left in APOSTROPHES:
            if split.right_1.normal in ('s', 'll', 'm', 'd', 've', 're'):
                return JOIN


class OrdinalNumbers(Rule):
    def __call__(self, split:TokenSplit):
        if split.left_1.type == INT and split.right in ('st', 'nd', 'rd', 'th'):
            return JOIN
        if (split.left_1.type == INT
            and split.right == 's'
            and (len(split.left) == 4 and split.left[:2] in ('19, 20')
                 or len(split.left) == 2  and split.left[1] == '0')):
            return JOIN




EN_RULES = [
    ApostropheRule(),
    ApostropheRightJoinRule(),
    OrdinalNumbers()
]


def en_postproc(chunks):
    en_split_rules_dict = _get_special_en_tokens()

    for chunk in chunks:
        lower_chunk = chunk.lower()
        if (split := en_split_rules_dict.get(lower_chunk)):
            assert len(split) == 2, f"{len(split)} split len is unsupported"
            split_point = len(split[0])
            yield chunk[:split_point]
            yield chunk[split_point:]
        else:
            yield chunk
