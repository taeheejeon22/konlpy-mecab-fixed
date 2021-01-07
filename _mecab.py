# -*- coding: utf-8 -*-
from __future__ import absolute_import

import itertools     # for list flattening
import re            # for clearing unnecessary attrs (e.g. 불태워/VV/*, 터/NNP/인명)

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
         'first_pos',   # 첫 번째 품사
         'last_pos',    # 마지막 품사
         'original',    # 원형
         'indexed']     # 인덱스 표현

regexp = re.compile(".+(?=/[^A-Z])") # a pattern for only morphemes and their POS (e.g. 불태워/VV/* > 불태워/VV)


######################## the original code ##############################
# def parse(result, allattrs=False, join=False):
#     def split(elem, join=False):
#         if not elem: return ('', 'SY')
#         s, t = elem.split('\t')
#         if join:
#             return s + '/' + t.split(',', 1)[0]
#         else:
#             return (s, t.split(',', 1)[0])

#     return [split(elem, join=join) for elem in result.splitlines()[:-1]]
#########################################################################


# parse(): a function for getting the morpheme/POS list of its original sentence
"""
e.g. 이게 뭔지 알아.
>
[('이것', 'NP'),
('이', 'JKS'),
('뭐', 'NP'),
('이', 'VCP'),
('ㄴ지', 'EC'),
('알', 'VV'),
('아', 'EF'),
('.', 'SF')])
"""

def parse(result, allattrs=False, join=False):
        # result: an analysed result of a sentence (e.g. 이게 뭔지 알아. > 이게\tNP+JKS,*,F,이게,Inflect,NP,JKS,이것/NP/*+이/JKS/*\n뭔지\tNP+VCP+EC,*,F,뭔지,Inflect,NP,EC,뭐/NP/*+이/VCP/*+ㄴ지/EC/*\n알\tVV,*,T,알,*,*,*,*\n아\tEF,*,F,아,*,*,*,*\n.\tSF,*,*,*,*,*,*,*\nEOS\n)
             
    def split(elem, join=False):
            # elem: an analysed result of an eojeol (e.g. 뭔지 > 뭔지\tNP+VCP+EC,*,F,뭔지,Inflect,NP,EC,뭐/NP/*+이/VCP/*+ㄴ지/EC/*)

        if not elem: return ('', 'SY')
        s, t = elem.split('\t') # s: an eojeol (e.g. 위한)   # t: analysed resulf of an eojeol (e.g. VV+ETM,*,T,위한,Inflect,VV,ETM,위하/VV/*+ᆫ/ETM/*)
        lst_morpos = t.split(',')[-1].split("+")  # splitting the last attr (인덱스 표현) of 't' by morpheme (e.g. 위하/VV/*+ᆫ/ETM/* > ["위하/VV/*", "ᆫ/ETM/*"])
        if join:
            if not t.split(',')[4].startswith("Inflect"): # If an eojeol is not Inflect (= a concatenation of morphemes is equal to its original eojeol. e.g. 해수욕장 == 해수 + 욕 + 장)
                return s + '/' + t.split(',')[0]  # eojeol + / + POS (e.g. 위한/VV+ETM)
            else:   # If an eojeol is Inflect (= a concatenation of morphemes is not equal to its original eojeol) (e.g. 불태워졌다 != 불태우 + 어 + 지 + 었 + 다)
                return [regexp.search(x).group() for x in lst_morpos]   # make a list of morphemes with their POSs (e.g. ['줍/VV', '어서/EC'])

        else:
            if not t.split(',')[4].startswith("Inflect"):
                return (s, t.split(',')[0])
            else:
                return [tuple(regexp.search(x).group().split("/")) for x in lst_morpos]

    return list ( itertools.chain.from_iterable( [[x] if type(x) != list else x  for x in [split(elem, join=join) for elem in result.splitlines()[:-1]] ] ) )
                                                # making a 2-D (eojeol, morpheme/POS) list
                # flattening the list to a 1-D (morphme/POS) list
                                                


######################## the original code ##############################
# class Mecab():
#     """Wrapper for MeCab-ko morphological analyzer.

