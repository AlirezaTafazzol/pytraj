from __future__ import absolute_import 
from .gdt import gdt

def calc_score(frame0=None, frame1=None, mask="*", 
               top=None, score="gdtscore", *args, **kwd):
    if score == 'gdtscore':
        _score = 1
    elif score == 'tmscore':
        _score = 2
    elif score == 'maxsub':
        _score = 3

    atm = top(mask)
    arr0 = frame0.get_subframe(atm).coords

    arr1 = frame1.get_subframe(atm).coords
    return gdt(arr0, arr1, 1, len(arr0)/3, _score)[0]
