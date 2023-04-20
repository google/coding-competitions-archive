// We make sure assert() actually works.
#undef NDEBUG

#include <algorithm>
#include <cassert>
#include <cctype>
#include <csignal>
#include <cstdint>
#include <ctime>
#include <fstream>
#include <functional>
#include <iostream>
#include <list>
#include <map>
#include <optional>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
#include <ext/pb_ds/assoc_container.hpp>

using namespace std;

ostream &operator<<(ostream& out, unsigned __int128 a) {
  string s;
  do {
    s += (char)('0' + a % 10);
    a /= 10;
  } while (a > 0);
  reverse(s.begin(), s.end());
  return out << s;
}

template <typename T, typename U>
ostream& operator<<(ostream& out, const pair<T, U>& p) {
  return out << "<" << p.first << "," << p.second << ">";
}

template <typename T>
ostream& operator<<(ostream& out, const vector<T>& v) {
  out << "[";
  for (const T& t : v) out << t << ", ";
  return out << "]";
}

template <typename T>
bool Eq(const T& t1, const T& t2) {
  if (t1 != t2)
    cerr << "Expected " << t1 << " and " << t2 << " to be equal" << endl;
  return t1 == t2;
}

bool mocked_error;
string last_error;

string ProtoEscape(const string& msg) {
  string r;
  r.reserve(msg.size() * 2);  // Just an estimate. msg should be short.
  for (char c : msg) {
    switch (c) {
      case '\n':
        r += "\\n";
        break;
      case '\'':
        r += "\\'";
        break;
      case '\"':
        r += "\\\"";
        break;
      default:
        if (32 <= c && c <= 127) {
          r += c;
        } else {
          ostringstream out;
          int cc = c;
          out << '\\' << (cc >> 6) << ((cc >> 3) & 3) << (cc & 3);
          r += out.str();
        }
    }
  }
  return r;
}

ofstream error_file;

void Error(const string& msg) {
  // TODO: for testing, I guess we need to propagate output_stream here
  // instead of using cout directly.
  cout << -1 << endl;
  if (mocked_error) {
    last_error = msg;
    // throw to avoid additional errors.
    throw 1;
  } else {
    error_file << "status: INVALID" << endl;
    error_file << "status_message: '" << ProtoEscape(msg) << "'" << endl;
    exit(0);
  }
}

string JudgeErrorStr(const string& msg) { return "JUDGE_ERROR! " + msg; }

void JudgeError(const string& msg) { Error(JudgeErrorStr(msg)); }

void JudgeAssert(bool condition, const string& msg) {
  if (!condition) JudgeError(msg);
}

#define AssertEqual(a, b)                                                 \
  {                                                                       \
    auto ___va = a;                                                       \
    auto ___vb = b;                                                       \
    if (!(___va == ___vb)) {                                              \
      cerr << "Error in " << __func__ << " at line " << __LINE__ << endl; \
      cerr << "  " #a << endl                                             \
           << "    which is `" << ___va << "`" << endl                    \
           << "  is not equal to" << endl                                 \
           << "  " #b << endl                                             \
           << "    which is `" << ___vb << "`." << endl;                  \
      exit(1);                                                            \
    }                                                                     \
  }

#define AssertTrue(a) AssertEqual(a, true)
#define AssertFalse(a) AssertEqual(a, false)

#define AssertError(call, err)  \
  mocked_error = true;          \
  try {                         \
    call;                       \
  } catch (...) {               \
  }                             \
  AssertEqual(last_error, err); \
  last_error = "";              \
  mocked_error = false;

#define AssertJudgeError(call, err) AssertError(call, JudgeErrorStr(err))

string Strint(int64_t n) {
  ostringstream out;
  out << n;
  return out.str();
}

void TestStrint() {
  assert(Strint(5) == "5");
  assert(Strint(-21) == "-21");
  assert(Strint(0) == "0");
}

string Truncate(const string& s) {
  if (s.size() <= 50) return s;
  return s.substr(0, 47) + string("...");
}

void TestTruncate() {
  assert(Truncate("") == "");
  assert(Truncate("helloworld") == "helloworld");
  assert(Truncate(string(50, 'x')) == string(50, 'x'));
  assert(Truncate(string(51, 'x')) == string(47, 'x') + "...");
}

// Parses ints in [-10^18, 10^18] or raises Error.
int64_t ParseInt(const string& ss) {
  const string error = string("Not an integer in range: ") + Truncate(ss);
  if (ss[0] != '-' && (ss[0] < '0' || ss[0] > '9')) Error(error);
  for (int i = 1; i < ss.size(); ++i)
    if (ss[i] < '0' || ss[i] > '9') Error(error);
  string s;
  if (!ss.empty()) {
    int first_digit = 0;
    if (ss[0] == '-') {
      s += '-';
      first_digit = 1;
    }
    while (first_digit < ss.size() - 1 && ss[first_digit] == '0') ++first_digit;
    s += ss.substr(first_digit);
  }
  if (s.empty() || s.size() > 20) Error(error);
  if (s.size() == 20 && s != string("-1") + string(18, '0')) Error(error);
  if (s.size() == 19 && s[0] != '-' && s != string("1") + string(18, '0'))
    Error(error);
  istringstream in(s);
  int64_t r;
  in >> r;
  return r;
}

void TestParseInt() {
  assert(ParseInt("0") == 0);
  assert(ParseInt("0000") == 0);
  assert(ParseInt("-0") == 0);
  assert(ParseInt("-0000") == 0);
  assert(ParseInt("-10") == -10);
  assert(ParseInt("-010") == -10);
  assert(ParseInt("010111") == 10111);
  assert(ParseInt("00009") == 9);
  assert(ParseInt(string("1") + string(18, '0')) == 1000000000000000000);
  assert(ParseInt(string("0001") + string(18, '0')) == 1000000000000000000);
  assert(ParseInt(string("-1") + string(18, '0')) == -1000000000000000000);
  assert(ParseInt(string("-0001") + string(18, '0')) == -1000000000000000000);
  AssertError(ParseInt(""), "Not an integer in range: ");
  AssertError(ParseInt("a"), "Not an integer in range: a");
  AssertError(ParseInt("1a1"), "Not an integer in range: 1a1");
  AssertError(ParseInt(string("1") + string(17, '0') + "1"),
              "Not an integer in range: 1000000000000000001");
  AssertError(ParseInt(string("-1") + string(17, '0') + "1"),
              "Not an integer in range: -1000000000000000001");
  AssertError(ParseInt("0x10"), "Not an integer in range: 0x10");
  AssertError(ParseInt("1.0"), "Not an integer in range: 1.0");
}

string Lowercase(const string& s) {
  string r(s);
  for (char& c : r) c = tolower(c);
  return r;
}

void TestLowercase() {
  assert(Lowercase("Case") == "case");
  assert(Lowercase("c") == "c");
  assert(Lowercase("A") == "a");
  assert(Lowercase("234") == "234");
  assert(Lowercase("AbC234xYz") == "abc234xyz");
}

vector<string> Tokenize(const string& l) {
  istringstream in(l);
  string s;
  vector<string> r;
  while (in >> s) r.push_back(Lowercase(s));
  return r;
}

void TestTokenize() {
  assert(Tokenize("a b c") == vector<string>({"a", "b", "c"}));
  assert(Tokenize("1") == vector<string>({"1"}));
  assert(Tokenize("  1  ") == vector<string>({"1"}));
  assert(Tokenize("  1\t2    \n3\n\n\n4") ==
         vector<string>({"1", "2", "3", "4"}));
}

vector<int64_t> ReadInts(istream& stream) {
  string s;
  if (!getline(stream, s)) {
    Error("Expected a string");
  }
  vector<string> tokens = Tokenize(s);
  if (tokens.empty()) {
    Error("Expected a non-empty string");
  }
  vector<int64_t> values;
  for (auto token : tokens) {
    values.push_back(ParseInt(token));
  }
  return values;
}

void TestReadInts() {
  // TODO
}

void TestLib() {
  TestStrint();
  TestTruncate();
  TestParseInt();
  TestLowercase();
  TestTokenize();
  TestReadInts();
}

//////////////////////////////////////////////

template <typename K, typename V, typename H>
using HashMapType = __gnu_pbds::gp_hash_table<K, V, H>;

