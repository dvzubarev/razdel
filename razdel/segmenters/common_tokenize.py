
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
DOI_REGEXP = r'doi:10\.\d+' + _URI_FULL_VALID_PATH_REGEXP

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
        #brackets are allowed in uri and they used in some DOIs
        #but doi can be in bracket, for example (doi:10.1/1).
        #So closing bracket will be part of a DOI, but this is mistake.
        #Try to fix this mistake, assuming that brackets  should be balanced inside DOI.
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

_WORDS_DICTIONARY = None

def init_words_dictionary(words_dict):
    global _WORDS_DICTIONARY
    _WORDS_DICTIONARY = words_dict


class BaseWordDictionary:
    def is_word_known(self, word:str, lang: str):
        return False

def get_words_dictionary()->BaseWordDictionary:
    global _WORDS_DICTIONARY
    if _WORDS_DICTIONARY is None:
        #by default init with empty dict
        _WORDS_DICTIONARY = BaseWordDictionary()
    return _WORDS_DICTIONARY


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


class DashRule(Rule2112):
    name = 'dash'

    def delimiter(self, delimiter):
        return delimiter in DASHES


    def rule(self, left:"Atom", right:"Atom"):
        if left.type == INT and right.type == RU:
            return JOIN

        if left.type in (LAT, RU) and right.type == INT:
            return JOIN


        if left.type in (RU, LAT) and right.type in (RU, LAT):
            # keep this as single token if it is found in dictionary, split otherwise
            words_dict = get_words_dictionary()
            word = left.text + '-' + right.text
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

    def rule(self, left, right):
        if left.type == INT and right.type == INT:
            return JOIN


class InsideDigitsRule(Rule2112):
    name = 'inside_digits'

    def delimiter(self, delimiter):
        return delimiter in 'xXхХ:/\\'

    def rule(self, left, right):
        if left.type == INT and right.type == INT:
            return JOIN

#########
#
#  MISC alphanumeric identifiers: Model names, ids, etc.
#
##########

def alphanum_ids(split: "TokenSplit"):
    if split.right_1.type == INT and any(c.isalpha() for c in split.buffer):
        #MP3, А4, XR4Ti
        return JOIN
    if (split.left_1.type == LAT and split.right_1.type == RU or
        split.left_1.type == RU and split.right_1.type == LAT):
        #СаМgВ6O8
        return JOIN

    if (split.left_1.type == INT
        and (split.right_1.text in DASHES or split.right_1.type in (LAT, RU))
        and not split.buffer.isdigit()
        ):
        # x3-9890
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
            yield atom.text


COMMON_RULES = [
    DashRule(),
    UnderscoreRule(),
    AmpRule(),
    CommonApostropheRule(),
    FloatRule(),
    InsideDigitsRule(),

    FunctionRule(punct),
    FunctionRule(other),

    FunctionRule(yahoo),

    FunctionRule(alphanum_ids),
    FunctionRule(tags),

]
