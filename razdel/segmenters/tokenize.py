#!/usr/bin/env python3


from razdel.rule import JOIN, FunctionRule

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
    COMMON_RULES
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

def ru_hyphen_specific_rules(split:TokenSplit):
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



########
#
#   SEGMENT
#
########

RU_RULES = [
    FunctionRule(ru_hyphen_specific_rules),
    AdjHyphenRule(),

]


RULES = RU_RULES + EN_RULES + COMMON_RULES


class TokenSegmenter(Segmenter):
    def __init__(self, split=TokenSplitter(), rules=RULES):
        super().__init__(split, rules)

    def segment(self, parts):
        buffer = safe_next(parts)
        if buffer is None:
            return

        for split in parts:
            right = next(parts)
            split.buffer = buffer
            if not split.delimiter and self.join(split):
                buffer += right
            else:
                yield buffer
                buffer = right
        yield buffer

    def post(self, chunks):
        chunks = en_postproc(chunks)
        yield from chunks

    @property
    def debug(self):
        return DebugTokenSegmenter()


class DebugTokenSegmenter(TokenSegmenter, DebugSegmenter):
    pass


tokenize = TokenSegmenter()