static const uint64_t kMul = 0xc6a4a7935bd1e995ULL;

// Borrowed from MurMurHash
uint64_t MurMurMix(uint64_t a) {
  a ^= a >> 47;
  a *= kMul;
  a ^= a >> 47;
 return a;
}

uint64_t MurMurCombine(uint64_t a, uint64_t b) {
  b *= kMul;
  b ^= b >> 47;
  b *= kMul;
  a ^= b;
  a *= kMul;
  return a;
}

using KeyType = unsigned __int128;

struct KeyHash {
  uint64_t operator()(KeyType val) const {
    return MurMurMix(MurMurCombine(val, val >> 64));
  }
};

struct SubsetHash {
  uint64_t operator()(uint64_t val) const {
    return MurMurMix(val);
  }
};

template <typename K, typename V, typename H>
struct LRUCache {
  using LRUList = list<pair<K, V>>;
  LRUList lru;
  HashMapType<K, typename LRUList::iterator, H> lookup;
  int maxSize;

  explicit LRUCache(int maxSize) : maxSize(maxSize) {}

  ~LRUCache() {
    // Clear the map first to make sure we don't have any invalid iterators.
    lookup.clear();
  }

  optional<V> Fetch(K key) {
    auto it = lookup.find(key);
    if (it == lookup.end()) return nullopt;
    lru.splice(lru.begin(), lru, it->second);
    return it->second->second;
  }

  // Must only be called if the element is not already there.
  void Store(K key, V value) {
    lru.emplace_front(key, value);
    lookup[key] = lru.begin();
    if (lru.size() > maxSize) {
      lookup.erase(lru.back().first);
      lru.pop_back();
    }
  }
};

uint64_t Bit(int x) { return uint64_t(1) << x; }

// Computes an integer that has bit 1 at position x if and only if
// a has bit 1 at position (x ^ b).
uint64_t BitwisePositionXor(uint64_t a, int b) {
  uint64_t res = 0;
  // In most cases this function is called when only a few bits
  // are set, so we iterate over all set bits via __builtin_ctzll.
  while (a) {
    int i = __builtin_ctzll(a);
    res |= Bit(i ^ b);
    a ^= Bit(i);
  }
  return res;
}

struct Solver {
  int n;
  // Adjacency lists for each vertex.
  vector<vector<int>> adj;
  // Adjacency bitmask for each vertex.
  vector<uint64_t> adj_mask;
  // For each pair of vertices (a,b) connected with an edge, the mask of
  // vertices in the component of vertex b if we cut the edge (a,b).
  vector<vector<uint64_t>> child_mask;
  // Maps the canonicalized tree description to a nimber.
  // The canonicalized tree description is created, after picking the
  // appropriate root, in the following manner as a bitmask:
  // 0(child 1)(child 2)...(last child)1
  // where for each child we describe in the same manner, and children's
  // descriptions are sorted.
  HashMapType<KeyType, int, KeyHash> nimber;
  // We keep this vector of vectors to avoid creating temporary vectors inside
  // GetRootedTreeKey method, which brings a ~7% speedup.
  vector<vector<pair<int, KeyType>>> recursive_vals;
  // This keeps an LRU cache that maps the subsets of vertices to the
  // canonicalized tree description.
  LRUCache<uint64_t, KeyType, SubsetHash> lru;
  // In order to avoid long running times and big memory usages for the judge,
  // we limit the number of states that we visit (see the constructor below
  // for the value of the limit, and the size of the LRU cache). But we
  // guarantee that we'll fully explore at least one move from the starting
  // position.
  int64_t budget;
  // This is the list of fully explored moves from the starting position
  // given the budget limitation above.
  vector<int> mains_to_consider_for_first_move;
  // This stores the last game where each outcome of the first move
  // has appeared, to help us ensure the diversity of the first moves.
  map<vector<KeyType>, int> first_move_outcome_last_seen;

  // The edges must form a tree.
  explicit Solver(vector<pair<int, int>> edges)
      : lru(int(1e6)), budget(int(5e5)) {
    n = edges.size() + 1;
    adj.assign(n, {});
    adj_mask.assign(n, {});
    child_mask.assign(n, vector<uint64_t>(n));

    for (const auto& [p, q] : edges) {
      JudgeAssert(p >= 0 && p < n && q >= 0 && q < n, "Vertex out of bounds");
      adj[p].push_back(q);
      adj[q].push_back(p);
      adj_mask[p] |= Bit(q);
      adj_mask[q] |= Bit(p);
    }

    uint64_t all = Bit(n) - 1;
    for (int i = 0; i < n; ++i) {
      for (int j : adj[i]) {
        child_mask[i][j] = FindComponent(all, j, i);
      }
    }
    NimberSingleComponent(all);
  }

  // Finds the centroid(s) of a subtree: vertices such that after removing them
  // the remaining components have size k/2 or less, where k is the size of the
  // subtree.
  template<typename Callback>
  void FindCentroids(uint64_t subset, Callback callback) {
    JudgeAssert(subset != 0, "Trying to find the centroids of an empty set");
    int root = __builtin_ctzll(subset);
    int subset_size = __builtin_popcountll(subset);
    int prev_root = -1;
    while (true) {
      bool found = false;
      for (int i : adj[root]) {
        if (subset & Bit(i)) {
          uint64_t child = subset & child_mask[root][i];
          int child_size = __builtin_popcountll(child);
          if (2 * child_size == subset_size) {
            callback(root);
            callback(i);
            return;
          }
          if (2 * child_size > subset_size) {
            JudgeAssert(i != prev_root, "Centroid search went into a cycle");
            prev_root = root;
            root = i;
            found = true;
            break;
          }
        }
      }
      if (!found) {
        callback(root);
        return;
      }
    }
  }

  pair<int, KeyType> GetRootedTreeKey(uint64_t subset, int root, int skip,
                                      int depth) {
    if (depth >= recursive_vals.size()) recursive_vals.resize(depth + 1);
    recursive_vals[depth].clear();
    for (int child : adj[root]) {
      if (child != skip && (subset & Bit(child))) {
        auto child_key = GetRootedTreeKey(subset, child, root, depth + 1);
        // Note that since the recursive call can resize recursive_vals,
        // we cannot store a reference to its elements yet.
        recursive_vals[depth].push_back(child_key);
      }
    }
    auto& vals = recursive_vals[depth];
    sort(vals.begin(), vals.end());
    int count = 1;
    KeyType key = 0;
    for (auto p : vals) {
      key <<= p.first;
      key += p.second;
      count += p.first;
    }
    key <<= 1;
    key += 1;
    count += 1;
    return {count, key};
  }

  KeyType GetTreeKey(uint64_t subset) {
    auto cached = lru.Fetch(subset);
    if (cached != nullopt) return cached.value();
    KeyType res = 0;
    auto callback = [&](int centroid) {
      auto p = GetRootedTreeKey(subset, centroid, -1, 0);
      res = max(res, p.second);
    };
    FindCentroids(subset, callback);
    JudgeAssert(res != 0, "Could not find any centroids");
    lru.Store(subset, res);
    return res;
  }

  uint64_t FindComponent(uint64_t subset, int root, int skip) {
    JudgeAssert(subset & Bit(root), "Component dfs visited an excluded vertex");
    uint64_t res = Bit(root);
    for (int i : adj[root]) {
      if (i != skip && (subset & Bit(i))) {
        res |= FindComponent(subset, i, root);
      }
    }
    return res;
  }

  int LargestComponentSizeForAllButOne(int one) {
    uint64_t subset = Bit(n) - 1 - Bit(one);
    int max_size = 0;
    for (int i = 0; i < n; ++i) {
      if (subset & Bit(i)) {
        uint64_t component = FindComponent(subset, i, -1);
        int size = __builtin_popcountll(component);
        subset ^= component;
        max_size = max(max_size, size);
      }
    }
    return max_size;
  }

