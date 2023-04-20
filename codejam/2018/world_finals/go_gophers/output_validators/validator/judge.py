"""judge.py for the Gopher Trace interactive judge.
"""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (small), 1 (large) or -2 (test mode).

import fractions
import random
import sys

NUM_CASES = 10
MIN_N, MAX_N = (2, 25)
MIN_TASTE, MAX_TASTE = (1, 10**6)
S = 10**5
EATEN = 1
UNEATEN = 0
WRONG_ANSWER = -1

INVALID_LINE_ERROR = "Couldn't read a valid line."
NOT_INTEGER_ERROR = "Not an integer: {}".format
OUT_OF_RANGE_ERROR = "Value {} is out of range.".format
TOO_MANY_SNACKS_ERROR = "Used too many snacks."
WRONG_GUESS_ERROR = "Wrong guess of {} gophers (true value: {})".format
WRONG_NUM_TOKENS_ERROR = "Wrong number of tokens: {}. Expected 1.".format


def ReadValue(line):
  t = line.split()
  if len(t) != 1:
    return WRONG_NUM_TOKENS_ERROR(len(t))
  try:
    v = int(t[0])
  except:
    return NOT_INTEGER_ERROR(t[0] if len(t[0]) < 100 else t[0][0:100])
  if v < -MAX_N or -MIN_N < v < MIN_TASTE or MAX_TASTE < v:
    return OUT_OF_RANGE_ERROR(v)
  return v


def TestReadValue():
  assert ReadValue("-25") == -25
  assert ReadValue("-2") == -2
  assert ReadValue("1") == 1
  assert ReadValue(str(MAX_TASTE)) == MAX_TASTE
  assert ReadValue("11 ") == 11
  assert ReadValue(" 11") == 11
  for v, expected in (("1 1", WRONG_NUM_TOKENS_ERROR(2)),
                      ("a11", NOT_INTEGER_ERROR("a11")),
                      ("11a", NOT_INTEGER_ERROR("11a")),
                      ("abcdefghij" * 11, NOT_INTEGER_ERROR("abcdefghij" * 10)),
                      ("-26", OUT_OF_RANGE_ERROR(-26)),
                      ("-1", OUT_OF_RANGE_ERROR(-1)),
                      ("0", OUT_OF_RANGE_ERROR(0)),
                      (str(MAX_TASTE + 1), OUT_OF_RANGE_ERROR(MAX_TASTE + 1))):
    result = ReadValue(v)
    assert result == expected, (
      "TestReadValue({}): expected {}, got {}".format(
        v, expected, result))


def RandomShuffle(a):
  random.shuffle(a)
  # To make this different from the randomization method used publicly in the
  # local testing tool, do some swaps. This does not break our "uniformly at
  # random" guarantee.
  if len(a) > 1:
    for _ in xrange(10):
      i1, i2 = random.sample(xrange(len(a)), 2)
      a[i1], a[i2] = a[i2], a[i1]


def Noop(a):
  return


def Reverse(a):
  a.reverse()


def RunCase(s, taste_levels, reorder_func=RandomShuffle, test=False, test_input=[]):

  output_values = []

  def Input():
    if not test:
      return raw_input()
    else:
      return test_input.pop(0)

  def Output(line):
    if not test:
      print line
      sys.stdout.flush()
    else:
      output_values.append(line)

  snacks = 0
  n = len(taste_levels)
  Output(s)
  err = None

  while True:
    if snacks % n == 0:
      reorder_func(taste_levels)
    try:
      line = Input()
    except:
      err = INVALID_LINE_ERROR
      break
    v = ReadValue(line)
    if isinstance(v, str):
      err = v
      break
    if v < 0:  # The submitted value is a guess.
      if abs(v) == n:
        err = None  # Correct.
        break
      err = WRONG_GUESS_ERROR(abs(v), n)
      break
    else:  # The submitted value is a snack quality level.
      snacks += 1
      if snacks > s:
        err = TOO_MANY_SNACKS_ERROR
        break
      Output(EATEN if v >= taste_levels[snacks % n] else UNEATEN)

  if err:
    Output(WRONG_ANSWER)
  if not test:
    return err
  else:
    return err, output_values


