# **A fixed version of code for morpheme tokenization of KoNLPy Mecab class**

## Requirements
- Python 3.x
- [KoNLPy with Mecab](https://konlpy.org/en/latest/install/ "KoNLPy: Installation")

## Installation
1. Download the fixed version (_mecab.py)
2. Figure out the path of your KoNLPy
    - one way to figure out the path
    ```python
    import konlpy
    print(konlpy.__file__)
    ```
3. Replace the original file with the fixed version\
***Please back up the original file!***

## Simple Demo
1) The original version
```python
from konlpy.tag import Mecab
mc = Mecab(use_original=True)
print(mc.pos("들어간다"))
```
```python
[('들어간다', 'VV+EC')]
```

2) The fixed version
```python
from konlpy.tag import Mecab
mc = Mecab(use_original=False)
print(mc.pos("들어간다"))
```
```python
[('들어가', 'VV'), ('ㄴ다', 'EC')]
```

<br>

## Description (English)
MeCab-Ko is the fastest of all the morphological analyzer in KoNLPy. [[reference]](https://konlpy.org/en/latest/morph/#id1 "KoNLPy: Morphological analysis and POS tagging") However, its morpheme tokenization doesn't work under a certain condition.

```python
from konlpy.tag import Mecab
mc = Mecab()
print(mc.pos("들어간다"))
```
```python
[('들어간다', 'VV+EC')]
```

The string above is not morpheme-tokenized properly. What we expect is

```python
[('들어가', 'VV'), ('ㄴ다', 'EC')]
```

It seems that **if the sum of morpheme-tokenized strings in an eojeol string is not equal to the original string,** MeCab-Ko does not tokenize the eojeol string.
To put it another way, 

### 1) sum of morpheme-tokenized strings == original string<br>
(ex. '들어가' + '다' == '들어가다')
```python
from konlpy.tag import Mecab
mc = Mecab()
print(mc.pos("들어가다"))
```
```python
[('들어가', 'VV'), ('다', 'EC')]
```

### 2) sum of morpheme-tokenized strings != original string<br>
(ex. '들어가' + 'ㄴ다' != '들어간다')
```python
from konlpy.tag import Mecab
mc = Mecab()
print(mc.pos("들어간다"))
```
```python
[('들어간다', 'VV+EC')]
```

This causes inconsistent tokenization, and makes weird POS tags like VV+EC which users would not want.
The fixed code in this repository would solve this problem. It forces MeCab-ko to morpheme-tokenize all eojeol strings consistently.

<br>

Additionaly, there are some other changes.
- Ideographic spaces (\u3000) which cannot be distinguished from eojeol separators (spaces) with the naked eye are replaced with spaces (" ").
- Consonant characters *ᆫ*, *ᆯ*, and *ᄇ* are replaced with *ㄴ*, *ㄹ*, and *ㅂ* which can be typed easily on a keyboard.
- A 2 eojeol string '영치기 영차' which is incorrectly morpheme-tokenized as one morpheme (영치기 영차/IC) is forced to morpheme-tokenized as two morphemes temporarily.

<br>

## Description (한국어)
MeCab-ko는 KoNLPy에서 활용할 수 있는 형태소 분석기 중 분석 시간의 측면에서 가장 뛰어난 성능을 보이는 형태소 분석기이다. [[reference]](https://konlpy.org/en/latest/morph/#id1 "KoNLPy: Morphological analysis and POS tagging") 다만 특정 조건하에서 형태소 토큰화가 일반적인 방식으로 이루어지지 않는 경우가 있다.

```python
from konlpy.tag import Mecab
mc = Mecab()
print(mc.pos("들어간다"))
```
```python
[('들어간다', 'VV+EC')]
```

위의 예에서 하나의 어절(들어간다)이 하나의 토큰(들어간다/VV+EC)으로 토큰화되어 있음을 알 수 있다.

그러나 사용자가 기대하는 분석 결과는 다음과 같을 것이다.

```python
[('들어가', 'VV'), ('ㄴ다', 'EC')]
```

현재까지 파악된 바로는, **어절 내 형태소 문자열들에서 초성, 중성 등의 낱글자만 일반 낱글자로 변환(가령 종성 "ᆯ"을 일반 낱글자 "ㄹ"로 변환)한 후 합한(Python에서의 + 연산) 결과가 원어절 문자열과 동일하지 않은 경우**에 이러한 방식으로 분석이 되는 것으로 보인다. 즉 다음과 같은 두 가지 경우에 따라 토큰화가 다르게 이루어지는 것이다.

### 1) 어절 내 형태소 문자열의 합 == 원래 어절 문자열<br>
(예: '들어가' + '다' == '들어가다')
```python
from konlpy.tag import Mecab
mc = Mecab()
print(mc.pos("들어가다"))
```
```python
[('들어가', 'VV'), ('다', 'EC')]
```

### 2) 어절 내 형태소 문자열의 합 != 원래 어절 문자열<br>
(예: '들어가' + 'ㄴ다' != '들어간다')
```python
from konlpy.tag import Mecab
mc = Mecab()
print(mc.pos("들어간다"))
```
```python
[('들어간다', 'VV+EC')]
```

이로 인해 KoNLPy에서 MeCab-ko를 이용하는 경우에 일반적인 방식의 형태소 토큰화(위의 1) 방식)가 일관되게 이루어지지 않을 뿐 아니라, 일반적인 경우에 사용자가 원하지 않는 POS 태그(예: VV+EC)가 생성되는 문제가 발생한다. 본 코드를 이용하면 위의 1) 방식으로 일관된 형태소 토큰화를 함으로써 이러한 문제를 해결할 수 있다.

<br>

추가적으로 다음과 같은 변경 사항이 존재한다.
- 어절 구분자인 space와 육안으로 구분되지 않는 ideographic space **\u3000**을 space로 변환하여 처리하도록 함.
- 자음 문자 *ᆫ*, *ᆯ*, *ᄇ을*, 키보드에서 바로 입력할 수 있는, 일반 낱글자 *ㄴ*, *ㄹ*, *ㅂ* 로 변환하여 처리하도록 함.
- '영치기 영차'라는 2어절 문자열을 공백을 포함한 하나의 형태소 토큰(영치기 영차/IC)으로 분석하는 문제가 있어, 이를 2개의 형태소 토큰으로 나누어 분석하도록 임시 조치함.


## KoNLPy GitHub
https://github.com/konlpy/konlpy


## update log
- 2021-09-10
    - We added an instance variable 'use_original' so that you don't have to replace the "_mecab.py" file itself to use the original or the fixed version.
    - The default value is False, which means we use the fixed version. If you want to use the original version, set the variable as True.
