# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sys

try:
    from MeCab import Tagger
except ImportError:
    pass

from konlpy import utils


__all__ = ['Mecab']


attrs = ['tags',        # 품사 태그
         'semantic',    # 의미 부류
         'has_jongsung',  # 종성 유무
         'read',        # 읽기
         'type',        # 타입
         'first_pos',   # 첫번째 품사
         'last_pos',    # 마지막 품사
         'original',    # 원형
         'indexed']     # 인덱스 표현


def parse(result, allattrs=False, join=False):
    def split(elem, join=False):
        if not elem: return ('', 'SY')
        s, t = elem.split('\t')
        if join:
            return s + '/' + t.split(',', 1)[0]
        else:
            return (s, t.split(',', 1)[0])

    return [split(elem, join=join) for elem in result.splitlines()[:-1]]


class Mecab():
    """Wrapper for MeCab-ko morphological analyzer.

    `MeCab`_, originally a Japanese morphological analyzer and POS tagger
    developed by the Graduate School of Informatics in Kyoto University,
    was modified to MeCab-ko by the `Eunjeon Project`_
    to adapt to the Korean language.

    In order to use MeCab-ko within KoNLPy, follow the directions in
    :ref:`optional-installations`.

    .. code-block:: python
        :emphasize-lines: 1

        >>> # MeCab installation needed
        >>> from konlpy.tag import Mecab
        >>> mecab = Mecab()
        >>> print(mecab.morphs(u'영등포구청역에 있는 맛집 좀 알려주세요.'))
        ['영등포구', '청역', '에', '있', '는', '맛집', '좀', '알려', '주', '세요', '.']
        >>> print(mecab.nouns(u'우리나라에는 무릎 치료를 잘하는 정형외과가 없는가!'))
        ['우리', '나라', '무릎', '치료', '정형외과']
        >>> print(mecab.pos(u'자연주의 쇼핑몰은 어떤 곳인가?'))
        [('자연', 'NNG'), ('주', 'NNG'), ('의', 'JKG'), ('쇼핑몰', 'NNG'), ('은', 'JX'), ('어떤', 'MM'), ('곳', 'NNG'), ('인가', 'VCP+EF'), ('?', 'SF')]

    :param dicpath: The path of the MeCab-ko dictionary.

    .. _MeCab: https://code.google.com/p/mecab/
    .. _Eunjeon Project: http://eunjeon.blogspot.kr/
    """

    # TODO: check whether flattened results equal non-flattened
    def pos(self, phrase, flatten=True, join=False):
        """POS tagger.

        :param flatten: If False, preserves eojeols.
        :param join: If True, returns joined sets of morph and tag.
        """

        phrase = phrase.replace('영치기 영차', '영치기영차')   # a temporary solution for '영치기 영차'. '영치기 영차' consists of 2 eojeols. However, MeCab-ko analyses it as 1 eojeol. I haven't figured out the reason yet.

        if sys.version_info[0] < 3:
            phrase = phrase.encode('utf-8')
            if flatten:
                result = self.tagger.parse(phrase).decode('utf-8')
                return parse(result, join=join)
            else:
                return [parse(self.tagger.parse(eojeol).decode('utf-8'), join=join)
                        for eojeol in phrase.split()]

        else:
            if flatten:
                result = self.tagger.parse(phrase)
                return parse(result, join=join)
            else:
                ## 1) analysed result of Mecab-ko
                result = self.tagger.parse(phrase)
                result_mor_lst = result.splitlines()[:-1]
                # example of result_mor_lst'
                # ['너\tNP,*,F,너,*,*,*,*',
                #  '를\tJKO,*,T,를,*,*,*,*',
                #  '좋아해\tVV+EF,*,F,좋아해,Inflect,VV,EF,좋아하/VV/*+아/EF/*',
                #  '.\tSF,*,*,*,*,*,*,*']


                ## 2) adding indices of eojeols to result_mor_lst
                phrase2ej = phrase.split()  # eojeol list # ['너를', '좋아해.']
                cnt = 0  # index of an eojeol
                concat_mor = ""

                for i in range(len(result_mor_lst)):
                    info_str = result_mor_lst[i].split("\t")[0].strip() # '너\tNP,*,F,너,*,*,*,*'   >   '너'
                    
                    concat_mor += info_str  # concatenating morphemes until the string is equal to their original eojeol (e.g. 알 > 알+았 > 알+았+어요)

                    if concat_mor == phrase2ej[cnt]:  # If the string of concatenated morphemes is equal to its original eojeol
                        result_mor_lst[i] += "," + str(cnt)  # adding the index (cnt) of the eojeol
                        cnt += 1
                        concat_mor = ""
                    else:
                        result_mor_lst[i] += "," + str(cnt)  # adding the index (cnt) of the eojeol
                # example of 'result_mor_lst'
                # ['너\tNP,*,F,너,*,*,*,*,0',   # add an eojeol index (',0') to each morpheme analysis
                # '를\tJKO,*,T,를,*,*,*,*,0',
                # '좋아해\tVV+EF,*,F,좋아해,Inflect,VV,EF,좋아하/VV/*+아/EF/*,1',
                # '.\tSF,*,*,*,*,*,*,*,1']


                ## 3) saving the 3-D (unflattened) result:    [ [ (morpheme, POS), (morpheme, POS), ... ], ... ] 
                parsed_mor = parse(self.tagger.parse(phrase), join=join)  # 2-D (flattened) result: [ (morpheme, POS), ...]

                pos_result = list() # list for the final result: 3-D (unflattened) list
                cnt = 0  # index for a morpheme

                for i in range(len(phrase2ej)):
                    ej_mor = list() # list for an 2-D (flattened) eojeol list: [(morpheme, POS), ...]

                    while i == int(result_mor_lst[cnt].split(",")[-1]):  # While the index of a morpheme is equal to the index of an eojeol
                        if cnt > len(parsed_mor)-1:
                            break

                        ej_mor.append(parsed_mor[cnt])  # adding a (morpheme, POS) to ej_mor
                        cnt += 1

                        if cnt == len(result_mor_lst):  # If cnt is equal to the length of a phrase (or sentence)
                            break

                    pos_result.append(ej_mor) # adding the 2-D (flattened) list of an eojeol to the final 3-D (unflattened) list

                return pos_result
                # example of pos_result
                # [[('너', 'NP'), ('를', 'JKO')], [('좋아해', 'VV+EF'), ('.', 'SF')]]


    def morphs(self, phrase):
        """Parse phrase to morphemes."""

        return [s for s, t in self.pos(phrase)]

    def nouns(self, phrase):
        """Noun extractor."""

        tagged = self.pos(phrase)
        return [s for s, t in tagged if t.startswith('N')]

    def __init__(self, dicpath='/usr/local/lib/mecab/dic/mecab-ko-dic'):
        self.dicpath = dicpath
        try:
            self.tagger = Tagger('-d %s' % dicpath)
            self.tagset = utils.read_json('%s/data/tagset/mecab.json' % utils.installpath)
        except RuntimeError:
            raise Exception('The MeCab dictionary does not exist at "%s". Is the dictionary correctly installed?\nYou can also try entering the dictionary path when initializing the Mecab class: "Mecab(\'/some/dic/path\')"' % dicpath)
        except NameError:
            raise Exception('Install MeCab in order to use it: http://konlpy.org/en/latest/install/')

    def __setstate__(self, state):
        """just reinitialize."""

        self.__init__(dicpath=state['dicpath'])

    def __getstate__(self):
        """store arguments."""

        return {'dicpath': self.dicpath}