def TestRunCase():
  for s, taste_levels, test_input, expected in (
    (4, [1, 2], [], INVALID_LINE_ERROR),
    (4, [1, 2], ["HELLO"], NOT_INTEGER_ERROR("HELLO")),
    (4, [1, 2], ["-4"], WRONG_GUESS_ERROR(4, 2)),
    (4, [1, 2], ["-2"], None),
    (4, [1, 2], ["1", "1", "1", "1", "-2"], None),
    (4, [1, 2], ["1", "1", "1", "1", "1", "-2"], TOO_MANY_SNACKS_ERROR)):
    result, _ = RunCase(s, taste_levels, test=True, test_input=test_input[:])
    assert result == expected, (
      "TestRunCase(s={}, taste_levels={}, test_input={}): "
      "expected {}, got {}".format(
        s, taste_levels, test_input, expected, result))

  # Check permutations.
  result, output_values = RunCase(
      100, [1, 2, 2, 3, 3, 3, 4, 5, MAX_TASTE - 1, MAX_TASTE], test=True,
      test_input = ["3"] * 100 + ["-10"])
  assert result is None, (
      "TestRunCase(permutations): got error {}".format(result))
  assert output_values[0] == 100
  per_round_outputs = [output_values[1 + 10 * i : 1 + 10 * (i + 1)]
                            for i in xrange(10)]
  for pro in per_round_outputs:
    assert pro.count(1) == 6
    assert pro.count(0) == 4
  assert per_round_outputs.count(per_round_outputs[0]) != 10


def RunCases(cases):
  for i, (taste_levels, reorder_func) in enumerate(cases, 1):
    result = RunCase(S, list(taste_levels), reorder_func)
    if result:
      return "Case #{} ({}) failed: {}".format(i, sorted(taste_levels), result)
  try:
    extra_input = raw_input()
  except EOFError:
    return None
  except Exception:  # pylint: disable=broad-except
    return "Exception raised while reading input after all cases finish."
  return "Additional input after all cases finish: {}".format(extra_input[:100])


def Set1Cases():
  cases = [
      (1, 2),
      (MAX_TASTE - 1, MAX_TASTE, MAX_TASTE - 2),
      tuple(xrange(86427, 86452)),
      tuple(xrange(23526, 23526 + 256*24, 256)),
      tuple(MAX_TASTE - 2**i for i in xrange(20)),
      tuple(2 + i * (i+1) / 2 for i in xrange(24)),
      tuple(range(1000, 1013) + range(MAX_TASTE - 1012, MAX_TASTE - 1000)),
      (1, 2, MAX_TASTE - 1, MAX_TASTE),
      tuple((MAX_TASTE - 1) * i / 4 + 1 for i in xrange(5)),
      tuple((MAX_TASTE - 1) * i / 23 + 1 for i in xrange(24))
  ]
  return [(c, RandomShuffle) for c in cases]


def CheckSet2(taste_levels):
  counts = {x : taste_levels.count(x) for x in taste_levels}.values()
  gcd = reduce(fractions.gcd, counts)
  if gcd != 1:
    return ("The multiset of taste levels is a multiple (gcd {}) of "
                "some other set.".format(gcd))
  return None


def Interject(rep, singles):
  return sum(tuple(rep + (s,) for s in singles), ())


def CheckInterject():
  assert Interject((1,2,3), (4,5)) == (1,2,3,4,1,2,3,5)
  assert Interject((1,2,3), (4,)) == (1,2,3,4)
  assert Interject((1,), (4,5,6)) == (1,4,1,5,1,6)
  assert Interject((), (4,5,6)) == (4,5,6)
  assert Interject((1,2,3), ()) == ()
  assert Interject((1,), (2,)) == (1,2)