#     `MeCab`_, originally a Japanese morphological analyzer and POS tagger
#     developed by the Graduate School of Informatics in Kyoto University,
#     was modified to MeCab-ko by the `Eunjeon Project`_
#     to adapt to the Korean language.

#     In order to use MeCab-ko within KoNLPy, follow the directions in
#     :ref:`optional-installations`.

#     .. code-block:: python
#         :emphasize-lines: 1

#         >>> # MeCab installation needed
#         >>> from konlpy.tag import Mecab
#         >>> mecab = Mecab()
#         >>> print(mecab.morphs(u'영등포구청역에 있는 맛집 좀 알려주세요.'))
#         ['영등포구', '청역', '에', '있', '는', '맛집', '좀', '알려', '주', '세요', '.']
#         >>> print(mecab.nouns(u'우리나라에는 무릎 치료를 잘하는 정형외과가 없는가!'))
#         ['우리', '나라', '무릎', '치료', '정형외과']
#         >>> print(mecab.pos(u'자연주의 쇼핑몰은 어떤 곳인가?'))
#         [('자연', 'NNG'), ('주', 'NNG'), ('의', 'JKG'), ('쇼핑몰', 'NNG'), ('은', 'JX'), ('어떤', 'MM'), ('곳', 'NNG'), ('인가', 'VCP+EF'), ('?', 'SF')]

#     :param dicpath: The path of the MeCab-ko dictionary.

#     .. _MeCab: https://code.google.com/p/mecab/
#     .. _Eunjeon Project: http://eunjeon.blogspot.kr/
#     """

#     # TODO: check whether flattened results equal non-flattened
#     def pos(self, phrase, flatten=True, join=False):
#         """POS tagger.

#         :param flatten: If False, preserves eojeols.
#         :param join: If True, returns joined sets of morph and tag.
#         """

#         if sys.version_info[0] < 3:
#             phrase = phrase.encode('utf-8')
#             if flatten:
#                 result = self.tagger.parse(phrase).decode('utf-8')
#                 return parse(result, join=join)
#             else:
#                 return [parse(self.tagger.parse(eojeol).decode('utf-8'), join=join)
#                         for eojeol in phrase.split()]
#         else:
#             if flatten:
#                 result = self.tagger.parse(phrase)
#                 return parse(result, join=join)
#             else:
#                 return [parse(self.tagger.parse(eojeol), join=join)
#                         for eojeol in phrase.split()]

#     def morphs(self, phrase):
#         """Parse phrase to morphemes."""

#         return [s for s, t in self.pos(phrase)]

#     def nouns(self, phrase):
#         """Noun extractor."""

#         tagged = self.pos(phrase)
#         return [s for s, t in tagged if t.startswith('N')]

#     def __init__(self, dicpath='/usr/local/lib/mecab/dic/mecab-ko-dic'):
#         self.dicpath = dicpath
#         try:
#             self.tagger = Tagger('-d %s' % dicpath)
#             self.tagset = utils.read_json('%s/data/tagset/mecab.json' % utils.installpath)
#         except RuntimeError:
#             raise Exception('The MeCab dictionary does not exist at "%s". Is the dictionary correctly installed?\nYou can also try entering the dictionary path when initializing the Mecab class: "Mecab(\'/some/dic/path\')"' % dicpath)
#         except NameError:
#             raise Exception('Install MeCab in order to use it: http://konlpy.org/en/latest/install/')

#     def __setstate__(self, state):
#         """just reinitialize."""

#         self.__init__(dicpath=state['dicpath'])

#     def __getstate__(self):
#         """store arguments."""

