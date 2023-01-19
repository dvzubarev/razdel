
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
    '300,000',
    '3.14',
    '1/2',
    '20:55',
    '10x8',
    '10Х8',
    '20.04.2012',

    '$|500',
    '2,67|%',
    '+|27|°С',

    'в| |1990|г',
    '5|PM'
    'MP3',
    'МИ6',
    'СаМgВ6O8',
    'Аg2Te',
    'i2p',
    'XR4Ti',
    'АК-47',
    'Ми-8',
    'МЗП-1М',
    'x3-9890',

    'http://www.wikihow.com/wikiHow:Statistics|)',
    'http://im.yahoo.com/search?q=1&p=1%2C3%2C477#nor_re',
    'https://user@кто.рф:444/files/pdf/docs/rules_ru-rf.pdf|:)',
    'http://ex.ru|!',
    'https://ru.wikipedia.org/wiki/%D0%A1_%D0%B4|,',
    'doi:10.1037/0022-3514.92.6.1087',
    'doi:10.1002/0470856009.ch2f(ii)',
    '(|doi:10.1002/0470856009.ch2f(ii)|)|,',

    '(|cra.org/resources/taulbee-survey|)',
    'Secunia.edu.com|,',
    '<|ekrapels@esaibos.com|>',
    'privacy_policy!service@v-tell.com|.',
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

RU_UNIT = parse_partitions([
    '1-ый',
    '79-летний',
    'пол-яблока',
])

@pytest.mark.parametrize('test', RU_UNIT)
def test_ru_unit(test):
    run(tokenize, test)


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


def int_tests(count):
    path = data_path('tokens.txt')
    lines = data_lines(path, count)
    return parse_partitions(lines)


def test_int(int_test):
    run(tokenize, int_test)
