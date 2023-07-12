#include <algorithm>
#include <cstdio>
#include <utility>
#include <vector>

#include "khazaddum.h"  // NOLINT
#include "message.h"    // NOLINT

typedef long long ll;    // NOLINT
typedef long double ld;  // NOLINT

#define MAXN 100000000
#define MAXHEI 100000000

ll N;
int me;
std::vector<ll> heights;
std::vector<ll> minhei;

// We want to calculate the answer to the question "if we dig up to x
// centimeters deep, how much will we excavate?". The answer to this question
// is a piecewise quadratic function, and we want to know, for a given x, what
// are the coefficients of this function on the range the x belongs to.
// The equation we care about will be alpha x^2  + beta x + gamma.
// We will first accumulate changes to alpha, beta, and gamma at points in time
// (in the _deltas vectors), then sort and accumulate those vectors, and then
// binary search in them for answers.
std::vector<std::pair<ld, ld>> alpha_deltas;
std::vector<std::pair<ld, ld>> beta_deltas;
std::vector<std::pair<ld, ld>> gamma_deltas;
std::vector<std::pair<ld, ld>> alph;
std::vector<std::pair<ld, ld>> bet;
std::vector<std::pair<ld, ld>> gamm;

// This register the changes to the alph, bet and gamm values for an interval
// of length "multiplier" that has heights of h1 and h2 at edges, and
// min heights of mh1 and mh2 at edges.
void PushValues(ld h1, ld h2, ld mh1, ld mh2, ld multiplier) {
  ld s = mh1 - h1;
  ld e = mh2 - h2;
  if (s > e) std::swap(s, e);
  // If the road is exactly parallel to the mountain surface, the excavation
  // function will first be zero, and then jump to being linear with coefficient
  // one (or rather, multiplier) at s. We need to subtract a constant, so that
  // the linear function begins with zero at s.
  if (s == e) {
    beta_deltas.push_back(std::make_pair(s, multiplier));
    gamma_deltas.push_back(std::make_pair(s, -multiplier * s));
  } else {
    // This defines a quadratic function with a double-zero at s, and
    // reaching (e-s) / 2 at e. In the range between s and e, the area excavated
    // will be a triangle, growing linearly (so the area grows quadratic). At
    // the beginning, the area is zero, and the derivative is zero - which is
    // where the double-zero at s comes from. At the end, we have a triangle
    // with a base of e - s, and height of multiplier.
    alpha_deltas.push_back(std::make_pair(s, multiplier * 0.5 / (e - s)));
    beta_deltas.push_back(std::make_pair(s, -multiplier * s / (e - s)));
    gamma_deltas.push_back(
        std::make_pair(s, multiplier * s * s * 0.5 / (e - s)));
    // This cancels out the quadratic function above, inserting instead a
    // linear function that has value (e - s) / 2 at e, and a coefficient of 1.
    alpha_deltas.push_back(std::make_pair(e, -multiplier * 0.5 / (e - s)));
    beta_deltas.push_back(std::make_pair(e, multiplier * ((s / (e - s)) + 1)));
    gamma_deltas.push_back(std::make_pair(
        e, multiplier * (-s * s * 0.5 / (e - s) - (e + s) * 0.5)));
  }
}

void accumulate(std::vector<std::pair<ld, ld>> &deltas,
                std::vector<std::pair<ld, ld>> &result) {
  std::sort(deltas.begin(), deltas.end());
  ld current_pos = -1;
  ld val = 0;
  for (const auto &delta : deltas) {
    if (delta.first != current_pos) {
      result.push_back(std::make_pair(current_pos, val));
      current_pos = delta.first;
    }
    val += delta.second;
  }
  result.push_back(std::make_pair(current_pos, val));
}

ld upto(std::vector<std::pair<ld, ld>> &coefficients, ld pos) {
  int lo = 0;
  int hi = coefficients.size();
  while (hi - lo > 1) {
    int med = (hi + lo) / 2;
    if (coefficients[med].first <= pos) {
      lo = med;
    } else {
      hi = med;
    }
  }
  return coefficients[lo].second;
}

// We don't have get/put functions for doubles. So, we'll hack them on top of
// Get/Put LL.
void PutDouble(int node, double value) { PutLL(node, *(ll *)(&value)); }
double GetDouble(int node) {
  ll value = GetLL(node);
  return *(double *)(&value);
}