def ApplyToSlices(func, slices):
  def FuncToSlices(l):
    slice_size = len(l) / slices
    for i in xrange(slices):
      orig = l[i * slice_size:(i + 1) * slice_size]
      func(orig)
      l[i * slice_size:(i + 1) * slice_size] = orig
  return FuncToSlices


def CheckApplyToSlices():
  def AfterApplied(f):
    def g(l):
      x = list(l)
      f(x)
      return x
    return g
  HalfReversed = AfterApplied(ApplyToSlices(Reverse, 2))
  assert HalfReversed([]) == []
  assert HalfReversed([1,2]) == [1,2]
  assert HalfReversed([1,2,3,4]) == [2,1,4,3]
  assert HalfReversed([1,2,3,4,5]) == [2,1,4,3,5]
  assert HalfReversed([1,2,3,4,5,6]) == [3,2,1,6,5,4]
  assert HalfReversed([1,2,3,4,5,6,7]) == [3,2,1,6,5,4,7]
  ThirdReversed = AfterApplied(ApplyToSlices(Reverse, 3))
  assert ThirdReversed([]) == []
  assert ThirdReversed([1,2,3]) == [1,2,3]
  assert ThirdReversed([1,2,3,4,5,6,7,8,9]) == [3,2,1,6,5,4,9,8,7]
  assert ThirdReversed([1,2,3,4,5,6,7,8,9,10]) == [3,2,1,6,5,4,9,8,7,10]
  def SwapFirstTwo(x):
    x[0], x[1] = x[1], x[0]
  HalfFirstTwoSwapped = AfterApplied(ApplyToSlices(SwapFirstTwo, 2))
  assert HalfFirstTwoSwapped([1,2,3,4,5]) == [2,1,4,3,5]
  assert HalfFirstTwoSwapped([1,2,3,4,5,6]) == [2,1,3,5,4,6]
  assert HalfFirstTwoSwapped([1,2,3,4,5,6,7,8,9,10]) == [2,1,3,4,5,7,6,8,9,10]


def OnceInAWhile(f):
  def NewF(x):
    if random.randrange(10) == 0:
      f(x)
  return NewF


def Set2Cases():
  MX = MAX_TASTE
  cases = [
      ((1, 1, 3), RandomShuffle),
      ((MX, MX - 1, MX - 1, MX - 2), ApplyToSlices(RandomShuffle, 2)),
      ((1,) * 4 + (MX / 3, 2 * MX / 3) + (MX,) * 6, Reverse),
      (Interject((2,) * 3 + (MX - 1,) * 2, (MX / 2, MX / 2 + 1)),
       ApplyToSlices(Reverse, 2)),
      (Interject((MX / 5,) * 4 + (4 * MX / 5,) * 2 + (3 * MX / 5,),
                 (2 * MX / 5, 2 * MX / 5 + 1, 2 * MX / 5 + 2)),
                 ApplyToSlices(Reverse, 3)),
      (Interject((17, 19, 2048, 2049, MX / 2 - 1000, MX / 2 + 1024,
                  3 * MX / 4 + 9, 3 * MX / 4 + 10, 3 * MX / 4 + 11,
                  999979, 999983), (MX / 2 - 3, MX / 2 - 2)),
                  Noop),
      (tuple(xrange(MX - 86452, MX - 86427)), Noop),  # Breaks TimonKnigge.
      (Interject(tuple(xrange(MX - 12, MX - 4)) + (MX - 1, MX - 2),
                 (MX - 4, MX - 3)), OnceInAWhile(ApplyToSlices(Reverse, 2))),
      (Interject((100000, 200000, 800000, 900000),
                 (300000, 400000, 500000, 600000, 700000)),
       ApplyToSlices(Reverse, 5)),
      ((8, 8**4, 8**6) * 3 + (8**2, 8**5) * 4 + (8**3,) * 5,
       OnceInAWhile(RandomShuffle))
  ]
  return cases


