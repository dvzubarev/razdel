#!/usr/bin/env python3

import enum

from razdel.rule import JOIN, FunctionRule
from razdel.substring import Substring

from .punct import DASHES, APOSTROPHES

from .base import (
    safe_next,
    Segmenter,
    DebugSegmenter
)

from .common_tokenize import (
    Atom,
    TokenSplitter,
    TokenSplit,
    Rule2112,
    COMMON_RULES,
    DOMAIN
)

from .en_support import (
    en_postproc,
    EN_RULES
)

########
#
#  RU specific rules
#
########

def ru_hyphen_complex_cases(split:TokenSplit):
    # 'Кот-д’Ивуар'
    if (split.left_1.normal == 'кот'
        and split.right in DASHES
        and split.right_2 and split.right_2.normal == 'д'
        and split.right_3 and split.right_3.text in APOSTROPHES
        ):
        return JOIN
    if (split.left_2 and split.left_2.normal == 'кот'
        and split.left in DASHES
        and split.right_1.normal == 'д'
        and split.right_2 and split.right_2.text in APOSTROPHES):
        return JOIN


class AdjHyphenRule(Rule2112):
    name = "ru_adj_hyphen"
    def __init__(self) -> None:
        super().__init__()

        self._adj_3_suffixes = {
            "его",
            "ему",
            "ими",
            "ому",
            "ого",
            "ыми",
        }
        self._adj_2_suffixes = {
            "ая",
            "ее",
            "ей",
            "ем",
            "ие",
            "ий",
            "им",
            "их",
            "ое",
            "ой",
            "ом",
            "ую",
            "ый",
            "ые",
            "ым",
            "ых",

        }

    def delimiter(self, delimiter):
        return delimiter in DASHES

    def rule(self, left:Atom, right:Atom):
        if ((left.normal == 'сине' or left.normal[-1] == 'о')
            and (len(right.normal) > 5 and right.normal[-3:] in self._adj_3_suffixes
                 or
                 len(right.normal) > 4 and right.normal[-2:] in self._adj_2_suffixes)
            ):
            return JOIN


class HyphenAbbrevsRule(Rule2112):
    name = "ru_hyphen_abbr"
    def __init__(self) -> None:
        super().__init__()

        self._abbrevs = {
            ("кол", "во"),
            ("р", "н"),
            ("гр", "н"),
            ("пр", "кт"),
            ("ун", "т"),
            ("изд", "во"),
            ("хоз", "во"),
        }

    def delimiter(self, delimiter):
        return delimiter in DASHES

    def rule(self, left:Atom, right:Atom):
        words = (left.normal, right.normal)
        if words in self._abbrevs:
            return JOIN

class HyphenAuxWords(Rule2112):
    name = "ru_hyphen_aux"
    def __init__(self) -> None:
        super().__init__()

        self._aux_words = {
            "эль",
            "эш",
            "о",
            "au"
        }

    def delimiter(self, delimiter):
        return delimiter in DASHES

    def rule(self, left:Atom, right:Atom):
        if left.normal in self._aux_words and right.text.istitle():
            return JOIN
        if right.normal in self._aux_words and left.text.istitle():
            return JOIN

########
#
#   SEGMENT
#
########

RU_RULES = [
    FunctionRule(ru_hyphen_complex_cases),
    AdjHyphenRule(),
    HyphenAbbrevsRule(),
    HyphenAuxWords()

]


RULES = RU_RULES + EN_RULES + COMMON_RULES


class TokenType(enum.IntEnum):
    RU     = 0
    LAT    = 1
    INT    = 2
    PUNCT  = 3
    URI    = 4
    DOI    = 5
    DOMAIN = 6
    EMAIL  = 7
    OTHER  = 8
    UNK    = 127

def token_type_from_atom(atom_type:str):
    if atom_type == DOMAIN:
        atom_type = 'DOMAIN'
    try:
        return TokenType[atom_type]
    except KeyError:
        return TokenType.UNK


class Token(Substring):
    __attributes__ = Substring.__attributes__ + ['token_type']
    def __init__(self, start, stop, text, token_type):
        super().__init__(start, stop, text)
        self.token_type = token_type




class TokenSegmenter(Segmenter):
    def __init__(self, split=TokenSplitter(), rules=RULES):
        super().__init__(split, rules)

    def segment(self, parts):
        #first time parts yields texts of the first atom
        t = safe_next(parts)
        if t is None:
            return
        buffer, atom_type = t

        for split in parts:
            #current atom is in right_1 of the split

            #it the the text of the current atom
            right, next_atom_type = next(parts)
            split.buffer = buffer
            if not split.delimiter and self.join(split):
                buffer += right
                #Merging of multiple atoms makes the original atom type not
                #relevant. It would be great if join returns new atom type but
                #for now just keep type of the first atom.
            else:
                yield buffer, atom_type
                buffer = right
                atom_type = next_atom_type
        yield buffer, atom_type

    def post(self, chunks):
        chunks = en_postproc(chunks)
        yield from chunks

    def __call__(self, text):
        parts = self.split(text)
        chunks = self.segment(parts)
        chunks = self.post(chunks)

        offset = 0
        for token_text, atom_type in chunks:
            start = text.find(token_text, offset)
            stop = start + len(token_text)
            yield Token(start, stop, token_text, token_type_from_atom(atom_type))
            offset = stop


    @property
    def debug(self):
        return DebugTokenSegmenter()


class DebugTokenSegmenter(TokenSegmenter, DebugSegmenter):
    pass


tokenize = TokenSegmenter()