  template <typename Callback1, typename Callback2>
  void EnumerateMoves(uint64_t subset, int main, Callback1 callback,
                      Callback2 out_of_budget_callback) {
    for (int child : adj[main]) {
      if (subset & Bit(child)) {
        uint64_t component = child_mask[main][child] & subset;
        auto nimber_with = NimberSingleComponent(component);
        if (!nimber_with.has_value()) {
          out_of_budget_callback();
          return;
        }
        auto nimber_without =
            NimberSingleComponentWithRootRemoved(component, child);
        if (!nimber_without.has_value()) {
          out_of_budget_callback();
          return;
        }
        callback(child, nimber_with.value(), nimber_without.value());
      }
    }
  }

  optional<int> NimberSingleComponentWithRootRemoved(uint64_t subset,
                                                     int root) {
    int res = 0;
    for (int child : adj[root]) {
      if (subset & Bit(child)) {
        uint64_t component = child_mask[root][child] & subset;
        auto part = NimberSingleComponent(component);
        if (!part.has_value()) return nullopt;
        res ^= part.value();
      }
    }
    return res;
  }

  optional<int> NimberSingleComponent(uint64_t subset) {
    auto key = GetTreeKey(subset);
    auto it = nimber.find(key);
    if (it != nimber.end()) {
      return it->second;
    }
    // We stop the research if the budget has been exhausted and we have fully
    // investigated at least one first move. I don't expect the second condition
    // to matter in practice because we start researching first moves from the
    // one that splits the tree into parts of size at most 20, and which
    // therefore should not exhaust the budget, but keeping it here for
    // safety.
    if (budget < 0 && !mains_to_consider_for_first_move.empty()) {
      return nullopt;
    }
    bool is_everything = subset == Bit(n) - 1;
    if (is_everything) {
      JudgeAssert(mains_to_consider_for_first_move.empty(),
                  "Somehow exploring the first move twice");
    }
    // Since the game can never last more than n turns, the nimbers
    // never exceed n, so we can use a bitmask to represent reachable nimbers.
    uint64_t seen = 0;
    // Note that we can't just try all moves,
    // as the number of moves for a star with n leaves is O(2**n).
    // So we do a DP that computes the reachable nimbers after taking
    // the first K decisions of the form "do we take this adjacent vertex".
    bool out_of_budget = false;

    auto consider_main = [&](int main) {
      uint64_t can = 1;
      int base_xor = 0;
      auto callback = [&](int root, int nimber_with, int nimber_without) {
        base_xor ^= nimber_with;
        int extra = nimber_with ^ nimber_without;
        if (!(can & Bit(extra))) {
          can |= BitwisePositionXor(can, extra);
        }
      };
      auto out_of_budget_callback = [&]() { out_of_budget = true; };
      EnumerateMoves(subset, main, callback, out_of_budget_callback);
      if (out_of_budget) {
        return;
      }
      seen |= BitwisePositionXor(can, base_xor);
    };

    if (is_everything) {
      // For the first move, we try the moves in increasing order of the
      // largest tree component that they produce, so that the first moves
      // we try would be explored fast and not exhaust our budget.
      vector<pair<int, int>> candidates;
      for (int main = 0; main < n; ++main) {
        candidates.emplace_back(LargestComponentSizeForAllButOne(main), main);
      }
      sort(candidates.begin(), candidates.end());
      for (auto p : candidates) {
        int main = p.second;
        consider_main(main);
        if (out_of_budget) {
          // For the first move, we still compute a nimber without
          // trying all options, so that the judge can make some first move
          // and then play optimally.
          JudgeAssert(
              !mains_to_consider_for_first_move.empty(),
              "Somehow ran out of budget before exploring the first move");
          break;
        }
        mains_to_consider_for_first_move.push_back(main);
        if (seen & Bit(0)) {
          // If we have already found a way to win with the first move,
          // no need to examine other moves.
          break;
        }
      }
    } else {
      for (int main = 0; main < n; ++main) {
        if (subset & Bit(main)) {
          consider_main(main);
          if (out_of_budget) {
            return nullopt;
          }
        }
      }
    }

    --budget;
    int res = __builtin_ctzll(~seen);
    nimber[key] = res;
    return res;
  }

  optional<int> NimberMultiComponent(uint64_t subset) {
    int res = 0;
    for (int i = 0; i < n; ++i) {
      if (subset & Bit(i)) {
        uint64_t component = FindComponent(subset, i, -1);
        subset ^= component;
        auto part = NimberSingleComponent(component);
        if (!part.has_value()) return nullopt;
        res ^= part.value();
      }
    }
    return res;
  }

  // Returns the canonical keys for each of the trees in the given subset.
  vector<KeyType> FindComponentTypes(uint64_t subset) {
    vector<KeyType> res;
    for (int i = 0; i < n; ++i) {
      if (subset & Bit(i)) {
        uint64_t component = FindComponent(subset, i, -1);
        subset ^= component;
        auto key = GetTreeKey(component);
        res.push_back(key);
      }
    }
    return res;
  }

  // Normalizes the set of keys of trees in a subset so that different
  // sets after this normalization present substantially different situations
  // that we want to make sure the solutions are tested on.
  vector<KeyType> NormalizeComponentTypes(vector<KeyType> types) {
    map<KeyType, int> freq;
    for (auto t : types) {
      ++freq[t];
    }
    vector<KeyType> res;
    // Note that since we iterate over a map we also implicitly sort here.
    for (const auto& p : freq) {
      int count = p.second;
      if (count >= 3) {
        // Get a smaller number with the same parity, as it most likely
        // won't matter for a solution, and we don't want to explore
        // all possible ways to cut rays from a star.
        count = count - (count - 1) / 2 * 2;
      }
      for (int i = 0; i < count; ++i) {
        res.push_back(p.first);
      }
    }
    return res;
  }

  bool CanWinInOneMove(uint64_t subset) {
    JudgeAssert(subset != 0,
                "Trying to check if we can win from an empty state");
    for (int i = 0; i < n; ++i) {
      if (subset & Bit(i)) {
        if (subset == ((adj_mask[i] & subset) | (Bit(i)))) {
          return true;
        }
      }
    }
    return false;
  }

  // This is essentially the answer reconstruction for the DP
  // in the NimberSingleComponent method.
  vector<int> FindSingleComponentMoveTo(uint64_t subset, int need_nimber) {
    auto key = GetTreeKey(subset);
    auto it = nimber.find(key);
    JudgeAssert(it != nimber.end(),
                "Trying to reconstruct a move from an unprocessed state");
    JudgeAssert(need_nimber < it->second,
                "Trying to reconstruct a move to a bigger nimber");

    vector<int> res;
    auto consider_main = [&](int main) {
      vector<int> roots;
      vector<int> nimber_withs;
      vector<int> nimber_withouts;
      vector<vector<int>> via;
      via.push_back({0});
      auto callback = [&](int root, int nimber_with, int nimber_without) {
        roots.push_back(root);
        nimber_withs.push_back(nimber_with);
        nimber_withouts.push_back(nimber_without);
        vector<int> nvia;
        for (int i = 0; i < via.back().size(); ++i) {
          if (via.back()[i] >= 0) {
            int move_index = 0;
            for (int move : {nimber_with, nimber_without}) {
              int got = i ^ move;
              if (got >= nvia.size()) nvia.resize(got + 1, -1);
              nvia[got] = move_index;
              ++move_index;
            }
          }
        }
        via.push_back(nvia);
      };
      auto out_of_budget_callback = [&]() {
        // This should never happen since we only traverse the states
        // that have already been traversed when computing the nimber,
        // and therefore always hit the cache.
        JudgeError("We ran out of budget during move reconstruction");
      };
      EnumerateMoves(subset, main, callback, out_of_budget_callback);
      if (need_nimber < via.back().size() && via.back()[need_nimber] >= 0) {
        res.push_back(main);
        for (int i = int(roots.size()) - 1; i >= 0; --i) {
          int move_index = via[i + 1][need_nimber];
          JudgeAssert(move_index >= 0,
                      "Move reconstruction led to an unvisited state");
          if (move_index == 0) {
            need_nimber ^= nimber_withs[i];
          } else {
            need_nimber ^= nimber_withouts[i];
            res.push_back(roots[i]);
          }
        }
        JudgeAssert(need_nimber == 0,
                    "Move reconstruction failed to return to 0 nimber");
        return true;
      }
      return false;
    };

    if (subset == Bit(n) - 1) {
      for (int main : mains_to_consider_for_first_move) {
        if (consider_main(main)) {
          return res;
        }
      }
    } else {
      for (int main = 0; main < n; ++main) {
        if (subset & Bit(main)) {
          if (consider_main(main)) {
            return res;
          }
        }
      }
    }
    JudgeError(
        "Could not find a move to a smaller nimber from a single component");
    assert(false);  // To avoid a compilation warning
  }