def TestCheckSet2():
  # Note: (1,) would pass this, despite being an invalid set, because it is
  # not CheckSet2's job to check the length of the set.
  for ok_set in (
      (1,) * 24 + (2,),
      (3, 3, 3, 2, 2),
      (2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6),
      (1, 2, 2, 3, 3, 3),
      (1, 2, 2),
      (1, 2, 2, 22, 22, 222, 222, 2222, 2222),
      (2, 2, 22, 22, 3, 3, 3, 33, 33, 33),
  ):
    assert CheckSet2(ok_set) is None, (
        "TestCheckSet2 found error in OK set: {}".format(ok_set))
  for bad_set in (
      (9999, 9999),
      (123456,)*25,
      (2, 2, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 8, 8, 8, 8, 8, 8, 8, 8),
      (2, 2, 22, 22, 222, 222, 2222, 2222),
      (10, 10, 10, 10, 10, 5, 5, 5, 5, 5, 10, 10, 10, 10, 10),
  ):
    assert isinstance(CheckSet2(bad_set), str), (
      "TestCheckSet2 failed to reject bad set: {}".format(bad_set))


def IsReorderFunc(reorder_func):
  for tl in ([], range(5), range(5) + range(7), [1000000]):
    random.shuffle(tl)
    orig = sorted(tl)
    for _ in xrange(20):
      reorder_func(tl)
      if sorted(tl) != orig: return False
  return True


def CheckIsReorderFunc():
  assert IsReorderFunc(RandomShuffle)
  assert IsReorderFunc(Noop)
  assert IsReorderFunc(Reverse)
  for new_list in (lambda x: x[1:] + x[-1:], lambda x: [0] * len(x),
                   lambda x: []):
    def ApplyNewList(x):
      x[:] = new_list(x)
    assert not IsReorderFunc(ApplyNewList)


def ValidateCases():
  seen_cases = set()
  for ts, cases in enumerate((Set1Cases(), Set2Cases()), 1):
    assert len(cases) == NUM_CASES, (
        "Set {}: Did not use all {} cases".format(ts, NUM_CASES))
    for c, (tl, reorder_func) in enumerate(cases, 1):
      assert IsReorderFunc(reorder_func)
      taste_levels = tuple(sorted(tl))
      assert taste_levels not in seen_cases, (
        'Duplicated case: {}'.format(taste_levels))
      seen_cases.add(taste_levels)
      assert 2 <= len(taste_levels) <= 25, (
          "Set {}, Case {} ({}): Number of gophers ({}) out of range".format(
              ts, c, taste_levels, len(taste_levels)))
      assert (MIN_TASTE <= taste_levels[0] and
              taste_levels[-1] <= MAX_TASTE), (
          "Set {}, Case {} ({}): A taste level is out of range".format(
              ts, c, taste_levels))
      if ts == 1:
        assert len(set(taste_levels)) == len(taste_levels), (
            "Set 1, Case {} ({}): Duplicated taste level".format(
                c, taste_levels))
      else:
        err = CheckSet2(taste_levels)
        assert err is None, "Set 2, Case {}: {}".format(c, err)


def Test():
  TestReadValue()
  TestRunCase()
  CheckInterject()
  CheckApplyToSlices()
  TestCheckSet2()
  CheckIsReorderFunc()
  ValidateCases()
  print "\n".join("TS{} case {}: {}".format(i, j, c)
                  for i, cases in enumerate((Set1Cases(), Set2Cases()), 1)
                  for j, (c, _) in enumerate(cases))


def main():
  random.seed(92653)
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  if index == -2:
    Test()
  else:
    cases = list(Set1Cases() if index == 0 else Set2Cases())
    random.shuffle(cases)
    print len(cases)
    result = RunCases(cases)
    if result:
      print >> sys.stderr, result
      sys.stdout.flush()
      sys.exit(1)


if __name__ == "__main__":
  main()
