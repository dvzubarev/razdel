
import re

from razdel.record import (
    Record,
    cached_property
)
from razdel.rule import (
    JOIN, SPLIT,
    Rule,
    FunctionRule
)
from razdel.split import (
    Split,
    Splitter,
)

from .punct import (
    DASHES,
    ENDINGS,
    QUOTES,
    BRACKETS,
    APOSTROPHES,

    SMILES
)

from .sokr import SOKRS, PAIR_SOKRS

RU = 'RU'
LAT = 'LAT'
INT = 'INT'
PUNCT = 'PUNCT'
URI = 'URI'
DOI = 'DOI'
DOMAIN = 'DOM'
EMAIL = 'EMAIL'
OTHER = 'OTHER'

PUNCTS = '\\/!#$%&*+,.:;<=>?@^_`|~№…' + DASHES + QUOTES + BRACKETS

####complex atoms support
_URI_SCHEME_REGEXP = r'\b(https?|git|s3)://'

_URI_FULL_VALID_PATH_REGEXP = r'(?:[!#$&-;=?-[\]_a-z~]|%[0-9a-f]{2})*'
_URI_SANE_PATH_REGEXP = r'(?:[-!#$&*+.-;=?-Z_a-z~]|%[0-9a-f]{2})*'
_URI_HOST_REGEXP = r'[-a-zа-я0-9.@:._\+~=]{1,256}\b'

_COMMON_TLD_REGEXP = r'(?:com|net|org|int|edu|gov|de|icu|uk|ru|info|top|xyz|tk|cn|ga|cf|nl|io)'

DOMAIN_WITH_PATH_REGEXP = r'\b[-a-zа-я0-9.]{1,256}\.' + _COMMON_TLD_REGEXP + _URI_SANE_PATH_REGEXP

URI_WITH_HOST_REGEXP = _URI_SCHEME_REGEXP + _URI_HOST_REGEXP + _URI_SANE_PATH_REGEXP
#it is common? to put a space after doi:
#doi: 10.1109/TCAD.2013.2244643.
DOI_REGEXP = r'doi:\s?10\.\d+' + _URI_FULL_VALID_PATH_REGEXP

EMAIL_REGEXP = r"\b[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9.-]{1,256}\b"

ATOM = re.compile(
    rf'''
    (?P<URI>{URI_WITH_HOST_REGEXP})
    |(?P<DOI>{DOI_REGEXP})
    |(?P<DOM>{DOMAIN_WITH_PATH_REGEXP})
    |(?P<EMAIL>{EMAIL_REGEXP})
    |(?P<RU>[а-яё]+)
    |(?P<LAT>[a-z]+)
    |(?P<INT>\d+)
    |(?P<PUNCT>[{re.escape(PUNCTS)}])
    |(?P<OTHER>\S)
    ''',
    re.I | re.U | re.X
)

SMILE = re.compile(r'^' + SMILES + '$', re.U)


##########
#
#  HELPERS
#
######

def clean_uri_atom(uri_text):
    fixed_uri = None
    if uri_text[-1] in ')]':
        #brackets are allowed in uri and they are used in some DOIs.
        #Doi itself may be in bracket, for example (doi:10.1/1).
        #So closing bracket will be part of a DOI, but this is mistake.
        #Try to fix this mistake, assuming that brackets should be balanced inside DOI.
        closing_symbol = uri_text[-1]
        opening_symbol = '(' if closing_symbol == ')' else '['
        num_opening_symbols = uri_text.count(opening_symbol)
        num_closing_symbols = uri_text.count(closing_symbol)
        if num_closing_symbols != num_opening_symbols:
            fixed_uri = uri_text[:-1]

    elif uri_text[-1] in ',:;.!?*':
        #its likely to be not related to uri symbols
        fixed_uri = uri_text[:-1]


    if fixed_uri is not None:
        #repeate this operation, since there are possible cases: <end of doi>),
        return clean_uri_atom(fixed_uri)
    return uri_text

##########
#
#  Dictionaries support
#
######


class BaseWordDictionary:
    def is_word_known(self, word:str, lang: str):
        return False