  vector<int> FindMultiComponentMoveToZero(uint64_t subset) {
    auto start = NimberMultiComponent(subset);
    JudgeAssert(start.has_value(),
                "Trying to find a move from a state that was truncated because "
                "of budget");
    int start_nimber = start.value();
    for (int i = 0; i < n; ++i) {
      if (subset & Bit(i)) {
        uint64_t component = FindComponent(subset, i, -1);
        subset ^= component;
        auto cur = NimberSingleComponent(component);
        JudgeAssert(cur.has_value(),
                    "A potential move leads to a state that was truncated "
                    "because of budget");
        int need = cur.value() ^ start_nimber;
        if (need < cur.value()) {
          return FindSingleComponentMoveTo(component, need);
        }
      }
    }
    JudgeError("Could not find a move to a smaller nimber");
    assert(false);  // To avoid a compilation warning
  }

  vector<int> GetRandomMove(uint64_t subset, int game_id, mt19937& rng) {
    JudgeAssert(subset, "Trying to pick a move on an empty subset");

    auto consider_main = [&](int main) {
      vector<int> res;
      res.push_back(main);
      for (int a : adj[main]) {
        if (subset & Bit(a)) {
          if (uniform_int_distribution<int>(0, 1)(rng) == 1) {
            res.push_back(a);
          }
        }
      }
      return res;
    };

    bool is_everything = subset == Bit(n) - 1;
    if (is_everything) {
      // For the first move in case we're in a losing position, we try
      // to enforce some diversity in the set of states we reach, to make
      // sure that casework solutions are tested properly.
      // Since the number of potential first moves can be exponential,
      // we just try 100 candidates and pick the one that adds the most
      // diversity.
      // 100 iterations here should not damage the judge running time too much
      // since we have to make up to 40 moves afterwards anyway.
      vector<int> best_res;
      vector<KeyType> best_res_first_move_outcome;
      int best_res_appeared = (int) 1e9;
      for (int iteration = 0; iteration < 100; ++iteration) {
        int main_index = uniform_int_distribution<int>(
            0, mains_to_consider_for_first_move.size() - 1)(rng);
        int main = mains_to_consider_for_first_move[main_index];
        auto res = consider_main(main);
        uint64_t remains = subset;
        for (int x : res) remains ^= Bit(x);
        vector<KeyType> types = FindComponentTypes(remains);
        types = NormalizeComponentTypes(types);
        auto it = first_move_outcome_last_seen.find(types);
        if (it == first_move_outcome_last_seen.end()) {
          // In case we have never seen this, no further iterations are needed.
          best_res = res;
          best_res_first_move_outcome = types;
          break;
        }
        // Try to choose the outcome that last appeared as early as possible.
        if (it->second < best_res_appeared) {
          best_res = res;
          best_res_first_move_outcome = types;
          best_res_appeared = it->second;
        }
      }
      JudgeAssert(!best_res.empty(), "Did not decide on a move");
      first_move_outcome_last_seen[best_res_first_move_outcome] = game_id;
      return best_res;
    } else {
      int size = __builtin_popcountll(subset);
      int main_index = uniform_int_distribution<int>(0, size - 1)(rng);
      for (int main = 0; main < n; ++main) {
        if (subset & Bit(main)) {
          --main_index;
          if (main_index < 0) {
            return consider_main(main);
          }
        }
      }
      JudgeError("Failed to select a random move");
    }
    assert(false);  // To avoid a compilation warning
  }
};

void RunCase(istream& input_stream, ostream& output_stream, int case_idx,
             int min_n, int max_n, int max_m, mt19937& rng) {
  JudgeAssert(case_idx >= 1 && case_idx <= max_n - min_n + 1,
              "Invalid case number");
  int n = min_n + case_idx - 1;
  output_stream << n << endl;
  vector<pair<int, int>> edges;
  vector<int> component(n);
  iota(component.begin(), component.end(), 0);
  for (int i = 0; i < n - 1; ++i) {
    auto e = ReadInts(input_stream);
    if (e.size() != 2) {
      Error("Expected 2 numbers for an edge");
    }
    for (auto& x : e) {
      if (x < 1 || x > n) {
        Error("Vertex out of range");
      }
      --x;
    }
    int c0 = component[e[0]];
    int c1 = component[e[1]];
    if (c1 == c0) {
      Error("Found a cycle");
    }
    for (int& x : component) {
      if (x == c0) x = c1;
    }
    edges.emplace_back(e[0], e[1]);
  }
  for (int i = 0; i < n; ++i) {
    JudgeAssert(component[i] == component[0],
                "Somehow a graph with n-1 edges and n vertices has no cycles "
                "but is also not connected");
  }

  Solver solver(edges);

  output_stream << max_m << endl;

  for (int game_id = 0; game_id < max_m; ++game_id) {
    uint64_t subset = Bit(n) - 1;
    while (subset) {
      if (solver.CanWinInOneMove(subset)) {
        Error("Ueli won");
      }
      auto res = solver.NimberMultiComponent(subset);
      JudgeAssert(res.has_value(),
                  "We reached a state that was truncated because of budget");
      int val = res.value();
      vector<int> move;
      if (val != 0) {
        move = solver.FindMultiComponentMoveToZero(subset);
      } else {
        move = solver.GetRandomMove(subset, game_id, rng);
      }
      output_stream << move.size() << endl;
      for (int i = 0; i < move.size(); ++i) {
        if (i > 0) output_stream << " ";
        output_stream << (move[i] + 1);
        JudgeAssert(subset & Bit(move[i]), "We produced an invalid move");
        subset ^= Bit(move[i]);
      }
      output_stream << endl;
      auto kv = ReadInts(input_stream);
      if (kv.size() != 1) {
        Error("Expected a single integer on the first line of a move");
      }
      auto k = kv[0];
      if (k < 1 || k > n) {
        Error("The number of vertices to change color is out of range");
      }
      auto vv = ReadInts(input_stream);
      if (vv.size() != k) {
        Error("The number of vertices to change color does not match k");
      }
      int first = -1;
      for (auto v : vv) {
        if (v < 1 || v > n) {
          Error("Vertex in a move out of range");
        }
        --v;
        if (!(subset & Bit(v))) {
          Error("Trying to take a vertex that is already taken");
        }
        if (first >= 0) {
          if (!(solver.adj_mask[first] & Bit(v))) {
            Error(
                "Trying to take a vertex not adjacent to the first taken one");
          }
        } else {
          first = v;
        }
        subset ^= Bit(v);
      }
    }
  }
}

////////////////////////////////////////////////////////////////////////////////

struct BruteForce {
  int n;
  vector<int> adj_mask;
  vector<bool> is_connected;
  vector<int> nimbers;
  explicit BruteForce(const vector<pair<int, int>> &edges) {
    n = edges.size() + 1;
    adj_mask.assign(n, 0);
    for (const auto &edge : edges) {
      adj_mask[edge.first] |= 1 << edge.second;
      adj_mask[edge.second] |= 1 << edge.first;
    }
    is_connected.assign(1 << n, false);
    for (int u = 0; u < n; ++u) {
      is_connected[1 << u] = true;
    }
    for (int p = 0; p < 1 << n; ++p) {
      if (is_connected[p]) {
        for (int u = 0; u < n; ++u) {
          if (p & adj_mask[u]) {
            is_connected[p | 1 << u] = true;
          }
        }
      }
    }
    nimbers.assign(1 << n, 0);
    for (int p = 0; p < 1 << n; ++p) {
      set<int> seen;
      for (int u = 0; u < n; ++u) {
        if (p & 1 << u) {
          const int adj_submask = p & adj_mask[u];
          for (int q = adj_submask; ; --q &= adj_submask) {
            seen.insert(nimbers[p - (1 << u) - q]);
            if (q == 0) break;
          }
        }
        for (int x = 0; ; ++x) {
          if (!seen.count(x)) {
            nimbers[p] = x;
            break;
          }
        }
      }
    }
  }
};

