# razdel [![Build Status](https://travis-ci.org/natasha/razdel.svg?branch=master)](https://travis-ci.org/natasha/razdel)

`razdel` — библиотека для разделения русскоязычного текста на токены и предложения. Система построена на правилах. Решение показывает на обоих задачах качество и производительность выше других инструментов. Результаты оценок в [eval.ipynb](https://github.com/natasha/razdel/blob/master/eval.ipynb).

## Использование

```python
from razdel import tokenize

tokens = list(tokenize('Кружка-термос на 0.5л (50—64 см³, 516;...)'))
tokens[:5]
[Substring(0, 13, 'Кружка-термос'),
 Substring(14, 16, 'на'),
 Substring(17, 20, '0.5'),
 Substring(20, 21, 'л'),
 Substring(22, 23, '(')]
 
[_.text for _ in tokens]
['Кружка-термос', 'на', '0.5', 'л', '(', '50—64', 'см³', ',', '516', ';', '...', ')']


```
```python
from razdel import sentenize

text = '''Епископский перстень (лат. Annulus pontificalis) — 
является одной из понтификальных инсигний епископов и аббатов
в латинском обряде, а также в некоторых восточных обрядах
(например, армянском), а также носится епископами Лютеранской
церкви. Впервые упомянут в этом качестве в начале VII века и
получил повсеместное распространение на Западе в IX—X веках.
Символизирует обручение епископа со своей Церковью, а также —
как печать — его власть, о чём свидетельствует формула при
вручении перстня во время епископской хиротонии или возведении
в сан аббата: «Прими перстень как печать верности, чтобы,
украшенный, незапятнанной верой, ты хранил непорочной Невесту
Божию, то есть Святую Церковь» (в реформированном чине: «Прими
этот перстень как знамение твоей верности; с верой и любовью
защищай Невесту Божию, Его Святую Церковь»). Епископ Рима,
который также является Папой римским, носит так называемое
кольцо рыбака. Bd. 16, Berlin 1993, S. 196—202.'
'''
list(sentenize(text))
[Substring(0, 241, 'Епископский перстень (лат. Annulus pontificalis) — \nявляется одной из понтификальных инсигний епископов и аббатов\nв латинском обряде, а также в некоторых восточных обрядах\n(например, армянском), а также носится епископами Лютеранской\nцеркви.'),
 Substring(242, 355, 'Впервые упомянут в этом качестве в начале VII века и\nполучил повсеместное распространение на Западе в IX—X веках.'),
 Substring(356, 828, 'Символизирует обручение епископа со своей Церковью, а также —\nкак печать — его власть, о чём свидетельствует формула при\nвручении перстня во время епископской хиротонии или возведении\nв сан аббата: «Прими перстень как печать верности, чтобы,\nукрашенный, незапятнанной верой, ты хранил непорочной Невесту\nБожию, то есть Святую Церковь» (в реформированном чине: «Прими\nэтот перстень как знамение твоей верности; с верой и любовью\nзащищай Невесту Божию, Его Святую Церковь»).'),
 Substring(829, 916, 'Епископ Рима,\nкоторый также является Папой римским, носит так называемое\nкольцо рыбака.'),
 Substring(917, 950, "Bd. 16, Berlin 1993, S. 196—202.'")]
```

## Установка

`razdel` поддерживает Python 2.7+, 3.4+ и PyPy 2, 3.

```bash
$ pip install razdel
```

## Лицензия

MIT

## Поддержка

- Чат — https://telegram.me/natural_language_processing
- Тикеты — https://github.com/natasha/razdel/issues

## Разработка