_WORDS_DICTIONARY = None

def init_words_dictionary(words_dict):
    global _WORDS_DICTIONARY
    _WORDS_DICTIONARY = words_dict



def get_words_dictionary()->BaseWordDictionary:
    global _WORDS_DICTIONARY
    if _WORDS_DICTIONARY is None:
        #by default init with empty dict
        _WORDS_DICTIONARY = BaseWordDictionary()
    return _WORDS_DICTIONARY

class DefAbbrsWordDictionary(BaseWordDictionary):
    def __init__(self) -> None:
        self._known_pair_abbrs = frozenset(' '.join(a) for a in PAIR_SOKRS)

    def is_word_known(self, word:str, lang: str):
        if word in SOKRS:
            return True
        return word in self._known_pair_abbrs


_ABBREVS_DICTIONARY = None


def init_abbrevs_dictionary(abbrevs_dict):
    global _ABBREVS_DICTIONARY
    _ABBREVS_DICTIONARY = abbrevs_dict

def get_abbrevs_dictionary()->BaseWordDictionary:
    global _ABBREVS_DICTIONARY
    if _ABBREVS_DICTIONARY is None:
        #by default init with abrrevs from sokr module
        _ABBREVS_DICTIONARY = DefAbbrsWordDictionary()
    return _ABBREVS_DICTIONARY


##########
#
#  TRIVIAL
#
######


def split_space(split):
    if split.delimiter:
        return SPLIT


##########
#
#   2112
#
##########


class Rule2112(Rule):
    def __call__(self, split):
        if self.delimiter(split.left):
            # cho-|to
            left, right = split.left_2, split.right_1
        elif self.delimiter(split.right):
            # cho|-to
            left, right = split.left_1, split.right_2
        else:
            return

        if not left or not right:
            return

        return self.rule(left, right)


class DashRule(Rule):
    name = 'dash'

    def delimiter(self, delimiter):
        return delimiter in DASHES


    def __call__(self, split:"TokenSplit"):
        if self.delimiter(split.left):
            # cho-|to
            left_2, left, right, right_2 = split.left_3, split.left_2, split.right_1, split.right_2
        elif self.delimiter(split.right):
            # cho|-to
            left_2, left, right, right_2 = split.left_2, split.left_1, split.right_2, split.right_3
        else:
            return

        if not left or not right:
            return

        if left.type == INT and (right.type == RU or right.text.istitle()):
            return JOIN

        if left.type in (LAT, RU) and right.type == INT:
            return JOIN

        if (left.text.istitle() and right.text.istitle() or
            left.text in ('in', 'of') and right.text.istitle() or
            left.text.istitle() and right.text in ('in', 'of')):
            # keep this as single token if both part are titlecased
            return JOIN

        if left.type in (RU, LAT) and right.type in (RU, LAT):
            # keep this as single token if it is found in dictionary, split otherwise
            words_dict = get_words_dictionary()

            prefix = ''
            if left_2 and left_2.text in DASHES and left_2.stop == left.start:
                #state-\of|-the-art
                prefix = '-'
            suffix = ''
            if right_2 and right_2.text in DASHES and right.stop == right_2.start:
                #state-of|-the/-art
                suffix = '-'
            word = prefix + left.text + '-' + right.text + suffix

            lang = 'ru' if left.type == RU or right.type == RU else 'en'
            if words_dict.is_word_known(word, lang):
                return JOIN



class UnderscoreRule(Rule2112):
    name = 'underscore'

    def delimiter(self, delimiter):
        return delimiter == '_'

    def rule(self, left, right):
        if left.type == PUNCT or right.type == PUNCT:
            return
        return JOIN

class AmpRule(Rule2112):
    name = 'ampersand'

    def delimiter(self, delimiter):
        return delimiter == '&'

    def rule(self, left, right):
        if (left.type in (LAT, RU)
            and right.type in (LAT, RU)
            and left.text[-1].isupper()
            and right.text[0].isupper()):
            return JOIN

