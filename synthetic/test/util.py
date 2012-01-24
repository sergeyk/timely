import itertools
from nose.tools import *
import numpy as np

import synthetic.util as ut

def test_random_subset_up_to_N():
  Ns = [1,2,10,100]
  max_nums = [1,50]
  for N,max_num in itertools.product(Ns, max_nums):
    r = ut.random_subset_up_to_N(N, max_num)
    assert(len(r)==min(N,max_num))
    assert(max(r)<=N)
    assert(min(r)>=0)

def test_random_subset_up_to_N_exception():
  Ns = [-2, 0]
  max_nums = [1,50]
  for N,max_num in itertools.product(Ns, max_nums):
    assert_raises(ValueError, ut.random_subset_up_to_N, N, max_num)
  Ns = [1, 10, 100]
  max_nums = [-4, 0]
  for N,max_num in itertools.product(Ns, max_nums):
    assert_raises(ValueError, ut.random_subset_up_to_N, N, max_num)

def test_random_subset():
  l = range(100,120)
  max_num = 10
  r = ut.random_subset(l, max_num)
  assert(len(r)==min(len(l),max_num))
  assert(max(r)<=max(l))
  assert(min(r)>=min(l))

  l = np.array(range(0,120))
  max_num = 10
  r = ut.random_subset(l, max_num)
  assert(len(r)==min(len(l),max_num))
  assert(max(r)<=max(l))
  assert(min(r)>=min(l))

def test_random_subset_ordered():
  l = range(100,120)
  max_num = 10
  r = ut.random_subset(l, max_num, ordered=True)
  assert(len(r)==min(len(l),max_num))
  assert(max(r)<=max(l))
  assert(min(r)>=min(l))
  assert(sorted(r)==r)
