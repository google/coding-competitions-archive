#include <algorithm>
#include <cassert>
#include <cctype>
#include <csignal>
#include <fstream>
#include <iostream>
#include <numeric>
#include <sstream>
#include <vector>
using namespace std;

constexpr int N = 50;
constexpr int T = 2000;
constexpr int W[3] = {1200, 1560, 1720};

ostream& operator<<(ostream& out, const vector<char>& v) {
  out << "[";
  for (const char& t : v) out << (int)t << ", ";
  return out << "]";
}

template <typename T>
ostream& operator<<(ostream& out, const vector<T>& v) {
  out << "[";
  for (const T& t : v) out << t << ", ";
  return out << "]";
}

template <typename T, typename U>
ostream& operator<<(ostream& out, const pair<T, U>& p) {
  return out << "<" << p.first << "," << p.second << ">";
}

bool mocked_error;
string last_error;

void Error(const string& msg) {
  if (mocked_error) {
    last_error = msg;
    // throw to avoid additional errors.
    throw 1;
  } else {
    cout << -1 << endl;
    cerr << msg << endl;
    exit(1);
  }
}

#define AssertError(call, err) \
  mocked_error = true;         \
  try {                        \
    call;                      \
  } catch (...) {              \
  }                            \
  assert(last_error == err);   \
  last_error = "";             \
  mocked_error = false;