void TestSolverGetRootedTreeKey() {
  {
    Solver solver({});
    AssertEqual(solver.GetRootedTreeKey(0b1, 0, -1, 0),
                make_pair(2, (KeyType)0b01));
  }
  {
    // 0-1-3-4-5-8
    //   |     |
    //   2   7-6-9
    Solver solver({{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6},
                   {7, 6}, {6, 9}});
    AssertEqual(solver.GetRootedTreeKey(0b1111111111, 8, -1, 0),
                make_pair(20, (KeyType)0b00001011000010111111));
    AssertEqual(solver.GetRootedTreeKey(0b1111101111, 8, -1, 0),
                make_pair(10, (KeyType)0b0000101111));
    AssertEqual(solver.GetRootedTreeKey(0b1111101111, 3, -1, 0),
                make_pair(8, (KeyType)0b00010111));
  }
  {
    // path
    const int n = 40;
    vector<pair<int, int>> edges;
    for (int i = 0; i < n - 1; ++i) edges.emplace_back(i, i + 1);
    unsigned __int128 key = 0;
    key |= ((unsigned __int128)1 << n) - 1;
    Solver solver(edges);
    AssertEqual(solver.GetRootedTreeKey((1ULL << n) - 1, 0, -1, 0),
                make_pair(2 * n, (KeyType)key));
  }
  {
    // star
    const int n = 40;
    vector<pair<int, int>> edges;
    for (int i = 1; i < n; ++i) edges.emplace_back(0, i);
    unsigned __int128 key = 1;
    for (int i = 1; i < n; ++i) key |= (unsigned __int128)1 << (2 * i - 1);
    Solver solver(edges);
    AssertEqual(solver.GetRootedTreeKey((1ULL << n) - 1, 0, -1, 0),
                make_pair(2 * n, (KeyType)key));
  }
}

void TestSolverGetTreeKey() {
  {
    Solver solver({});
    AssertEqual(solver.GetTreeKey(0b1), (KeyType)0b01);
    AssertEqual(solver.GetTreeKey(0b1), (KeyType)0b01);  // cached
  }
  {
    Solver solver({{0, 1}});
    AssertEqual(solver.GetTreeKey(0b11), (KeyType)0b0011);
  }
  {
    Solver solver({{0, 1}, {1, 2}});
    AssertEqual(solver.GetTreeKey(0b111), (KeyType)0b001011);
  }
  {
    // 0-1-3-4-5-8
    //   |     |
    //   2   7-6-9
    Solver solver({{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6},
                   {7, 6}, {6, 9}});
    AssertEqual(solver.GetTreeKey(0b1111111111),
                (KeyType)0b00100101100001011111);  // root: 5
    AssertEqual(solver.GetTreeKey(0b1111100000),
                (KeyType)0b0010100111);  // root: 6
    AssertEqual(solver.GetTreeKey(0b0000001111),
                (KeyType)0b00101011);  // root: 1
  }
  {
    // path
    const int n = 40;
    vector<pair<int, int>> edges;
    for (int i = 0; i < n - 1; ++i) edges.emplace_back(i, i + 1);
    unsigned __int128 key = 0;
    key |= (((unsigned __int128)1 << ((n - 1) / 2)) - 1) << (2 * (n / 2) + 1);
    key |= ((unsigned __int128)1 << (n / 2 + 1)) - 1;
    Solver solver(edges);
    AssertEqual(solver.GetTreeKey((1ULL << n) - 1), (KeyType)key);
  }
  {
    // star
    const int n = 40;
    vector<pair<int, int>> edges;
    for (int i = 1; i < n; ++i) edges.emplace_back(0, i);
    unsigned __int128 key = 1;
    for (int i = 1; i < n; ++i) key |= (unsigned __int128)1 << (2 * i - 1);
    Solver solver(edges);
    AssertEqual(solver.GetTreeKey((1ULL << n) - 1), (KeyType)key);
  }
}

void TestSolverFindComponent() {
  {
    // 0-1-3-4-5-8
    //   |     |
    //   2   7-6-9
    Solver solver({{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6},
                   {7, 6}, {6, 9}});
    AssertEqual(solver.FindComponent(0b1111101111, 8, -1), 0b1111100000);
    AssertEqual(solver.FindComponent(0b1111101111, 3, -1), 0b0000001111);
  }
}

void TestSolverLargestComponentSizeForAllButOne() {
  {
    Solver solver({});
    AssertEqual(solver.LargestComponentSizeForAllButOne(0), 0);
  }
  {
    Solver solver({{0, 1}});
    AssertEqual(solver.LargestComponentSizeForAllButOne(0), 1);
    AssertEqual(solver.LargestComponentSizeForAllButOne(1), 1);
  }
  {
    // 0-1-3-4-5-8
    //   |     |
    //   2   7-6-9
    Solver solver({{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6},
                   {7, 6}, {6, 9}});
    AssertEqual(solver.LargestComponentSizeForAllButOne(4), 5);
  }
  {
    // star
    const int n = 40;
    vector<pair<int, int>> edges;
    for (int i = 1; i < n; ++i) edges.emplace_back(0, i);
    Solver solver(edges);
    AssertEqual(solver.LargestComponentSizeForAllButOne(0), 1);
  }
}

void TestSolverEnumerateMoves() {
  // 0-1-3-4-5-8
  //   |     |
  //   2   7-6-9
  const vector<pair<int, int>> edges(
      {{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6}, {7, 6}, {6, 9}});
  BruteForce brute(edges);
  Solver solver(edges);
  vector<pair<int, pair<int, int>>> calls;
  solver.EnumerateMoves(
      0b1101111111, 5,
      [&](int root, int nimber_with, int nimber_without) {
        calls.emplace_back(root, make_pair(nimber_with, nimber_without));
      },
      [&]() {
        cerr << "[TestSolverEnumerateMoves] out_of_budget_callback is called"
             << endl;
        exit(1);
      });
  sort(calls.begin(), calls.end());
  AssertEqual(calls, (vector<pair<int, pair<int, int>>>{{4, {5, 2}},
                                                        {6, {2, 1}},
                                                        {8, {1, 0}}}));
}

void TestSolverNimberSingleComponentWithRootRemoved() {
  cerr << "[TestSolverNimberSingleComponentWithRootRemoved] start" << endl;
  auto stress_test = [&](const vector<pair<int, int>> &edges) {
    BruteForce brute(edges);
    Solver solver(edges);
    for (int p = 0; p < 1 << brute.n; ++p) {
      if (brute.is_connected[p]) {
        for (int u = 0; u < brute.n; ++u) if (p & 1 << u) {
          AssertEqual(solver.NimberSingleComponentWithRootRemoved(p, u).value(),
                      brute.nimbers[p ^ 1 << u]);
        }
      }
    }
  };

  // 0-1-3-4-5-8
  //   |     |
  //   2   7-6-9
  stress_test(
      {{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6}, {7, 6}, {6, 9}});

  mt19937 rng(58);
  for (int n = 1; n <= 15; ++n) {
    for (int case_idx = 0; case_idx < 100; ++case_idx) {
      vector<pair<int, int>> edges;
      for (int i = 1; i < n; ++i) {
        edges.emplace_back(uniform_int_distribution<int>(0, i - 1)(rng), i);
      }
      stress_test(edges);
    }
  }
  {
    // The budget will exhaust.
    const vector<pair<int, int>> edges = {
      {1, 0},   {2, 0},   {3, 0},   {4, 1},   {5, 0},   {6, 2},   {7, 1},
      {8, 4},   {9, 4},   {10, 8},  {11, 0},  {12, 3},  {13, 2},  {14, 6},
      {15, 2},  {16, 8},  {17, 10}, {18, 7},  {19, 1},  {20, 10}, {21, 17},
      {22, 8},  {23, 16}, {24, 6},  {25, 14}, {26, 3},  {27, 12}, {28, 13},
      {29, 5},  {30, 6},  {31, 9},  {32, 4},  {33, 14}, {34, 25}, {35, 10},
      {36, 24}, {37, 17}, {38, 21}, {39, 20}};
    Solver solver(edges);
    AssertFalse(solver
                    .NimberSingleComponentWithRootRemoved(
                        (1ULL << solver.n) - 1, solver.n - 1)
                    .has_value());
    AssertTrue(solver.budget < 0);
    cerr << "[TestSolverNimberSingleComponentWithRootRemoved] "
            "mains_to_consider_for_first_move = "
         << solver.mains_to_consider_for_first_move << endl;
  }
  cerr << "[TestSolverNimberSingleComponentWithRootRemoved] passed" << endl;
}