class CommonApostropheRule(Rule2112):
    name = 'apostrophe'

    def delimiter(self, delimiter):
        return delimiter in APOSTROPHES

    def rule(self, left:"Atom", right:"Atom"):
        if (left.normal in ('д', 'л', 'о', 'd', 'o', 'xi', 'l')):
            return JOIN


class FloatRule(Rule2112):
    name = 'float'

    def delimiter(self, delimiter):
        return delimiter in '.,'

    def rule(self, left:"Atom", right:"Atom"):
        #check that there is no space between delimiter and any part.
        #left stop (it is pos of delimiter) + 1 should be equal to start of the right.
        if left.type == INT and right.type == INT and left.stop + 1 == right.start:
            return JOIN



class InsideDigitsRule(Rule):
    name = 'inside_digits'

    def delimiter(self, delimiter):
        return delimiter in 'xXхХ:/\\'

    def __call__(self, split:"TokenSplit"):
        if self.delimiter(split.left):
            # cho-|to
            delim, left, right, right_2 = split.left, split.left_2, split.right_1, split.right_2
        elif self.delimiter(split.right):
            # cho|-to
            delim, left, right, right_2 = split.right, split.left_1, split.right_2, split.right_3
        else:
            return

        if not left or not right:
            return

        #check that there is space between right and right_2.
        #right's stop should not be equal to start of the right_2.
        # print('right', right, 'right2', right_2)
        if left.type == INT and right.type == INT and (right_2 is None or
                                                       right.stop != right_2.start):

            if delim == ':':
                #keep as single token only if it looks like time
                try:
                    if (len(left.text)< 3 and len(right.text) < 3 and
                        0 < int(left.text) <= 24 and
                        0 < int(right.text) < 60):
                        return JOIN
                except ValueError:
                    pass
            else:
                return JOIN

#########
#
#  Common Abbrevs support
#
##########

def abbrevs(split: "TokenSplit"):
    def _det_lang(atom:"Atom"):
        return 'ru' if atom.type == RU else 'en'

    #detect pair abbrevs
    pair = None
    between_pair = False
    lang = None
    if split.right == '.' and split.right_3 and split.right_3.text == '.':
        #т|.д.
        pair = f'{split.left_1.normal} {split.right_2.normal}'
        lang = _det_lang(split.left_1)
    if split.left_2 and split.left == '.' and split.right_2 and split.right_2.text == '.':
        #т.|д.
        pair = f'{split.left_2.normal} {split.right_1.normal}'
        lang = _det_lang(split.left_2)
        between_pair = True
    if split.left_3 and split.left_2 and split.left_2.text == '.' and split.right == '.':
        #т.д|.
        pair = f'{split.left_3.normal} {split.left_1.normal}'
        lang = _det_lang(split.left_3)

    abbrevs_dict = get_abbrevs_dictionary()
    if pair is not None and lang is not None:
        if not between_pair:
            if abbrevs_dict.is_word_known(pair, lang):
                return JOIN
        else:
            if lang == 'en' and abbrevs_dict.is_word_known(pair, lang):
                return JOIN

    #single abbr
    if split.right == '.':
        #гг|. or Д|.

        if len(split.left) == 1 and split.left.isupper():
            return JOIN
        lang = _det_lang(split.left_1)
        if abbrevs_dict.is_word_known(split.left_1.normal, lang):
            return JOIN


#########
#
#  MISC alphanumeric identifiers: Model names, ids, etc.
#
##########

def alphanum_ids(split: "TokenSplit"):
    assert split.buffer is not None, "Logic error 12"
    alphanum_id_regex = r'^[@#]?\w++[\w_–-]*+'

    if (split.right_1.type == INT and re.fullmatch(alphanum_id_regex, split.buffer) is not None):
        #MP3, А4, XR4Ti
        return JOIN

    if (split.left_1.type == INT
        and (split.right_1.text in DASHES or split.right_1.type in (LAT, RU))
        and not split.buffer.isdigit()
        and re.fullmatch(alphanum_id_regex, split.buffer) is not None
        ):
        # x3-9890
        return JOIN

    if (split.left_1.type == LAT and split.right_1.type == RU or
        split.left_1.type == RU and split.right_1.type == LAT):
        #СаМgВ6O8
        return JOIN