#         return {'dicpath': self.dicpath}
#########################################################################



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

        phrase = phrase.replace('\u3000', ' ')  # replacing ideographic spaces into blanks
        phrase = phrase.replace('영치기 영차', '영치기영차')   # a temporary solution for '영치기 영차'. '영치기 영차' consists of 2 eojeol. However, MeCab-ko analyses it as 1 eojeol. I haven't figured out the reason yet.
                
        # self = Mecab()
        if sys.version_info[0] >= 3: # for Python 3
            result = self.tagger.parse(phrase)  # an analysed result of a phrase (or a sentence) (e.g. 이게 뭔지 알아. > 이게\tNP+JKS,*,F,이게,Inflect,NP,JKS,이것/NP/*+이/JKS/*\n뭔지\tNP+VCP+EC,*,F,뭔지,Inflect,NP,EC,뭐/NP/*+이/VCP/*+ㄴ지/EC/*\n알\tVV,*,T,알,*,*,*,*\n아\tEF,*,F,아,*,*,*,*\n.\tSF,*,*,*,*,*,*,*\nEOS\n)
            result = result.replace("ᆯ", "ㄹ").replace("ᆫ", "ㄴ") # converting final consonant characters to ordinary single characters

            if flatten: # flatten = True. If you want to get a 1-D (morpheme/POS) result
                            # e.g.
                            # [('이것', 'NP'),
                            # ('이', 'JKS'),
                            # ('뭐', 'NP'),
                            # ('이', 'VCP'),
                            # ('ㄴ지', 'EC'),
                            # ('알', 'VV'),
                            # ('아', 'EF'),
                            # ('.', 'SF')])
                return parse(result, join=join)
            else:   # flatten = False. If you want to get a 2-D (eojeol, morpheme/POS) result
                        # e.g.
                        # [[('이것', 'NP'), ('이', 'JKS')],
                        # [('뭐', 'NP'), ('이', 'VCP'), ('ᆫ지', 'EC')],
                        # [('알', 'VV'), ('아', 'EF'), ('.', 'SF')]]

                ## 1) an analysed result of Mecab-ko
                    # e.g.
                    # ['이게\tNP+JKS,*,F,이게,Inflect,NP,JKS,이것/NP/*+이/JKS/*',
                    # '뭔지\tNP+VCP+EC,*,F,뭔지,Inflect,NP,EC,뭐/NP/*+이/VCP/*+ㄴ지/EC/*',
                    # '알\tVV,*,T,알,*,*,*,*',
                    # '아\tEF,*,F,아,*,*,*,*',
                    # '.\tSF,*,*,*,*,*,*,*']
                result_mor_lst = result.splitlines()[:-1]
                result_mor_lst = [x.replace('영치기 영차', '영치기영차') for x in result_mor_lst]   # a temporary solution for '영치기 영차'. '영치기 영차' consists of 2 eojeol. However, MeCab-ko analyses it as 1 eojeol. I haven't figured out the reason yet.


                ## 2) adding indices of eojeols to result_mor_lst
                phrase2ej = phrase.split()  # 어절 리스트 # ['먹을', '수', '있다']        
                cnt = 0 # index of an eojeol
                concat_mor = ''               
                
                for i in range(len(result_mor_lst)):
                    info_str = result_mor_lst[i].split("\t")[0]
                    info_str = info_str.strip()
                    
                    concat_mor += info_str  # concatenating morphemes until the string is equal to their original eojeol (e.g. 알 > 알았 > 알았어요)

                    if concat_mor == phrase2ej[cnt]:    # If the string of concatenated morphemes is equal to their original eojeol
                        result_mor_lst[i] += "," + str(cnt) # adding the index (cnt) of the eojeol
                        cnt += 1
                        concat_mor = ''
                    else:
                        result_mor_lst[i] += "," + str(cnt) # adding the index (cnt) of the eojeol


                ## 3) splitting the result_mor_lst by morpheme for the case when the string of concatenated morphmese is not equal to their original eojeol (e.g. 뭔지 != 뭐 + 이 + ㄴ지)
                for i in range(len(result_mor_lst)):
                    splited = result_mor_lst[i].split(",")
                    if splited[4] == 'Inflect': # If an eojeol is Inflect (= a concatenation of morphemes is not equal to its original eojeol. (e.g. 뭔지 != 뭐 + 이 + ㄴ지)
                        mors = [x.split('/')[0] for x in splited[7].split('+')]                        
                        for_replace = []
                        for j in range(len(mors)):
                            for_replace += [ mors[j] + '\t' + result_mor_lst[i].split('\t')[-1]]
                        result_mor_lst[i] = for_replace
                                    
                result_mor_lst_1 = []   # 형태소 단위로 쪼개 놓은 것 저장할 list
                for i in range(len(result_mor_lst)):
                    if not type(result_mor_lst[i]) == list:
                        result_mor_lst_1.append(result_mor_lst[i])
                    else:
                        for j in range(len(result_mor_lst[i])):
                            result_mor_lst_1.append(result_mor_lst[i][j])


                """
                e.g.
                ['이게\tNP+JKS,*,F,이게,Inflect,NP,JKS,이것/NP/*+이/JKS/*,0',                    ['이것\tNP+JKS,*,F,이게,Inflect,NP,JKS,이것/NP/*+이/JKS/*,0',
                                                                                            '이\tNP+JKS,*,F,이게,Inflect,NP,JKS,이것/NP/*+이/JKS/*,0',
                '뭔지\tNP+VCP+EC,*,F,뭔지,Inflect,NP,EC,뭐/NP/*+이/VCP/*+ㄴ지/EC/*,1',            '뭐\tNP+VCP+EC,*,F,뭔지,Inflect,NP,EC,뭐/NP/*+이/VCP/*+ㄴ지/EC/*,1',
                                                                                        >     '이\tNP+VCP+EC,*,F,뭔지,Inflect,NP,EC,뭐/NP/*+이/VCP/*+ㄴ지/EC/*,1',
                                                                                            'ㄴ지\tNP+VCP+EC,*,F,뭔지,Inflect,NP,EC,뭐/NP/*+이/VCP/*+ㄴ지/EC/*,1',
                '알\tVV,*,T,알,*,*,*,*,2',                                                     '알\tVV,*,T,알,*,*,*,*,2',
                '아\tEF,*,F,아,*,*,*,*,2',                                                     '아\tEF,*,F,아,*,*,*,*,2',
                '.\tSF,*,*,*,*,*,*,*,2']                                                      '.\tSF,*,*,*,*,*,*,*,2']
                """

                ## 4) saving the 2-D (eojeol, morpheme/POS) result 
                parsed_mor = parse(self.tagger.parse(phrase), join=join)    # the 1-D (morpheme/POS) result

                pos_result = [] # a 2-D list for the final result
                cnt = 0 # index for a morpheme
                for i in range(len(phrase2ej)):
                    ej_mor = [] # a 1-D (morpheme/POS) list of an eojeol
                    while i == int( result_mor_lst_1[cnt].split(",")[-1]):  # While the index of a morpheme is equal to the index of an eojeol
                        ej_mor.append(parsed_mor[cnt])  # adding a morpheme/POS to ej_mor
                        cnt += 1
                        if cnt == len(result_mor_lst_1): # If cnt is equal to the lengh of a phrase (or sentence)
                            break
                    pos_result.append(ej_mor)   # adding the 1-D (morpheme/POS) list to the final 2-D (eojeol, morpheme/POS) list

                return pos_result
                
                """
                an example of pos_result                    

                [[('이것', 'NP'), ('이', 'JKS')],
                [('뭐', 'NP'), ('이', 'VCP'), ('ᆫ지', 'EC')],
                [('알', 'VV'), ('아', 'EF'), ('.', 'SF')]]
                """
        
        else: # There is no code for Python 2. I strongly recommend you to use Python 3.
            phrase = phrase.encode('utf-8')
            if flatten:
                result = self.tagger.parse(phrase).decode('utf-8')
                return parse(result, join=join)
            else:
                return [parse(self.tagger.parse(eojeol).decode('utf-8'), join=join)
                        for eojeol in phrase.split()]


    def morphs(self, phrase):
        """Parse phrase to morphemes."""

        return [s for s, t in self.pos(phrase)]

    def nouns(self, phrase):
        """Noun extractor."""

        tagged = self.pos(phrase)
        return [s for s, t in tagged if t.startswith('N')]

    def __init__(self, dicpath='/usr/local/lib/mecab/dic/mecab-ko-dic'):
        try:
            self.tagger = Tagger('-d %s' % dicpath)
            self.tagset = utils.read_json('%s/data/tagset/mecab.json' % utils.installpath)
        except RuntimeError:
            raise Exception('The MeCab dictionary does not exist at "%s". Is the dictionary correctly installed?\nYou can also try entering the dictionary path when initializing the Mecab class: "Mecab(\'/some/dic/path\')"' % dicpath)
        except NameError:
            raise Exception('Install MeCab in order to use it: http://konlpy.org/en/latest/install/')