void TestSolverNimberSingleComponent() {
  cerr << "[TestSolverNimberSingleComponent] start" << endl;
  auto stress_test = [&](const vector<pair<int, int>> &edges) {
    BruteForce brute(edges);
    Solver solver(edges);
    for (int p = 0; p < (1 << brute.n) - 1; ++p) {
      if (brute.is_connected[p]) {
        AssertEqual(solver.NimberSingleComponent(p).value(), brute.nimbers[p]);
      }
    }
    // For the first move, Solver only cares if it has a winning move.
    AssertEqual(solver.NimberSingleComponent((1 << brute.n) - 1).value() != 0,
                brute.nimbers[(1 << brute.n) - 1] != 0);
  };

  // 0-1-3-4-5-8
  //   |     |
  //   2   7-6-9
  stress_test(
      {{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6}, {7, 6}, {6, 9}});

  mt19937 rng(58);
  for (int n = 1; n <= 15; ++n) {
    for (int case_idx = 0; case_idx < 100; ++case_idx) {
      vector<pair<int, int>> edges;
      for (int i = 1; i < n; ++i) {
        edges.emplace_back(uniform_int_distribution<int>(0, i - 1)(rng), i);
      }
      stress_test(edges);
    }
  }
  {
    // The budget will exhaust.
    const vector<pair<int, int>> edges = {
      {1, 0},   {2, 0},   {3, 0},   {4, 1},   {5, 0},   {6, 2},   {7, 1},
      {8, 4},   {9, 4},   {10, 8},  {11, 0},  {12, 3},  {13, 2},  {14, 6},
      {15, 2},  {16, 8},  {17, 10}, {18, 7},  {19, 1},  {20, 10}, {21, 17},
      {22, 8},  {23, 16}, {24, 6},  {25, 14}, {26, 3},  {27, 12}, {28, 13},
      {29, 5},  {30, 6},  {31, 9},  {32, 4},  {33, 14}, {34, 25}, {35, 10},
      {36, 24}, {37, 17}, {38, 21}, {39, 20}};
    Solver solver(edges);
    AssertFalse(
        solver.NimberSingleComponent((1ULL << (solver.n - 1)) - 1).has_value());
    AssertTrue(solver.budget < 0);
    cerr << "[TestSolverNimberSingleComponent] "
            "mains_to_consider_for_first_move = "
         << solver.mains_to_consider_for_first_move << endl;
  }
  cerr << "[TestSolverNimberSingleComponent] passed" << endl;
}

void TestSolverNimberMultiComponent() {
  cerr << "[TestSolverNimberMultiComponent] start" << endl;
  auto stress_test = [&](const vector<pair<int, int>> &edges) {
    BruteForce brute(edges);
    Solver solver(edges);
    for (int p = 0; p < (1 << brute.n) - 1; ++p) {
      AssertEqual(solver.NimberMultiComponent(p).value(), brute.nimbers[p]);
    }
    // For the first move, Solver only cares if it has a winning move.
    AssertEqual(solver.NimberMultiComponent((1 << brute.n) - 1).value() != 0,
                brute.nimbers[(1 << brute.n) - 1] != 0);
  };

  // 0-1-3-4-5-8
  //   |     |
  //   2   7-6-9
  stress_test(
      {{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6}, {7, 6}, {6, 9}});

  mt19937 rng(58);
  for (int n = 1; n <= 15; ++n) {
    for (int case_idx = 0; case_idx < 100; ++case_idx) {
      vector<pair<int, int>> edges;
      for (int i = 1; i < n; ++i) {
        edges.emplace_back(uniform_int_distribution<int>(0, i - 1)(rng), i);
      }
      stress_test(edges);
    }
  }
  {
    // The budget will exhaust.
    const vector<pair<int, int>> edges = {
      {1, 0},   {2, 0},   {3, 0},   {4, 1},   {5, 0},   {6, 2},   {7, 1},
      {8, 4},   {9, 4},   {10, 8},  {11, 0},  {12, 3},  {13, 2},  {14, 6},
      {15, 2},  {16, 8},  {17, 10}, {18, 7},  {19, 1},  {20, 10}, {21, 17},
      {22, 8},  {23, 16}, {24, 6},  {25, 14}, {26, 3},  {27, 12}, {28, 13},
      {29, 5},  {30, 6},  {31, 9},  {32, 4},  {33, 14}, {34, 25}, {35, 10},
      {36, 24}, {37, 17}, {38, 21}, {39, 20}};
    Solver solver(edges);
    AssertFalse(
        solver.NimberMultiComponent((1ULL << (solver.n - 1)) - 1).has_value());
    AssertTrue(solver.budget < 0);
    cerr << "[TestSolverNimberMultiComponent] "
            "mains_to_consider_for_first_move = "
         << solver.mains_to_consider_for_first_move << endl;
  }
  cerr << "[TestSolverNimberMultiComponent] passed" << endl;
}

void TestSolverFindComponentTypes() {
  {
    Solver solver({});
    AssertEqual(solver.FindComponentTypes(0b1), (vector<KeyType>{0b01}));
  }
  {
    Solver solver({{0, 1}});
    AssertEqual(solver.FindComponentTypes(0b11), (vector<KeyType>{0b0011}));
  }
  {
    Solver solver({{0, 1}, {1, 2}});
    AssertEqual(solver.FindComponentTypes(0b111), (vector<KeyType>{0b001011}));
    AssertEqual(solver.FindComponentTypes(0b101),
                (vector<KeyType>{0b01, 0b01}));
  }
  {
    // 0-1-3-4-5-8
    //   |     |
    //   2   7-6-9
    Solver solver({{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6},
                   {7, 6}, {6, 9}});
    AssertEqual(
        solver.FindComponentTypes(0b1111011111),
        (vector<KeyType>{0b0010100111, 0b001011, 0b01}));  // root: 1, 6, 8
  }
  {
    // path
    auto path = [&](int n) {
      unsigned __int128 key = 0;
      key |= (((unsigned __int128)1 << ((n - 1) / 2)) - 1) << (2 * (n / 2) + 1);
      key |= ((unsigned __int128)1 << (n / 2 + 1)) - 1;
      return key;
    };
    const int n = 40;
    vector<pair<int, int>> edges;
    for (int i = 0; i < n - 1; ++i) edges.emplace_back(i, i + 1);
    Solver solver(edges);
    AssertEqual(solver.FindComponentTypes((1ULL << n) - 1),
                (vector<KeyType>{path(n)}));
    AssertEqual(solver.FindComponentTypes((1ULL << n) - 1 - (1ULL << 33) -
                                          (1ULL << 34)),
                (vector<KeyType>{path(33), path(5)}));
  }
  {
    // star
    const int n = 40;
    vector<pair<int, int>> edges;
    for (int i = 1; i < n; ++i) edges.emplace_back(0, i);
    Solver solver(edges);
    AssertEqual(solver.FindComponentTypes((1ULL << n) - 1 - (1ULL << 0)),
                (vector<KeyType>(n - 1, 0b01)));
  }
}

void TestSolverNormalizeComponentTypes() {
  Solver solver({});  // not actually used
  unsigned __int128 values[10];
  for (int i = 0; i < 10; ++i) {
    values[i] = (unsigned __int128)1 << (64 + i);
  }
  AssertEqual(solver.NormalizeComponentTypes(vector<KeyType>(1, values[0])),
              (vector<KeyType>(1, values[0])));
  AssertEqual(solver.NormalizeComponentTypes(vector<KeyType>(2, values[0])),
              (vector<KeyType>(2, values[0])));
  AssertEqual(solver.NormalizeComponentTypes(vector<KeyType>(3, values[0])),
              (vector<KeyType>(1, values[0])));
  AssertEqual(solver.NormalizeComponentTypes(vector<KeyType>(4, values[0])),
              (vector<KeyType>(2, values[0])));
  AssertEqual(solver.NormalizeComponentTypes(vector<KeyType>(5, values[0])),
              (vector<KeyType>(1, values[0])));
  AssertEqual(solver.NormalizeComponentTypes(
                  vector<KeyType>{values[9], values[7], values[8]}),
              (vector<KeyType>{values[7], values[8], values[9]}));
  AssertEqual(solver.NormalizeComponentTypes(
                  vector<KeyType>{values[4], values[3], values[4], values[1],
                                  values[4], values[3], values[4], values[3]}),
              (vector<KeyType>{values[1], values[3], values[4], values[4]}));
}