def tags(split: "TokenSplit"):
    if split.left == '@' and split.right_1.type in (INT, RU, LAT):
        return JOIN
    if split.left == '#' and split.right_1.type in (RU, LAT):
        return JOIN


#########
#
#   PUNCT
#
##########


def punct(split):
    if split.left_1.type != PUNCT or split.right_1.type != PUNCT:
        return

    left = split.left
    right = split.right

    if SMILE.match(split.buffer + right):
        return JOIN

    if left in ENDINGS and right in ENDINGS:
        # ... ?!
        return JOIN

    if left + right in ('--', '**'):
        # ***
        return JOIN


def other(split):
    left = split.left_1.type
    right = split.right_1.type

    if left == OTHER and right in (OTHER, RU, LAT):
        # ΔP
        return JOIN

    if left in (OTHER, RU, LAT) and right == OTHER:
        # Δσ mβж
        return JOIN


########
#
#  EXCEPTION
#
#######


def yahoo(split):
    if split.left_1.normal == 'yahoo' and split.right == '!':
        return JOIN


########
#
#   SPLIT
#
########


class Atom(Record):
    __attributes__ = ['start', 'stop', 'type', 'text']

    def __init__(self, start, stop, type, text):
        self.start = start
        self.stop = stop
        self.type = type
        self.text = text
        self.normal = text.lower()


class TokenSplit(Split):
    def __init__(self, left, delimiter, right):
        self.left_atoms = left
        self.right_atoms = right
        super(TokenSplit, self).__init__(
            self.left_1.text,
            delimiter,
            self.right_1.text
        )

    @cached_property
    def left_1(self):
        return self.left_atoms[-1]

    @cached_property
    def left_2(self):
        if len(self.left_atoms) > 1:
            return self.left_atoms[-2]

    @cached_property
    def left_3(self):
        if len(self.left_atoms) > 2:
            return self.left_atoms[-3]

    @cached_property
    def right_1(self):
        return self.right_atoms[0]

    @cached_property
    def right_2(self):
        if len(self.right_atoms) > 1:
            return self.right_atoms[1]

    @cached_property
    def right_3(self):
        if len(self.right_atoms) > 2:
            return self.right_atoms[2]



class TokenSplitter(Splitter):
    def __init__(self, window=3):
        self.window = window

    def _create_atoms_from_uri(self, match, atom_type):
        uri_text = match.group(0)
        cleaned_uri_text = clean_uri_atom(uri_text)
        uri_start = match.start()
        uri_end = uri_start + len(cleaned_uri_text)
        yield Atom(uri_start, uri_end, atom_type, cleaned_uri_text)

        rest_atoms = len(uri_text) - len(cleaned_uri_text)
        atom_start = uri_end - uri_start

        while rest_atoms:
            yield Atom(atom_start, atom_start+1, PUNCT, uri_text[atom_start])
            rest_atoms -= 1
            atom_start += 1


    def atoms(self, text):
        matches = ATOM.finditer(text)
        for match in matches:
            atom_type = match.lastgroup
            if atom_type in (URI, DOI, DOMAIN, EMAIL):
                yield from self._create_atoms_from_uri(match, atom_type)
            else:
                start = match.start()
                stop = match.end()
                text = match.group(0)
                yield Atom(
                    start, stop,
                    atom_type, text
                )

    def __call__(self, text):
        atoms = list(self.atoms(text))
        for index in range(len(atoms)):
            atom = atoms[index]
            if index > 0:
                previous = atoms[index - 1]
                delimiter = text[previous.stop:atom.start]
                left = atoms[max(0, index - self.window):index]
                right = atoms[index:index + self.window]
                yield TokenSplit(left, delimiter, right)
            yield atom.text, atom.type


COMMON_RULES = [
    DashRule(),
    UnderscoreRule(),
    AmpRule(),
    CommonApostropheRule(),
    FloatRule(),
    InsideDigitsRule(),

    FunctionRule(abbrevs),
    FunctionRule(punct),
    FunctionRule(other),

    FunctionRule(yahoo),

    FunctionRule(alphanum_ids),
    FunctionRule(tags),

]