int main() {
  me = MyNodeId();
  int nodes = NumberOfNodes();

  N = GetRangeLength() + 1;
  // Note - the ranges owned by particular nodes have to overlap, because we
  // care about the intervals in between (each has to belong to someone), and
  // not about the vertices.
  ll beg = ((N - 1) * me) / nodes;
  ll end = ((N - 1) * (me + 1)) / nodes + 1;
  ll myN = end - beg;
  ld to_dig = GramsToExcavate();
  for (int i = 0; i < myN; ++i) {
    heights.push_back(GetHeight(i + beg));
    minhei.push_back(
        std::max(heights[i], i ? (minhei[i - 1] - 1) : heights[i]));
  }
  for (int i = myN - 1; i >= 0; --i) {
    minhei[i] =
        std::max(minhei[i], (i == myN - 1) ? heights[i] : minhei[i + 1] - 1);
  }
  // Now, send all the preceding nodes the min height on the left, and all the
  // succeeding nodes min height on the right.
  for (int node = 0; node < me; ++node) {
    PutLL(node, beg);
    PutLL(node, minhei[0]);
    Send(node);
  }
  for (int node = me + 1; node < nodes; ++node) {
    PutLL(node, end - 1);
    PutLL(node, minhei[myN - 1]);
    Send(node);
  }
  // And gather this data, and adjust.
  for (int node = 0; node < me; ++node) {
    Receive(node);
    ll where = GetLL(node);
    ll height = GetLL(node);
    ll height_at_beg = height - (beg - where);
    assert(beg >= where);
    minhei[0] = std::max(minhei[0], height_at_beg);
  }
  for (int node = me + 1; node < nodes; ++node) {
    Receive(node);
    ll where = GetLL(node);
    ll height = GetLL(node);
    assert(where >= end - 1);
    ll height_at_end_minus_one = height - (where - (end - 1));
    minhei[myN - 1] = std::max(minhei[myN - 1], height_at_end_minus_one);
  }
  for (int i = 1; i < myN; ++i) {
    if (minhei[i] < minhei[i - 1] - 1) {
      minhei[i] = minhei[i - 1] - 1;
    } else {
      break;
    }
  }
  for (int i = myN - 2; i >= 0; --i) {
    if (minhei[i] < minhei[i + 1] - 1) {
      minhei[i] = minhei[i + 1] - 1;
    } else {
      break;
    }
  }
  // Now all the min heights should be globally correct.
  for (int i = 0; i < myN - 1; ++i) {
    // If the two min heights are equal, and they are not set exactly at the
    // level of the heights, then the min height graph takes a little dip in
    // the middle of the [i, i+1] interval. We treat this as two intervals,
    // [i, i+0.5] and [i+0.5, i].
    // The indices in the tree will be multiplied by two, so that we can handle
    // them as integers.
    if (minhei[i + 1] == minhei[i] &&
        (minhei[i + 1] + minhei[i] != heights[i + 1] + heights[i])) {
      PushValues(heights[i], 0.5 * (heights[i] + heights[i + 1]), minhei[i],
                 0.5 * (minhei[i] + minhei[i + 1] - 1), 0.5);
      PushValues(0.5 * (heights[i] + heights[i + 1]), heights[i + 1],
                 0.5 * (minhei[i] + minhei[i + 1] - 1), minhei[i + 1], 0.5);
    } else {
      PushValues(heights[i], heights[i + 1], minhei[i], minhei[i + 1], 1);
    }
  }
  accumulate(alpha_deltas, alph);
  accumulate(beta_deltas, bet);
  accumulate(gamma_deltas, gamm);
  // In the worst case, we have a few high peaks (of height ~MAXHEI), and the
  // rest is flat. So, the zero-dig road goes along ~MAXHEI, and the first
  // MAXHEI we dig in excavates relatively little. If GramsToExcavate is around
  // MAXHEI * RangeLength, then we have to dig another MAXHEI in to excavate
  // enough (since on the second MAXHEI we're guaranteed to dig through the
  // ground).
  double hi = 2 * MAXHEI;
  double lo = 0;
  // We will do 1000-ary search - that is, we'll split the range into 1000
  // sub-ranges, each node will send back the values for each of the border
  // values, the master will sum them up, and identify the correct sub-interval.
  // Rinse and repeat.
  const int search_arity = 1000;
  // At this point, each node owns a partially quadratic function. We need to
  // N-ary search for the dig depth where we excavate enough.
  int master = 0;
  while ((hi - lo) / hi > 1e-8) {
    for (int i = 1; i < search_arity; ++i) {
      ld med = (lo * (search_arity - i) + hi * i) / search_arity;
      ld a = upto(alph, med);
      ld b = upto(bet, med);
      ld c = upto(gamm, med);
      ld res = a * med * med + b * med + c;
      PutDouble(master, res);
    }
    Send(master);
    if (me == master) {
      std::vector<double> values(search_arity - 1);
      for (int node = 0; node < nodes; ++node) {
        Receive(node);
        for (int i = 1; i < search_arity; ++i) {
          double dug = GetDouble(node);
          values[i - 1] += dug;
        }
      }
      double new_lo = -1;
      double new_hi = -1;
      for (int i = 1; i < search_arity; ++i) {
        if (values[i - 1] > to_dig) {
          new_lo =
              (lo * (search_arity - (i - 1)) + hi * (i - 1)) / search_arity;
          new_hi = (lo * (search_arity - i) + hi * i) / search_arity;
          break;
        }
      }
      if (new_lo == -1) {
        new_lo = (lo + hi * (search_arity - 1)) / search_arity;
        new_hi = hi;
      }
      for (int node = 0; node < nodes; ++node) {
        PutDouble(node, new_lo);
        PutDouble(node, new_hi);
        Send(node);
      }
    }
    Receive(master);
    lo = GetDouble(master);
    hi = GetDouble(master);
    master = (master + 1) % nodes;
  }
  if (me == master) {
    printf("%.8lf\n", lo);
  }
  return 0;
}