void TestSolverCanWinInOneMove() {
  {
    Solver solver({});
    AssertJudgeError(solver.CanWinInOneMove(0b0),
                     "Trying to check if we can win from an empty state");
    AssertTrue(solver.CanWinInOneMove(0b1));
  }
  {
    Solver solver({{0, 1}, {1, 2}, {2, 3}});
    AssertFalse(solver.CanWinInOneMove(0b1111));
    AssertTrue(solver.CanWinInOneMove(0b1110));
    AssertFalse(solver.CanWinInOneMove(0b1101));
    AssertFalse(solver.CanWinInOneMove(0b1011));
    AssertTrue(solver.CanWinInOneMove(0b0111));
  }
  {
    // 0-1-3-4-5-8
    //   |     |
    //   2   7-6-9
    Solver solver({{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6},
                   {7, 6}, {6, 9}});
    AssertFalse(solver.CanWinInOneMove(0b1111111111));
    AssertFalse(solver.CanWinInOneMove(0b1111100000));
    AssertTrue(solver.CanWinInOneMove(0b1011100000));
    AssertTrue(solver.CanWinInOneMove(0b0000010000));
  }
  {
    // star
    const int n = 40;
    vector<pair<int, int>> edges;
    for (int i = 1; i < n; ++i) edges.emplace_back(0, i);
    Solver solver(edges);
    AssertTrue(solver.CanWinInOneMove((1ULL << n) - 1));
    AssertFalse(solver.CanWinInOneMove((1ULL << n) - 1 - (1ULL << 0)));
    AssertTrue(solver.CanWinInOneMove((1ULL << n) - 1 - (1ULL << 1)));
  }
}

void TestSolverFindSingleComponentMoveTo() {
  cerr << "[TestSolverFindSingleComponentMoveTo] start" << endl;
  auto stress_test = [&](const vector<pair<int, int>> &edges) {
    BruteForce brute(edges);
    Solver solver(edges);
    for (int p = 0; p < 1 << brute.n; ++p) {
      if (brute.is_connected[p]) {
        // solver needs to have processed the search for the subtree.
        solver.NimberSingleComponent(p);
        for (int x = 0; x < brute.nimbers[p]; ++x) {
          if (p != (1 << brute.n) - 1 || x == 0) {
            const vector<int> move = solver.FindSingleComponentMoveTo(p, x);
            AssertFalse(move.empty());
            const int move_len = move.size();
            int q = p;
            for (int i = 0; i < move_len; ++i) {
              AssertTrue(0 <= move[i]);
              AssertTrue(move[i] < brute.n);
              AssertTrue((q & 1 << move[i]) != 0);
              q -= 1 << move[i];
            }
            for (int i = 1; i < move_len; ++i) {
              AssertTrue((brute.adj_mask[move[0]] & 1 << move[i]) != 0);
            }
            AssertEqual(brute.nimbers[q], x);
          }
        }
      }
    }
  };

  // 0-1-3-4-5-8
  //   |     |
  //   2   7-6-9
  stress_test(
      {{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6}, {7, 6}, {6, 9}});

  mt19937 rng(58);
  for (int n = 1; n <= 15; ++n) {
    for (int case_idx = 0; case_idx < 100; ++case_idx) {
      vector<pair<int, int>> edges;
      for (int i = 1; i < n; ++i) {
        edges.emplace_back(uniform_int_distribution<int>(0, i - 1)(rng), i);
      }
      stress_test(edges);
    }
  }
  cerr << "[TestSolverFindSingleComponentMoveTo] passed" << endl;
}

void TestSolverFindMultiComponentMoveToZero() {
  cerr << "[TestSolverFindMultiComponentMoveToZero] start" << endl;
  auto stress_test = [&](const vector<pair<int, int>> &edges) {
    BruteForce brute(edges);
    Solver solver(edges);
    for (int p = 0; p < 1 << brute.n; ++p) {
      if (brute.nimbers[p] != 0) {
        const vector<int> move = solver.FindMultiComponentMoveToZero(p);
        AssertFalse(move.empty());
        const int move_len = move.size();
        int q = p;
        for (int i = 0; i < move_len; ++i) {
          AssertTrue(0 <= move[i]);
          AssertTrue(move[i] < brute.n);
          AssertTrue((q & 1 << move[i]) != 0);
          q -= 1 << move[i];
        }
        for (int i = 1; i < move_len; ++i) {
          AssertTrue((brute.adj_mask[move[0]] & 1 << move[i]) != 0);
        }
        AssertEqual(brute.nimbers[q], 0);
      }
    }
  };

  // 0-1-3-4-5-8
  //   |     |
  //   2   7-6-9
  stress_test(
      {{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6}, {7, 6}, {6, 9}});

  mt19937 rng(58);
  for (int n = 1; n <= 15; ++n) {
    for (int case_idx = 0; case_idx < 100; ++case_idx) {
      vector<pair<int, int>> edges;
      for (int i = 1; i < n; ++i) {
        edges.emplace_back(uniform_int_distribution<int>(0, i - 1)(rng), i);
      }
      stress_test(edges);
    }
  }
  cerr << "[TestSolverFindMultiComponentMoveToZero] passed" << endl;
}

void TestSolverGetRandomMove() {
  cerr << "[TestSolverGetRandomMove] start" << endl;
  mt19937 rng_solver(20200604);
  auto stress_test = [&](const vector<pair<int, int>> &edges) {
    BruteForce brute(edges);
    Solver solver(edges);
    for (int p = 1; p < 1 << brute.n; ++p) {
      for (int game_id = 0; game_id < 10; ++game_id) {
        const vector<int> move = solver.GetRandomMove(p, game_id, rng_solver);
        AssertFalse(move.empty());
        const int move_len = move.size();
        int q = p;
        for (int i = 0; i < move_len; ++i) {
          AssertTrue(0 <= move[i]);
          AssertTrue(move[i] < brute.n);
          AssertTrue((q & 1 << move[i]) != 0);
          q -= 1 << move[i];
        }
        for (int i = 1; i < move_len; ++i) {
          AssertTrue((brute.adj_mask[move[0]] & 1 << move[i]) != 0);
        }
      }
    }
  };

  // 0-1-3-4-5-8
  //   |     |
  //   2   7-6-9
  stress_test(
      {{0, 1}, {1, 3}, {3, 4}, {4, 5}, {5, 8}, {1, 2}, {5, 6}, {7, 6}, {6, 9}});

  mt19937 rng(58);
  for (int n = 1; n <= 15; ++n) {
    for (int case_idx = 0; case_idx < 100; ++case_idx) {
      vector<pair<int, int>> edges;
      for (int i = 1; i < n; ++i) {
        edges.emplace_back(uniform_int_distribution<int>(0, i - 1)(rng), i);
      }
      stress_test(edges);
    }
  }

  // Check the output to see good random moves.
  // Also this hacks mains_to_consider_for_first_move because these are winning
  // positions and solver finds the first move immediately.
  {
    // path
    const int n = 40;
    const int m = 50;
    vector<pair<int, int>> edges;
    for (int i = 0; i < n - 1; ++i) edges.emplace_back(i, i + 1);
    Solver solver(edges);
    solver.mains_to_consider_for_first_move = {0, 33};
    vector<vector<int>> moves(m);
    for (int game_id = 0; game_id < m; ++game_id) {
      moves[game_id] =
          solver.GetRandomMove((1ULL << n) - 1, game_id, rng_solver);
      // Expected to repeat 6 possible moves.
      if (game_id >= 6) {
        AssertEqual(moves[game_id - 6], moves[game_id]);
      }
    }
    AssertTrue((set(moves.begin(), moves.begin() + 6)) ==
               (set{vector<int>{0}, vector<int>{0, 1}, vector<int>{33},
                    vector<int>{33, 32}, vector<int>{33, 34},
                    vector<int>{33, 32, 34}}));
  }
  {
    // star
    const int n = 40;
    const int m = 50;
    vector<pair<int, int>> edges;
    for (int i = 1; i < n; ++i) edges.emplace_back(0, i);
    Solver solver(edges);
    solver.mains_to_consider_for_first_move = {0};
    vector<vector<int>> moves(m);
    for (int game_id = 0; game_id < m; ++game_id) {
      moves[game_id] =
          solver.GetRandomMove((1ULL << n) - 1, game_id, rng_solver);
      // Expected to alternate parity for the number of remaining leaves.
      if (game_id >= 1) {
        AssertTrue(moves[game_id - 1].size() % 2 != moves[game_id].size() % 2);
      }
    }
  }

  cerr << "[TestSolverGetRandomMove] passed" << endl;
}

