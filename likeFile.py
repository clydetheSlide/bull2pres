#!/usr/bin/env python3
# File: likeFile.py
#
# Given a filename, look for an existing file that is similar enough that it is probably what is intended.
# Check for changes in capitalization,
# commas, spaces
# lack of or extra suffix
# minor spelling errors
#
# return the name of the existing file 
#    and a numerical rating of how good it is (0 probably not - 5 almost certainly is)
#
import os, sys
from enum import Enum
from difflib import SequenceMatcher

class Ratings (Enum):
    PERFECT = 5
    SUFFIX = 5
    CAPS = 4
    SPACES = 4
    COMMAS = 3
    SPELLING = 1
    NOT = 0

MATCHING_THRESHOLD=.8
MATCHING_BLOCK_THRESHOLD=5
MATCHING_SUM_THRESHOLD=5
def likeFiles(name, path="./", suffix=".xml", debug=False
  , thresh=MATCHING_THRESHOLD
  , threshB=MATCHING_BLOCK_THRESHOLD
  , threshS=MATCHING_SUM_THRESHOLD
  ):
    '''compare name with other files in path
       to determine if name might exist with a minor difference in spelling.
       returns a tuple:(newName, Rating, score)
       where newName is the matched file name (or the original if no match)
             Rating is an figure of merit
	     score is an auxiliary figure of merit 
       Rating.value == 0 indicates poor match; file probably doesn't exist
    '''
    found=[]
    # get list of files in the path folder
    if debug: print(suffix)
    for each in os.listdir(path):
        # compare name to each, with and without suffix
        if name==each:return each,Ratings.PERFECT,.99
        if name+suffix==each:return each,Ratings.SUFFIX,.99
        result =likeFile(name,each,suffix,debug=debug
  , thresh=thresh
  , threshB=threshB
  , threshS=threshS
)
        if result[1] == Ratings.PERFECT: return each,Ratings.PERFECT,.99
        if result[1].value > Ratings.NOT.value:
            found.append(result)
    if debug: print(len(found))
    if len(found)>0: 
        if debug:
            print('Unsorted potential matches')
            for (tit,rat,sc) in found:
                #print('   %s  %d   %f'%(tit,rat.value,sc))
                print('   {0}  {1:d}   {2:f}'.format(tit,rat.value,sc))
        #if len(found)>1: print('more than one potential match.\nBut no ranking method developed so useing the first')
        found.sort(key=lambda tup:tup[1].value+tup[2],reverse=True)
        return found[0]
    return name,Ratings.NOT,0.

def likeFile(name, testee, suffix=".xml", debug=True 
  , thresh=MATCHING_THRESHOLD
  , threshB=MATCHING_BLOCK_THRESHOLD
  , threshS=MATCHING_SUM_THRESHOLD
  ):
    ''' Compare name with testee, 
    Return a tuple (FOUND, SCORE, SUBSCORE)
    where the string is the match.
    A Perfect match warrants a SCORE of PERFECT (= 5).
    Differences in capitalization warrant 4.
    Extra spaces or lack thereof warrant 3.
    Extra commas or lack thereof warrant 2.
    Small spelling difference warrant a SCORE of 1 and a SUBSCORE value < .99
    If there is no match, FOUND is name, and SCORE =0.
    '''
    #        different capitalization
    nlower=name.lower()
    tlower=testee.lower()
    if(debug):
        print(nlower, end=' ')
        print('T: '+tlower)
    if nlower == tlower: return testee,Ratings.CAPS,.99
    if nlower+suffix == tlower: return testee,Ratings.CAPS,.99
    
    #        added/missing spaces: remove all spaces from both and compare
    nlower=nlower.replace(' ','')
    tlower=tlower.replace(' ','')
    if(debug):
        print(nlower,end=' ')
        print(nlower+suffix,end=' ')
        print('T: '+tlower)
    if nlower==tlower: 
        return testee,Ratings.SPACES,.99
    if nlower+suffix==tlower: 
        return testee,Ratings.SPACES,.99
    
    #        added commas, remove all commas from both and compare
    nlower=nlower.replace(',','')
    tlower=tlower.replace(',','')
    if nlower==tlower: 
        return testee,Ratings.COMMAS,.99
    if nlower+suffix==tlower: 
        return testee,Ratings.COMMAS,.99
    
    #      a couple of extraneous letters
    sm=SequenceMatcher(None,name,testee)
    blocks=sm.get_matching_blocks()
    rating=sm.ratio()
    if rating > thresh:
        if debug:print('%d %s'%(len(blocks),tlower))
        if len(blocks)<threshB:
            sum=0
            for b in blocks: sum+=b[2]
            if debug:print('blocks %d, sum %d %s'%(len(blocks),sum,tlower))
            if abs(sum-len(tlower))<threshS: return testee,Ratings.SPELLING,rating
    sm=SequenceMatcher(None,nlower+suffix,tlower)
    blocks=sm.get_matching_blocks()
    rating=sm.ratio()
    if rating > thresh:
        if debug:print('%d %s'%(len(blocks),tlower))
        if len(blocks)<threshB:
            sum=0
            for b in blocks: sum+=b[2]
            if debug:print('sum %d %s'%(sum,tlower))
            if abs(sum-len(tlower))<threshS: return testee,Ratings.SPELLING,rating
    return name,Ratings.NOT,0.

if __name__=='__main__':
    testee = 'likeFile'
    if len(sys.argv)>1: testee=sys.argv[1]
    if len(sys.argv)>5:
        found,score,rating=likeFiles(testee,suffix='.xml'
        ,debug=True
        ,path=sys.argv[2]
        ,thresh=float(sys.argv[3])
        ,threshB=float(sys.argv[4])
        ,threshS=float(sys.argv[5])
        )
    elif len(sys.argv)>2:
        found,score,rating=likeFiles(testee,suffix='.xml'
        ,debug=True
        ,path=sys.argv[2]
        )
    else:
        found,score,rating=likeFiles(testee,suffix='.xml'
        ,debug=True
        )
    print(found)
    print(score)
    print(score.value)
