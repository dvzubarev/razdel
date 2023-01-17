
import pytest

from razdel import tokenize

from .partition import parse_partitions
from .common import (
    run,
    data_path,
    data_lines
)


UNIT = parse_partitions([
    '1',
    'что-то',
    'К_тому_же',
    '...',
    '1,5',
    '1/2',
    '20|:|55',

    '»||.',
    ')||.',
    '(||«',
    ':)))',
    ':)||,',

    'mβж',
    'Δσ',
    '',
])


@pytest.mark.parametrize('test', UNIT)
def test_unit(test):
    run(tokenize, test)


def int_tests(count):
    path = data_path('tokens.txt')
    lines = data_lines(path, count)
    return parse_partitions(lines)


def test_int(int_test):
    run(tokenize, int_test)

EN_APOSTROPHE_CASES = parse_partitions([
    "(|companies|’|)",
    "Elsevier|’s",
    "2008|'s",
    "MTV|'s",
    "I|'m",
    "you|'d",
    "I|’ll",
    "must|'ve",
    "she|`s"

])

@pytest.mark.parametrize('test', EN_APOSTROPHE_CASES)
def test_en_apostrophe_cases(test):
    run(tokenize, test)


EN_SPECIAL_CASES = parse_partitions([
    "ca|n't",
    "DO|N'T",
    "DO|N’T",
    "Would|n't",
    "would|nt",
    "ai|n’t",
    "can|not",
    "Can|not",
    "sort|a",
    "kinda",
    "that|s"

])

@pytest.mark.parametrize('test', EN_SPECIAL_CASES)
def test_en_special_cases(test):
    run(tokenize, test)
