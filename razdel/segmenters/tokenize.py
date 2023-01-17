#!/usr/bin/env python3

from .en_support import (
    en_postproc,
    EN_RULES
)

from .base import (
    safe_next,
    Segmenter,
    DebugSegmenter
)

from .common_tokenize import (
    TokenSplitter,
    COMMON_RULES
)

########
#
#   SEGMENT
#
########


RULES = EN_RULES + COMMON_RULES


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