void TestSolver() {
  TestSolverGetRootedTreeKey();
  TestSolverGetTreeKey();
  TestSolverFindComponent();
  TestSolverLargestComponentSizeForAllButOne();
  TestSolverEnumerateMoves();
  TestSolverNimberSingleComponentWithRootRemoved();
  TestSolverNimberSingleComponent();
  TestSolverNimberMultiComponent();
  TestSolverFindComponentTypes();
  TestSolverNormalizeComponentTypes();
  TestSolverCanWinInOneMove();
  TestSolverFindSingleComponentMoveTo();
  TestSolverFindMultiComponentMoveToZero();
  TestSolverGetRandomMove();
}

void Test() {
  TestSolver();
  // TODO(yhos): Write other tests.
}

////////////////////////////////////////////////////////////////////////////////

// This is not used in the final judge, but was used during the exploration
// of hyperparameters so keeping it in case we need to re-explore.
void Explore() {
  vector<pair<int, int>> edges = {
      {1, 0},   {2, 0},   {3, 0},   {4, 1},   {5, 0},   {6, 2},   {7, 1},
      {8, 4},   {9, 4},   {10, 8},  {11, 0},  {12, 3},  {13, 2},  {14, 6},
      {15, 2},  {16, 8},  {17, 10}, {18, 7},  {19, 1},  {20, 10}, {21, 17},
      {22, 8},  {23, 16}, {24, 6},  {25, 14}, {26, 3},  {27, 12}, {28, 13},
      {29, 5},  {30, 6},  {31, 9},  {32, 4},  {33, 14}, {34, 25}, {35, 10},
      {36, 24}, {37, 17}, {38, 21}, {39, 20}};
  for (int n = 40; n <= edges.size() + 1; ++n) {
    vector<pair<int, int>> curEdges(edges.begin(), edges.begin() + (n - 1));
    auto start = clock();
    Solver solver(curEdges);
    double elapsed = (clock() - start) / (double)CLOCKS_PER_SEC;
    int max_nimber = 0;
    for (auto p : solver.nimber) {
      max_nimber = max(max_nimber, p.second);
    }
    cerr << "n=" << n << ": " << solver.nimber.size() << " states, " << elapsed
         << "s, max nimber = " << max_nimber << ", explored "
         << solver.mains_to_consider_for_first_move.size() << "/" << n
         << ", lru size = " << solver.lru.lookup.size()
         << ", starting nimber = "
         << solver.NimberSingleComponent((uint64_t(1) << n) - 1).value()
         << endl;
  }
}

// This is not used in the final judge, but was used during the exploration
// of hyperparameters so keeping it in case we need to re-explore.
void Explore2() {
  vector<pair<int, int>> edges;
  for (int n = 2; n <= 40; ++n) {
    int bp = -1;
    int best_states = 0;
    for (int p = 0; p < n - 1; ++p) {
      edges.emplace_back(n - 1, p);
      Solver solver(edges);
      int states = solver.nimber.size();
      if (states > best_states) {
        best_states = states;
        bp = p;
      }
      edges.pop_back();
    }
    edges.emplace_back(n - 1, bp);
    cerr << "Best states for n=" << n << ": " << best_states << endl;
  }
  for (auto e : edges) {
    cerr << e.first << " " << e.second << endl;
  }
}

// This is not used in the final judge, but was used during the exploration
// of hyperparameters so keeping it in case we need to re-explore.
struct ExploreCandidate {
  int states;
  vector<pair<int, int>> edges;
};

bool operator<(const ExploreCandidate& a, const ExploreCandidate& b) {
  return a.states < b.states;
}

void Explore3() {
  vector<vector<pair<int, int>>> candidates;
  candidates.emplace_back();
  int BUBEN = 20;
  int ATTS = 10;
  mt19937 rng(57);
  for (int n = 2; n <= 40; ++n) {
    int best_zero_states = 0;
    vector<pair<int, int>> best_zero;
    set<ExploreCandidate> new_candidates;
    for (auto edges : candidates) {
      // if (best_zero_states > 0) break;
      for (int att = 0; att < ATTS; ++att) {
        int p = uniform_int_distribution<int>(0, n - 2)(rng);
        edges.emplace_back(n - 1, p);
        Solver solver(edges);
        int states = solver.nimber.size();
        int got = solver.NimberSingleComponent(Bit(n) - 1).value();
        if (got == 0 && states > best_zero_states) {
          best_zero_states = states;
          best_zero = edges;
        }
        new_candidates.insert({.states = states, .edges = edges});
        while (new_candidates.size() > BUBEN) {
          new_candidates.erase(new_candidates.begin());
        }
        edges.pop_back();
      }
    }
    cerr << "Best states for n=" << n << ": " << new_candidates.rbegin()->states
         << ", and with zero: " << best_zero_states << ", propagating "
         << new_candidates.size() << " candidates" << endl;

    if (best_zero_states) {
      cout << "n = " << n << endl;
      for (auto e : best_zero) {
        cout << e.first << " " << e.second << endl;
      }
      cout.flush();
    }

    candidates.clear();
    for (auto p : new_candidates) {
      candidates.push_back(p.edges);
    }
    reverse(candidates.begin(), candidates.end());
  }
}

void Explore4() {
  // Remember to comment out "if (seen & Bit(0)) ... break;" section above when
  // rerunning this.
  cerr << "----" << endl;
  double total_time = 0.0;
  mt19937 rng(57);
  for (int n = 2; n <= 40; ++n) {
    auto start = clock();
    vector<pair<int, int>> edges;
    for (int i = 1; i < n; ++i) {
      edges.emplace_back(i, uniform_int_distribution<int>(0, i - 1)(rng));
    }
    Solver solver(edges);
    double elapsed = (clock() - start) / double(CLOCKS_PER_SEC);
    total_time += elapsed;
    cerr << "n = " << n << ", " << solver.nimber.size()
         << " states, elapsed: " << elapsed << "s" << endl;
  }
  cerr << "Total time: " << total_time << "s" << endl;
}

int main(int argc, char* argv[]) {
  signal(SIGPIPE, SIG_IGN);
  if (argc == 2 && string(argv[1]) == "-2") {
    TestLib();
    Test();
    cerr << "All tests passed!" << endl;
    return 0;
  }
  // error_file is not set up yet, so we use assert.
  assert(argc == 3);
  error_file.open(argv[2]);
  int dataset_index = ParseInt(argv[1]);
  istream& input_stream = cin;
  ostream& output_stream = cout;
  int max_m = 50;
  int num_cases;
  int min_n;
  int max_n;
  if (dataset_index == 0) {
    num_cases = 1;
    min_n = 30;
    max_n = 30;
  } else if (dataset_index == 1) {
    num_cases = 10;
    min_n = 31;
    max_n = 40;
  } else {
    JudgeError("Wrong dataset index");
  }
  mt19937 rng(57);
  output_stream << num_cases << endl;
  for (int case_idx = 1; case_idx <= num_cases; case_idx++) {
    RunCase(input_stream, output_stream, case_idx, min_n, max_n, max_m, rng);
  }
  string token;
  if (input_stream >> token) Error("Additional output found");
  error_file << "status: VALID" << endl;
  return 0;
}
