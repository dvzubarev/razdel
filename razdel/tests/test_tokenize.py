
import pytest

from razdel import tokenize as tokenize_orig
from razdel.segmenters.common_tokenize import BaseWordDictionary, init_words_dictionary
from razdel.substring import Substring

from .partition import parse_partitions
from .common import (
    run,
    data_path,
    data_lines
)

def tokenize(text):
    #convert Token to Substring, so tests can compare gold results with tokenize output
    for t in tokenize_orig(text):
        yield Substring(t.start, t.stop, t.text)

UNIT = parse_partitions([
    '1',
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
    '1991|-|1995',

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
    'MiG-23BN',
    'i|&|1',
    'S&P',
    'AT&T',

    '(|http://www.wikihow.com/wikiHow:Statistics|)',
    'http://im.yahoo.com/search?q=1&p=1%2C3%2C477#nor_re',
    'https://user@кто.рф:444/files/pdf/docs/rules_ru-rf.pdf|:)',
    'http://ex.ru|!',
    'https://ru.wikipedia.org/wiki/%D0%A1_%D0%B4|,',
    'doi:10.1037/0022-3514.92.6.1087',
    'doi: 10.1109/TCAD.2013.2244643|.',
    'doi:\n10.1109/ISDA.2007.5|.',
    'doi:10.1002/0470856009.ch2f(ii)',
    '(|doi:10.1002/0470856009.ch2f(ii)|)|,',

    '(|cra.org/resources/taulbee-survey|)',
    'Secunia.edu.com|,',
    '<|ekrapels@esaibos.com|>',
    'privacy_policy!service@v-tell.com|.',
    '@anna_li',
    '@c3p1o',
    '#хэштэг',
    '#hash13',
    '#|13',

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




@pytest.fixture
def with_words_dict():
    class DummyDict(BaseWordDictionary):
        def __init__(self) -> None:
            super().__init__()
            self.known_words = {'что-то', 'премьер-министром',
                                #en
                                'state-of-', '-of-the-', '-the-art'}
        def is_word_known(self, word, lang):
            return word in self.known_words

    words_dict = DummyDict()
    init_words_dictionary(words_dict)
    return words_dict



RU_UNIT = parse_partitions([
    'что-то',
    'премьер-министром',
    '-| |премьер-министром',
    'строитель|-|программист',
    '1-ый',
    '79-летний',
    'пол|-|яблока',
    'Вася|-|то',
    'сине-зеленый',
    'уныло-однообразном',
    'химико-биологическому',
    'общественно-трудовые',
    'кол-во',
    'Тополь-М',
    'Гвинее-Бисау',
    'СТРОИТЕЛЬ|-|ПРОГРАММИСТ',
    'Вади-эль-Аасаль',
    'Джебель-эш-Шейх',
    'Порт-о-Пренса',

    'О\'Нил',
    'Кот-д’Ивуар',
    'Д’Артаньян',
    'Л\'этуаль',
    "пол|'|слова",

    'стр.',
    'П.',
    'и| |т.|д.',
    'т.| |д.',
    'к.|т.|н.| |и|.',
    'т.|д.| |т.|п.',
    'т.|п.| |т.|д.',
    # like к.ф.-м.н.
    'к.|т.|-|т.|н.',
])

@pytest.mark.parametrize('test', RU_UNIT)
def test_ru_unit(test, with_words_dict):
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
    "she|`s",
    "L'Enfant",
    "o'clock",
    "Xi'an",
    "O'Kicki",


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

EN_MISC_CASES = parse_partitions([
    '31st',
    '42nd',
    '3rd',
    '80th',
    '1980s',
    '1908|s',
    'mid-1990s',
    'mid-90s',
    '80s',
    '85|s',
    'its| |30|-|day',
    'e-ink',
    'vice-president',
    'state-of-the-art',
    'its| |-| |of|-|the| |-| |art',
    'corp.',
    'p.m.| |8| |a.m.'
])

@pytest.mark.parametrize('test', EN_MISC_CASES)
def test_en_misc_cases(test, with_words_dict):
    run(tokenize, test)

def int_tests(count):
    path = data_path('tokens.txt')
    lines = data_lines(path, count)
    return parse_partitions(lines)


def test_int(int_test):
    run(tokenize, int_test)
