<img src="https://github.com/natasha/natasha-logos/blob/master/razdel.svg">

![CI](https://github.com/natasha/razdel/workflows/CI/badge.svg) [![codecov](https://codecov.io/gh/natasha/razdel/branch/master/graph/badge.svg)](https://codecov.io/gh/natasha/razdel)

`razdel` — rule-based system for Russian sentence and word tokenization..

## Usage

```python
>>> from razdel import tokenize

>>> tokens = list(tokenize('Кружка-термос на 0.5л (50/64 см³, 516;...)'))
>>> tokens
[Substring(0, 13, 'Кружка-термос'),
 Substring(14, 16, 'на'),
 Substring(17, 20, '0.5'),
 Substring(20, 21, 'л'),
 Substring(22, 23, '(')
 ...]
 
>>> [_.text for _ in tokens]
['Кружка-термос', 'на', '0.5', 'л', '(', '50/64', 'см³', ',', '516', ';', '...', ')']
```

```python
>>> from razdel import sentenize

>>> text = '''
... - "Так в чем же дело?" - "Не ра-ду-ют".
... И т. д. и т. п. В общем, вся газета
... '''

>>> list(sentenize(text))
[Substring(1, 23, '- "Так в чем же дело?"'),
 Substring(24, 40, '- "Не ра-ду-ют".'),
 Substring(41, 56, 'И т. д. и т. п.'),
 Substring(57, 76, 'В общем, вся газета')]
```

## Installation

`razdel` supports Python 3.5+ and PyPy 3.

```bash
$ pip install razdel
```

## Quality, performance
<a name="evalualtion"></a>

Unfortunately, there is no single correct way to split text into sentences and tokens. For example, one may split `«Как же так?! Захар...» — воскликнут Пронин.` into three sentences `["«Как же так?!",  "Захар...»", "— воскликнут Пронин."]` while `razdel` splits it into two `["«Как же так?!", "Захар...» — воскликнут Пронин."]`. What would be the correct way to tokenizer `т.е.`? One may split in into `т.|е.`, `razdel` splits into `т|.|е|.`.

`razdel` tries to mimic segmentation of these 4 datasets : <a href="https://github.com/natasha/corus#load_ud_syntag">SynTagRus</a>, <a href="https://github.com/natasha/corus#load_morphoru_corpora">OpenCorpora</a>, <a href="https://github.com/natasha/corus#load_morphoru_gicrya">GICRYA</a> and <a href="https://github.com/natasha/corus#load_morphoru_rnc">RNC</a>. These datasets mainly consist of news and fiction. `razdel` rules are optimized for these kinds of texts. Library may perform worse on other domains like social media, scientific articles, legal documents.

We measure absolute number of errors. There are a lot of trivial cases in the tokenization task. For example, text `чуть-чуть?!` is not non-trivial, one may split it into `чуть|-|чуть|?|!` while the correct tokenization is `чуть-чуть|?!`, such examples are rare. Vast majority of cases are trivial, for example text `в 5 часов ...` is correctly tokenized even via Python native `str.split` into `в| |5| |часов| |...`. Due to the large number of trivial case overall quality of all segmenators is high, it is hard to compare differentiate between for examlpe 99.33%, 99.95% and 99.88%, so we report the absolute number of errors.

`errors` — number of errors. For example, consider etalon segmentation is `что-то|?`, prediction is `что|-|то?`, then the number of errors is 3: 1 for missing split `то?` + 2 for extra splits `что|-|то`.

`time` — total seconds taken.

`spacy_tokenize`, `aatimofeev` and others a defined in <a href="https://github.com/natasha/naeval/blob/master/naeval/segment/models.py">naeval/segment/models.py</a>. Tables are computed in <a href="https://github.com/natasha/naeval/blob/master/scripts/segment/main.ipynb">segment/main.ipynb</a>.

### Tokens

<!--- token --->
<table border="0" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th colspan="2" halign="left">corpora</th>
      <th colspan="2" halign="left">syntag</th>
      <th colspan="2" halign="left">gicrya</th>
      <th colspan="2" halign="left">rnc</th>
    </tr>
    <tr>
      <th></th>
      <th>errors</th>
      <th>time</th>
      <th>errors</th>
      <th>time</th>
      <th>errors</th>
      <th>time</th>
      <th>errors</th>
      <th>time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>re.findall(\w+|\d+|\p+)</th>
      <td>4161</td>
      <td>0.5</td>
      <td>2660</td>
      <td>0.5</td>
      <td>2277</td>
      <td>0.4</td>
      <td>7606</td>
      <td>0.4</td>
    </tr>
    <tr>
      <th>spacy</th>
      <td>4388</td>
      <td>6.2</td>
      <td>2103</td>
      <td>5.8</td>
      <td><b>1740</b></td>
      <td>4.1</td>
      <td>4057</td>
      <td>3.9</td>
    </tr>
    <tr>
      <th>nltk.word_tokenize</th>
      <td>14245</td>
      <td>3.4</td>
      <td>60893</td>
      <td>3.3</td>
      <td>13496</td>
      <td>2.7</td>
      <td>41485</td>
      <td>2.9</td>
    </tr>
    <tr>
      <th>mystem</th>
      <td>4514</td>
      <td>5.0</td>
      <td>3153</td>
      <td>4.7</td>
      <td>2497</td>
      <td>3.7</td>
      <td><b>2028</b></td>
      <td>3.9</td>
    </tr>
    <tr>
      <th>mosestokenizer</th>
      <td><b>1886</b></td>
      <td><b>2.1</b></td>
      <td><b>1330</b></td>
      <td><b>1.9</b></td>
      <td>1796</td>
      <td><b>1.6</b></td>
      <td><b>2123</b></td>
      <td><b>1.7</b></td>
    </tr>
    <tr>
      <th>segtok.word_tokenize</th>
      <td>2772</td>
      <td><b>2.3</b></td>
      <td><b>1288</b></td>
      <td><b>2.3</b></td>
      <td>1759</td>
      <td><b>1.8</b></td>
      <td><b>1229</b></td>
      <td><b>1.8</b></td>
    </tr>
    <tr>
      <th>aatimofeev/spacy_russian_tokenizer</th>
      <td>2930</td>
      <td>48.7</td>
      <td><b>719</b></td>
      <td>51.1</td>
      <td><b>678</b></td>
      <td>39.5</td>
      <td>2681</td>
      <td>52.2</td>
    </tr>
    <tr>
      <th>koziev/rutokenizer</th>
      <td><b>2627</b></td>
      <td><b>1.1</b></td>
      <td>1386</td>
      <td><b>1.0</b></td>
      <td>2893</td>
      <td><b>0.8</b></td>
      <td>9411</td>
      <td><b>0.9</b></td>
    </tr>
    <tr>
      <th>razdel.tokenize</th>
      <td><b>1510</b></td>
      <td>2.9</td>
      <td>1483</td>
      <td>2.8</td>
      <td><b>322</b></td>
      <td>2.0</td>
      <td>2124</td>
      <td>2.2</td>
    </tr>
  </tbody>
</table>
<!--- token --->

### Sentencies

<!--- sent --->
<table border="0" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th colspan="2" halign="left">corpora</th>
      <th colspan="2" halign="left">syntag</th>
      <th colspan="2" halign="left">gicrya</th>
      <th colspan="2" halign="left">rnc</th>
    </tr>
    <tr>
      <th></th>
      <th>errors</th>
      <th>time</th>
      <th>errors</th>
      <th>time</th>
      <th>errors</th>
      <th>time</th>
      <th>errors</th>
      <th>time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>re.split([.?!…])</th>
      <td>20456</td>
      <td>0.9</td>
      <td>6576</td>
      <td>0.6</td>
      <td>10084</td>
      <td>0.7</td>
      <td>23356</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>segtok.split_single</th>
      <td>19008</td>
      <td>17.8</td>
      <td>4422</td>
      <td>13.4</td>
      <td>159738</td>
      <td><b>1.1</b></td>
      <td>164218</td>
      <td><b>2.8</b></td>
    </tr>
    <tr>
      <th>mosestokenizer</th>
      <td>41666</td>
      <td><b>8.9</b></td>
      <td>22082</td>
      <td><b>5.7</b></td>
      <td>12663</td>
      <td>6.4</td>
      <td>50560</td>
      <td><b>7.4</b></td>
    </tr>
    <tr>
      <th>nltk.sent_tokenize</th>
      <td><b>16420</b></td>
      <td><b>10.1</b></td>
      <td><b>4350</b></td>
      <td><b>5.3</b></td>
      <td><b>7074</b></td>
      <td><b>5.6</b></td>
      <td><b>32534</b></td>
      <td>8.9</td>
    </tr>
    <tr>
      <th>deeppavlov/rusenttokenize</th>
      <td><b>10192</b></td>
      <td>10.9</td>
      <td><b>1210</b></td>
      <td>7.9</td>
      <td><b>8910</b></td>
      <td>6.8</td>
      <td><b>21410</b></td>
      <td><b>7.0</b></td>
    </tr>
    <tr>
      <th>razdel.sentenize</th>
      <td><b>9274</b></td>
      <td><b>6.1</b></td>
      <td><b>824</b></td>
      <td><b>3.9</b></td>
      <td><b>11414</b></td>
      <td><b>4.5</b></td>
      <td><b>10594</b></td>
      <td>7.5</td>
    </tr>
  </tbody>
</table>
<!--- sent --->

## Support

- Chat — https://telegram.me/natural_language_processing
- Issues — https://github.com/natasha/razdel/issues

## Development

Test:

```bash
pip install -e .
pip install -r requirements/ci.txt
make test
make int  # 2000 integration tests
```

Package:

```bash
make version
git push
git push --tags

make clean wheel upload
```

`mystem` errors on `syntag`:

```bash
# see naeval/data
cat syntag_tokens.txt | razdel-ctl sample 1000 | razdel-ctl gen | razdel-ctl diff --show moses_tokenize | less
```

Non-trivial token tests:

```bash
pv data/*_tokens.txt | razdel-ctl gen --recall | razdel-ctl diff space_tokenize > tests.txt
pv data/*_tokens.txt | razdel-ctl gen --precision | razdel-ctl diff re_tokenize >> tests.txt
```

Update integration tests:

```bash
cd razdel/tests/data/
pv sents.txt | razdel-ctl up sentenize > t; mv t sents.txt
```

`razdel` and `moses` diff:

```bash
cat data/*_tokens.txt | razdel-ctl sample 1000 | razdel-ctl gen | razdel-ctl up tokenize | razdel-ctl diff moses_tokenize | less
```

`razdel` performance:

```bash
cat data/*_tokens.txt | razdel-ctl sample 10000 | pv -l | razdel-ctl gen | razdel-ctl diff tokenize | wc -l
```