string Strint(long long n) {
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
long long ParseInt(const string& ss) {
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
  long long r;
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

string ReadLine() {
  string l;
  getline(cin, l);
  return l;
}

pair<int, int> ReadInRangeInts(const string& l, int n) {
  auto t = Tokenize(l);
  if (t.size() != 2) Error("Wrong number of tokens");
  long long a = ParseInt(t[0]);
  if (a < 1 || a > n) Error("Integer not in range");
  long long b = ParseInt(t[1]);
  if (b < 1 || b > n) Error("Integer not in range");
  return {a - 1, b - 1};
}

void TestReadInRangeInts() {
  assert(ReadInRangeInts("  1  2  ", 50) == make_pair(0, 1));
  assert(ReadInRangeInts("10 20", 20) == make_pair(9, 19));
  AssertError(ReadInRangeInts("z", 20), "Wrong number of tokens");
  AssertError(ReadInRangeInts("1 10 1", 20), "Wrong number of tokens");
  AssertError(ReadInRangeInts("-1 10", 50), "Integer not in range");
  AssertError(ReadInRangeInts("1 51", 50), "Integer not in range");
  AssertError(ReadInRangeInts("0 1", 2), "Integer not in range");
}

void TestLib() {
  TestStrint();
  TestTruncate();
  TestParseInt();
  TestLowercase();
  TestTokenize();
  TestReadInRangeInts();
}

//////////////////////////////////////////////

constexpr long long ones[9] = {0,
                               1,
                               0x101,
                               0x10101,
                               0x1010101,
                               0x101010101,
                               0x10101010101,
                               0x1010101010101,
                               0x101010101010101};

// Only works if no value to be incremented is -1. Otherwise, overflow
// may be interpreted as carry instead of ignored.
void Add1ToRange(vector<char>& v, int incl_min, int excl_max) {
  if (incl_min <= excl_max - 8)
    for (long long* llv = (long long*)(&v[incl_min]);
         llv <= (long long*)(&v[excl_max - 8]); ++llv) {
      (*llv) += ones[8];
    }
  int left_over = (excl_max - incl_min) & 0x7;  // % 8.
  *((long long*)(&v[excl_max - left_over])) += ones[left_over];
}

void TestAdd1ToRange() {
  vector<char> v(100), v2(100);
  auto Reset = [&]() {
    iota(v.begin(), v.end(), 0);
    iota(v2.begin(), v2.end(), 0);
  };
  Reset();
  assert(v == v2);
  auto Add1ToRangeTrivial = [](vector<char>& v, int incl_min, int excl_max) {
    for (int i = incl_min; i < excl_max; ++i) v[i]++;
  };
  auto Add1ToBothRanges = [&](int incl_min, int excl_max) {
    Add1ToRange(v, incl_min, excl_max);
    Add1ToRangeTrivial(v2, incl_min, excl_max);
    return v == v2;
  };
  for (int i = 0; i < 100; ++i) {
    for (int j = i; j < 100; ++j) {
      if ((i + j) % 20 == 0) Reset();  // Prevent overflow.
      if (!Add1ToBothRanges(i, j)) {
        cerr << "Failed at " << i << ";" << j << endl;
        cerr << "v:";
        for (int i = 0; i < 100; ++i) cerr << " " << (int)v[i];
        cerr << endl << "v2:";
        for (int i = 0; i < 100; ++i) cerr << " " << (int)v2[i];
        cerr << endl;
        assert(false);
      }
    }
  }
}

void UpdateScores(vector<vector<char>>& scores, int ii, int jj) {
  for (int i = 0; i < ii; ++i) Add1ToRange(scores[i], jj + 1, scores.size());
  for (int i = ii + 1; i < scores.size(); ++i) Add1ToRange(scores[i], 0, jj);
}

void TestUpdateScores() {
  auto CheckUpdateScores = [](const vector<vector<char>>& iniscores, int ii,
                              int jj, const vector<vector<char>>& finscores) {
    auto scores = iniscores;
    UpdateScores(scores, ii, jj);
    return scores == finscores;
  };
  assert(CheckUpdateScores(
      {{0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}}, 1, 1,
      {{0, 0, 1, 1}, {0, 0, 0, 0}, {1, 0, 0, 0}, {1, 0, 0, 0}}));
  assert(CheckUpdateScores(
      {{0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}}, 0, 1,
      {{0, 0, 0, 0}, {1, 0, 0, 0}, {1, 0, 0, 0}, {1, 0, 0, 0}}));
  assert(CheckUpdateScores(
      {{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}, {13, 14, 15, 16}}, 0, 2,
      {{1, 2, 3, 4}, {6, 7, 7, 8}, {10, 11, 11, 12}, {14, 15, 15, 16}}));
}

int BestScore(const vector<bool>& used_north, const vector<bool>& used_south,
              const vector<vector<char>>& scores) {
  int n = scores.size();
  int r = 0;
  for (int i = 0; i < n; ++i)
    if (!used_north[i])
      for (int j = 0; j < n; ++j)
        if (!used_south[j] && scores[i][j] > r) r = scores[i][j];
  return r;
}

void TestBestScore() {
  assert(BestScore({0, 0, 0}, {0, 0, 0}, {{1, 2, 3}, {5, 7, 4}, {7, 1, 2}}) ==
         7);
  assert(BestScore({0, 0, 0}, {0, 0, 0}, {{8, 2, 3}, {5, 7, 4}, {7, 1, 2}}) ==
         8);
  assert(BestScore({0, 0, 0}, {0, 0, 0}, {{8, 2, 3}, {5, 7, 4}, {7, 1, 9}}) ==
         9);
  assert(BestScore({1, 0, 0}, {0, 0, 0}, {{8, 2, 3}, {5, 7, 4}, {7, 1, 2}}) ==
         7);
  assert(BestScore({1, 0, 0}, {0, 0, 1}, {{8, 2, 3}, {5, 7, 4}, {7, 1, 9}}) ==
         7);
  assert(BestScore({1, 1, 0}, {1, 0, 1}, {{8, 2, 3}, {5, 7, 4}, {7, 1, 9}}) ==
         1);
}

vector<pair<int, int>> PlaysOfScore(int score, const vector<bool>& used_north,
                                    const vector<bool>& used_south,
                                    const vector<vector<char>>& scores) {
  int n = scores.size();
  vector<pair<int, int>> r;
  for (int i = 0; i < n; ++i)
    if (!used_north[i])
      for (int j = 0; j < n; ++j)
        if (!used_south[j] && scores[i][j] == score) r.emplace_back(i, j);
  return r;
}

void TestPlaysOfScore() {
  assert(PlaysOfScore(7, {0, 0, 0}, {0, 0, 0},
                      {{1, 2, 3}, {5, 7, 4}, {7, 1, 2}}) ==
         (vector<pair<int, int>>{{1, 1}, {2, 0}}));
  assert(PlaysOfScore(1, {0, 0, 0}, {0, 0, 0},
                      {{1, 2, 3}, {5, 7, 4}, {7, 1, 2}}) ==
         (vector<pair<int, int>>{{0, 0}, {2, 1}}));
  assert(PlaysOfScore(1, {1, 0, 0}, {0, 0, 0},
                      {{1, 2, 3}, {5, 7, 4}, {7, 1, 2}}) ==
         (vector<pair<int, int>>{{2, 1}}));
}

vector<pair<int, int>> BestPlays(const vector<bool>& used_north,
                                 const vector<bool>& used_south,
                                 const vector<vector<char>>& scores) {
  return PlaysOfScore(BestScore(used_north, used_south, scores), used_north,
                      used_south, scores);
}

void TestBestPlays() {
  assert(BestPlays({0, 0, 0}, {0, 0, 0}, {{1, 2, 3}, {5, 7, 4}, {7, 1, 2}}) ==
         (vector<pair<int, int>>{{1, 1}, {2, 0}}));
  assert(BestPlays({0, 1, 0}, {1, 0, 0}, {{1, 2, 3}, {5, 7, 4}, {7, 1, 2}}) ==
         (vector<pair<int, int>>{{0, 2}}));  // 3 is the best.
}

class Input {
 public:
  Input() {}
  virtual ~Input() {}
  virtual string NextLine() { return ReadLine(); }
};

class MockInput : public Input {
 public:
  virtual ~MockInput() { assert(i_ == lines_.size()); }
  MockInput(const vector<string>& lines) : i_(0), lines_(lines) {}
  string NextLine() override {
    assert(i_ < lines_.size());
    return lines_[i_++];
  }

 private:
  int i_;
  vector<string> lines_;
};

class Output {
 public:
  Output() {}
  virtual ~Output() {}
  virtual void Write(const string& line) {
    cout << line << endl;
  }
};

class MockOutput : public Output {
 public:
  ~MockOutput() {}
  void Write(const string& line) override { lines_.push_back(line); }
  vector<string> lines() { return lines_; }

 private:
  vector<string> lines_;
};

class Random {
 public:
  Random() {}
  Random(int seed) { srand(seed); }
  virtual ~Random() {}
  // The non-uniformity of the distribution, given that n < 2500, is negligible.
  virtual int Next(int n) { return rand() % n; };
  template <typename T>
  T RandomElement(const vector<T>& v) {
    return v[Next(v.size())];
  }
};

class MockRandom : public Random {
 public:
  MockRandom(const vector<int>& picks) : i_(0), picks_(picks) {}
  ~MockRandom() { assert(i_ == picks_.size()); }
  int Next(int n) override {
    assert(i_ < picks_.size() && 0 <= picks_[i_] && picks_[i_] < n);
    return picks_[i_++];
  }

 private:
  int i_;
  vector<int> picks_;
};

// Returns the users' score minus the judge's score. > 0 if user wins.
int RunCase(int n, Input* in, Output* out, Random* rnd) {
  vector<vector<char>> scores(2 * n, vector<char>(2 * n));
  vector<bool> used_north(2 * n), used_south(2 * n);
  int user_score = 0, judge_score = 0;
  for (int i = 0; i < n; ++i) {
    const auto& [a, b] = ReadInRangeInts(in->NextLine(), 2 * n);
    if (used_north[a]) Error("Used north tree");
    if (used_south[b]) Error("Used south tree");
    user_score += scores[a][b];
    used_north[a] = true;
    used_south[b] = true;
    UpdateScores(scores, a, b);
    const auto& [c, d] =
        rnd->RandomElement(BestPlays(used_north, used_south, scores));
    assert(!used_north[c]);
    assert(!used_south[d]);
    judge_score += scores[c][d];
    UpdateScores(scores, c, d);
    used_north[c] = true;
    used_south[d] = true;
    out->Write(Strint(c + 1) + " " + Strint(d + 1));
  }
  out->Write(Strint(user_score > judge_score ? 1 : 0));
  return user_score - judge_score;
}

void TestRunCase() {
  auto MockRunCase = [](int n, const vector<string>& in_lines,
                        const vector<int>& rnd_vals,
                        const vector<string>& exp_out_lines) {
    MockInput in(in_lines);
    MockOutput out;
    MockRandom rnd(rnd_vals);
    int r = RunCase(n, &in, &out, &rnd);
    assert(out.lines() == exp_out_lines);
    return r;
  };
  AssertError(MockRunCase(1, {"z 1"}, {}, {}), "Not an integer in range: z");
  AssertError(MockRunCase(1, {"9999999999999999999 1"}, {}, {}),
              "Not an integer in range: 9999999999999999999");
  AssertError(MockRunCase(1, {"1 1 1"}, {}, {}), "Wrong number of tokens");
  AssertError(MockRunCase(1, {"0 1"}, {}, {}), "Integer not in range");
  AssertError(MockRunCase(1, {"1 3"}, {}, {}), "Integer not in range");
  assert(MockRunCase(1, {"1 1"}, {0}, {"2 2", "0"}) == 0);
  assert(MockRunCase(1, {"2 1"}, {0}, {"1 2", "0"}) == -1);
  assert(MockRunCase(2, {"2 1", "3 4"}, {0, 0}, {"1 2", "4 3", "0"}) == -2);
  assert(MockRunCase(2, {"2 1", "3 3"}, {2, 0}, {"1 4", "4 2", "0"}) == -2);
  assert(MockRunCase(2, {"1 1", "2 3"}, {3, 0}, {"3 2", "4 4", "1"}) == 1);
  AssertError(MockRunCase(2, {"1 1", "3 4"}, {3}, {"3 2"}), "Used north tree");
  AssertError(MockRunCase(2, {"1 1", "4 2"}, {3}, {"3 2"}), "Used south tree");
}

void Test() {
  TestAdd1ToRange();
  TestUpdateScores();
  TestBestScore();
  TestPlaysOfScore();
  TestBestPlays();
  TestRunCase();
}

int main(int argc, const char* argv[]) {
  signal(SIGPIPE, SIG_IGN);
  if (argc == 2 && string(argv[1]) == "-2") {
    TestLib();
    Test();
    // cerr << "All tests passed!" << endl;
    return 0;
  }
  if (argc != 2 || argv[1][0] == 0 || argv[1][1] != 0) return 1;
  int input_index = argv[1][0] - '0';
  if (input_index < 0 || input_index > 2) return 1;
  Input in;
  Output out;
  int seed = (input_index + 3453 + time(nullptr)) % 10000;
  cerr << "seed = " << seed << endl;
  Random rnd(seed);
  out.Write(Strint(T) + " " + Strint(N) + " " + Strint(W[input_index]));
  int wins = 0;
  for (int i = 0; i < T; ++i) {
    if (RunCase(N, &in, &out, &rnd) > 0) wins++;
  }
  cerr << "User won " << wins << " out of " << T << " games ("
       << (100.0 * wins / T) << "%). " << W[input_index]
       << " wins needed for CORRECT." << endl;
  if (wins < W[input_index]) Error("Not enough wins");
  string extra_line;
  if (getline(cin, extra_line)) Error("Extra output after end");
  return 0;
}
