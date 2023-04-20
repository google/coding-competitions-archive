#include <cassert>
#include <cctype>
#include <fstream>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <vector>
using namespace std;

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

void Error(const string& msg) {
  if (mocked_error) {
    last_error = msg;
    // throw to avoid additional errors.
    throw 1;
  } else {
    cerr << msg << endl;
    exit(1);
  }
}

string JudgeErrorStr(const string& msg) { return "JUDGE_ERROR! " + msg; }

void JudgeError(const string& msg) { Error(JudgeErrorStr(msg)); }

#define AssertEqual(a, b)                                    \
  {                                                          \
    auto ___va = a;                                          \
    auto ___vb = b;                                          \
    if (!(___va == ___vb)) {                                 \
      cerr << "`" << ___va << "` is not equal to `" << ___vb \
           << "` as requested. " << endl;                    \
      assert(___va == ___vb);                                \
    }                                                        \
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

vector<vector<string>> ReadAndTokenizeFileLines(const string& filename) {
  ifstream in(filename);
  string s;
  vector<vector<string>> r;
  while (getline(in, s)) {
    vector<string> tokens = Tokenize(s);
    if (!tokens.empty()) r.push_back(tokens);
  }
  return r;
}

vector<vector<vector<string>>> SplitCases(const vector<vector<string>>& lines) {
  vector<vector<vector<string>>> cases;
  for (const vector<string>& line : lines) {
    if (line.size() >= 2 && line[0] == "case" &&
        line[1][0] == '#') {  // New case line, like python judges define it.
      if (line[1].size() < 3 || line[1][line[1].size() - 1] != ':')
        Error("Bad format in case line");
      const string case_num = line[1].substr(1, line[1].size() - 2);
      if (ParseInt(case_num) != cases.size() + 1) {
        Error(string("Found case: ") + Truncate(case_num) +
              ", expected: " + Strint(cases.size() + 1));
      }
      vector<string> new_line(line);
      new_line.erase(new_line.begin(), new_line.begin() + 2);
      cases.push_back(vector<vector<string>>(1, new_line));
    } else {
      if (cases.empty()) Error("First line doesn't start with case #1:");
      cases.back().push_back(line);
    }
  }
  return cases;
}

void TestSplitCases() {
  auto SplitLines = [](const vector<string>& v) {
    vector<vector<string>> r;
    r.reserve(v.size());
    for (string s : v) r.push_back(Tokenize(s));
    return SplitCases(r);
  };
  assert(Eq(SplitLines({"Case   #1:  A  "}), {{{"a"}}}));
  assert(Eq(SplitLines({"Case\t#1:  A  ", "  cASE \t\t #2:\t   b  c  "}),
            {{{"a"}}, {{"b", "c"}}}));
  assert(Eq(SplitLines({"Case #01:  a  ", "x   y", "  z w ",
                        "CASE #0000002:", "   b  c  ", "WWWW"}),
            {{{"a"}, {"x", "y"}, {"z", "w"}}, {{}, {"b", "c"}, {"wwww"}}}));
  assert(Eq(SplitLines({"Case #1:", "", "  z w ", "CASE #2:", "", ""}),
            {{{}, {}, {"z", "w"}}, {{}, {}, {}}}));
  AssertError(SplitLines({"Case #1:", "case", "#1:", "CASE # 2:", "case #3:"}),
              "Bad format in case line");
  AssertError(SplitLines({"Case #1:", "case", "#1:", "CASE #2 :", "case #3:"}),
              "Bad format in case line");
  AssertError(SplitLines({"Case #1:", "case #1:"}),
              "Found case: 1, expected: 2");
  AssertError(SplitLines({"Case #2:", "case #1:"}),
              "Found case: 2, expected: 1");
  AssertError(SplitLines({"Case #0:", "case #1:"}),
              "Found case: 0, expected: 1");
  AssertError(SplitLines({"Case #-1:", "case #1:"}),
              "Found case: -1, expected: 1");
  AssertError(SplitLines({"Case #xyz:", "case #1:"}),
              "Not an integer in range: xyz");
  AssertError(SplitLines({"Case #ONE:", "case #1:"}),
              "Not an integer in range: one");
  AssertError(SplitLines({"Case #1.0:", "case #1:"}),
              "Not an integer in range: 1.0");
  AssertError(SplitLines({"Case #1:", "case", "#1:", "case #3:"}),
              "Found case: 3, expected: 2");
  AssertError(SplitLines({"Case #1:", "case", "#1:", "case #02:", "case #2:"}),
              "Found case: 2, expected: 3");
  AssertError(SplitLines({"Case#1:A"}),
              "First line doesn't start with case #1:");
  AssertError(SplitLines({"Case#1: A"}),
              "First line doesn't start with case #1:");
  AssertError(SplitLines({"Case #1:A"}), "Bad format in case line");
  AssertError(SplitLines({"Case #: A"}), "Bad format in case line");
  assert(Eq(SplitLines({"Case #1: A B", "Case#2:A"}),
            {{{"a", "b"}, {"case#2:a"}}}));
  assert(Eq(SplitLines({"Case #1: A B", "Case#2: A"}),
            {{{"a", "b"}, {"case#2:", "a"}}}));
  AssertError(SplitLines({"Case #1: A B", "Case #2:A"}),
              "Bad format in case line");
  AssertError(SplitLines({"Case # 1: A"}), "Bad format in case line");
  AssertError(SplitLines({"Case #1 : A"}), "Bad format in case line");
  AssertError(SplitLines({"Case# 1: A"}),
              "First line doesn't start with case #1:");
  AssertError(SplitLines({"Cases #1: A"}),
              "First line doesn't start with case #1:");
  assert(Eq(SplitLines({"Case #01: A"}), {{{"a"}}}));
  AssertError(SplitLines({"", "Cases #1: A"}),
              "First line doesn't start with case #1:");
}

template <typename T>
vector<T> ParseAllInput(const string& filename, T ParseCaseInputF(istream&)) {
  ifstream in(filename);
  int t;
  in >> t;
  vector<T> v(t);
  for (int i = 0; i < t; ++i) v[i] = ParseCaseInputF(in);
  return v;
}

template <typename U>
vector<U> ParseAllOutput(const string& filename,
                         U ParseCaseOutputF(const vector<vector<string>>&)) {
  vector<vector<vector<string>>> tokenized_lines =
      SplitCases(ReadAndTokenizeFileLines(filename));
  vector<U> v(tokenized_lines.size());
  for (int i = 0; i < tokenized_lines.size(); ++i)
    v[i] = ParseCaseOutputF(tokenized_lines[i]);
  return v;
}

template <typename T, typename U>
string JudgeAllCases(const vector<T>& input, const vector<U>& attempt,
                     string JudgeCase(const T&, const U&)) {
  if (attempt.size() != input.size())
    Error(string("Wrong number of cases in attempt: ") +
          Strint(attempt.size()) + ", expected: " + Strint(input.size()));
  for (int i = 0; i < input.size(); ++i) {
    string e = JudgeCase(input[i], attempt[i]);
    if (e.empty()) continue;
    ostringstream out;
    out << "Case #" << (i + 1) << ": " << e;
    return out.str();
  }
  return "";
}

string JudgeCaseTest(const int& n, const int& o) {
  if (n != o) return Strint(o) + " not equal to input: " + Strint(n);
  return "";
};

void TestJudgeAllCases() {
  AssertError(JudgeAllCases({1}, {1, 2}, JudgeCaseTest),
              "Wrong number of cases in attempt: 2, expected: 1");
  AssertError(JudgeAllCases({1, 2}, {1}, JudgeCaseTest),
              "Wrong number of cases in attempt: 1, expected: 2");
  AssertError(JudgeAllCases({1, 2}, {}, JudgeCaseTest),
              "Wrong number of cases in attempt: 0, expected: 2");
  assert(JudgeAllCases({1}, {1}, JudgeCaseTest) == "");
  assert(JudgeAllCases({1}, {2}, JudgeCaseTest) ==
         "Case #1: 2 not equal to input: 1");
  assert(JudgeAllCases({1, 1}, {2, 2}, JudgeCaseTest) ==
         "Case #1: 2 not equal to input: 1");
  assert(JudgeAllCases({1, 2}, {1, 2}, JudgeCaseTest) == "");
  assert(JudgeAllCases({1, 2}, {1, 1}, JudgeCaseTest) ==
         "Case #2: 1 not equal to input: 2");
}

void TestLib() {
  TestStrint();
  TestTruncate();
  TestParseInt();
  TestLowercase();
  TestTokenize();
  TestSplitCases();
  TestJudgeAllCases();
}

//////////////////////////////////////////////

typedef long long ll;

struct pt {
  ll x, y;
  pt operator-(const pt& o) const { return {x - o.x, y - o.y}; }
  pt operator+(const pt& o) const { return {x + o.x, y + o.y}; }
  ll operator%(const pt& o) const { return x * o.y - y * o.x; }  // cross
  bool operator==(const pt& o) const { return x == o.x && y == o.y; }
  bool operator<(const pt& o) const { return x != o.x ? x < o.x : y < o.y; }
};

ostream& operator<<(ostream& o, const pt& p) { return o << p.x << "," << p.y; }

struct seg {
  pt p, q;
  bool inter(const seg& s) const {
    if (p == s.p || p == s.q || q == s.p || q == s.q) return false;
    return (((q - p) % (s.q - p) < 0) != ((q - p) % (s.p - p) < 0)) &&
           (((s.q - s.p) % (q - s.p) < 0) != ((s.q - s.p) % (p - s.p) < 0));
  }
  bool vert() const { return p.x == q.x; }
  bool is_above(const pt& o) const { return (q - p) % (o - p) >= 0; }
  void order() {
    if (q < p) swap(p, q);
  }
  // These only work properly after order() has been called on both segs.
  bool operator==(const seg& o) const { return p == o.p && q == o.q; }
  bool operator<(const seg& o) const { return p == o.p ? q < o.q : p < o.p; }
};

seg Seg(ll x0, ll y0, ll x1, ll y1) { return seg{pt{x0, y0}, pt{x1, y1}}; }

void TestSeg() {
  AssertFalse(Seg(0, 0, 1, 0).vert());
  AssertTrue(Seg(0, 0, 0, 1).vert());

  // Do not get intersections at endpoints.
  AssertFalse(Seg(0, 0, 1, 0).inter(Seg(0, 0, 0, 1)));
  AssertFalse(Seg(0, 0, 0, 1).inter(Seg(0, 0, 1, 0)));
  AssertFalse(Seg(0, 0, 0, 1).inter(Seg(0, 0, 1, 1)));
  AssertFalse(Seg(0, 0, 1, 1).inter(Seg(0, 0, -1, -1)));

  AssertFalse(Seg(0, 0, 2, 2).inter(Seg(0, 1, 0, 2000)));
  AssertFalse(Seg(0, 0, 1, 2000).inter(Seg(0, 1, 0, 2000)));

  AssertTrue(Seg(0, 0, 2, 2).inter(Seg(0, 1, 2, 1)));
  AssertTrue(Seg(1, 0, 1, 2).inter(Seg(2, 2, 0, 0)));

  AssertTrue(Seg(344941, 697734, 389381, 763823)
                 .inter(Seg(361587, 737781, 415221, 771629)));
  AssertTrue(Seg(361587, 737781, 415221, 771629)
                 .inter(Seg(344941, 697734, 389381, 763823)));

  AssertTrue(Seg(0, 0, 2, 0).is_above(pt{1, 1}));
  AssertFalse(Seg(0, 0, 2, 0).is_above(pt{1, -1}));
  AssertTrue(Seg(0, 0, 2, 2).is_above(pt{1, 2}));
  AssertFalse(Seg(0, 0, 2, 2).is_above(pt{1, 0}));
}

ostream& operator<<(ostream& o, const seg& s) {
  return o << "[" << s.p << ";" << s.q << "]";
}

struct ppoles {
  int i, j;
  bool operator==(const ppoles& o) const { return i == o.i && j == o.j; }
};

ostream& operator<<(ostream& o, const ppoles& p) {
  return o << p.i << " " << p.j;
}

typedef pair<vector<pt>, vector<ppoles>> CaseInput;
typedef vector<ppoles> CaseOutput;

CaseInput ParseCaseInput(istream& in) {
  int n;
  in >> n;
  vector<pt> pts(n);
  for (int i = 0; i < n; i++) in >> pts[i].x >> pts[i].y;
  vector<ppoles> fences(2);
  for (int i = 0; i < 2; i++) in >> fences[i].i >> fences[i].j;
  return {pts, fences};
}

CaseInput ParseCaseInput(const string& s) {
  istringstream in(s);
  return ParseCaseInput(in);
}

void TestParseCaseInput() {
  istringstream in(R"(4
1 2
2 3
-3 0
2 1
1 2
3 4
END)");
  AssertEqual(ParseCaseInput(in),
              make_pair(vector<pt>{pt{1, 2}, pt{2, 3}, pt{-3, 0}, pt{2, 1}},
                        vector<ppoles>{ppoles{1, 2}, ppoles{3, 4}}));
  string s;
  in >> s;
  AssertEqual(s, "END");
}

vector<string> GetNextNonEmptyLineTokens(istream& in) {
  string line;
  vector<string> tokens;
  while (getline(in, line)) {
    tokens = Tokenize(line);
    if (!tokens.empty()) return tokens;
  }
  return {};
}

CaseOutput ParseCaseOutput(istream& in, int case_idx) {
  vector<string> tokens;
  tokens = GetNextNonEmptyLineTokens(in);
  if (tokens.size() != 3) Error("Wrong number of tokens in case output");
  if (Lowercase(tokens[0]) != "case")
    Error("Case output not starting with Case");
  if (tokens[1] != ("#" + to_string(case_idx) + ":"))
    Error("Case number not formatted correctly or not correct number");
  long long num_fences = ParseInt(tokens[2]);
  vector<ppoles> r(num_fences);
  for (int i = 0; i < num_fences; i++) {
    tokens = GetNextNonEmptyLineTokens(in);
    if (tokens.size() != 2) Error("Wrong number of tokens in case output");
    r[i].i = ParseInt(tokens[0]);
    r[i].j = ParseInt(tokens[1]);
    if (r[i].i == r[i].j) Error("Both endpoints of a fence are the same");
  }
  return r;
}

CaseOutput ParseCaseOutput(string input, int case_idx) {
  stringstream ss(input);
  return ParseCaseOutput(ss, case_idx);
}

CaseOutput ParseCaseOutput(const vector<vector<string>>& lines) {
  if (lines.size() <= 1) Error("Wrong number of lines in case output");
  if (lines[0].size() != 1) Error("Wrong number of tokens in case output");
  int n = ParseInt(lines[0][0]);
  if (lines.size() != n + 1) Error("Number of lines doesn't match output");
  vector<ppoles> r(n);
  for (int i = 0; i < n; ++i) {
    if (lines[i + 1].size() != 2)
      Error("Wrong number of tokens in case output");
    r[i].i = ParseInt(lines[i + 1][0]);
    r[i].j = ParseInt(lines[i + 1][1]);
    if (r[i].i == r[i].j) Error("Both endpoints of a fence are the same");
  }
  return r;
}

void TestParseCaseOutput() {
  AssertError(ParseCaseOutput("", 1), "Wrong number of tokens in case output");
  AssertError(ParseCaseOutput("1", 1), "Wrong number of tokens in case output");
  AssertError(ParseCaseOutput("1\n2\n", 1),
              "Wrong number of tokens in case output");
  AssertError(ParseCaseOutput("abcd #1: 5", 1),
              "Case output not starting with Case");
  AssertError(ParseCaseOutput("Case #2: 5", 1),
              "Case number not formatted correctly or not correct number");
  AssertError(ParseCaseOutput("Case #4: 5", 42),
              "Case number not formatted correctly or not correct number");
  AssertError(ParseCaseOutput("Case #1 5", 1),
              "Case number not formatted correctly or not correct number");
  AssertError(ParseCaseOutput("Case #1: 1\n2 a\n", 1),
              "Not an integer in range: a");
  AssertError(ParseCaseOutput("Case #1: 1\n2 2\n", 1),
              "Both endpoints of a fence are the same");
  AssertError(ParseCaseOutput("Case #1: 2\n2 2\n3\n", 1),
              "Both endpoints of a fence are the same");
  AssertEqual(ParseCaseOutput("Case #1: 3\n2 3\n3 2\n1 4\n", 1),
              (vector<ppoles>{ppoles{2, 3}, ppoles{3, 2}, ppoles{1, 4}}));
  AssertEqual(ParseCaseOutput("Case #42: 3\n2 3\n3 2\n1 4\n", 42),
              (vector<ppoles>{ppoles{2, 3}, ppoles{3, 2}, ppoles{1, 4}}));
}

vector<seg> GetFences(const CaseInput& input, const CaseOutput& attempt) {
  vector<seg> fences;  // Insert input fences first.
  fences.reserve(input.second.size() + attempt.size());
  int npts = input.first.size();
  for (const ppoles& p : input.second)
    fences.push_back(seg{input.first[p.i - 1], input.first[p.j - 1]});
  for (const ppoles& p : attempt) {
    if (p.i < 1 || p.i > npts || p.j < 1 || p.j > npts)
      Error("Fence endpoint out of range");
    fences.push_back(seg{input.first[p.i - 1], input.first[p.j - 1]});
  }
  for (seg& f : fences) f.order();
  if (set<seg>(fences.begin(), fences.end()).size() != fences.size())
    Error("Repeated fence");
  return fences;
}

void TestGetFences() {
  auto input1 = ParseCaseInput(R"(4
  0 0
  0 1
  1 0
  1 1
  1 2
  3 4
  )");
  auto input2 = ParseCaseInput(R"(5
  0 0
  0 1
  2 3
  1 0
  1 1
  1 2
  3 5
  )");

  AssertError(GetFences(input1, vector<ppoles>{ppoles{1, 3}, ppoles{0, 1}}),
              "Fence endpoint out of range");
  AssertError(GetFences(input1, vector<ppoles>{ppoles{1, 3}, ppoles{5, 1}}),
              "Fence endpoint out of range");
  AssertError(GetFences(input1, vector<ppoles>{ppoles{1, 3}, ppoles{1, 0}}),
              "Fence endpoint out of range");
  AssertError(GetFences(input1, vector<ppoles>{ppoles{1, 3}, ppoles{1, 5}}),
              "Fence endpoint out of range");
  AssertError(GetFences(input1, vector<ppoles>{ppoles{1, 3}, ppoles{1, 3}}),
              "Repeated fence");
  AssertError(GetFences(input1, vector<ppoles>{ppoles{1, 3}, ppoles{3, 1}}),
              "Repeated fence");
  AssertError(GetFences(input1, vector<ppoles>{ppoles{1, 3}, ppoles{4, 3}}),
              "Repeated fence");
  AssertEqual(GetFences(input2, vector<ppoles>{ppoles{1, 3}, ppoles{4, 3}}),
              (vector<seg>{seg{pt{0, 0}, pt{0, 1}}, seg{pt{1, 1}, pt{2, 3}},
                           seg{pt{0, 0}, pt{2, 3}}, seg{pt{1, 0}, pt{2, 3}}}));
  AssertEqual(GetFences(input1, vector<ppoles>{ppoles{3, 1}}),
              (vector<seg>{seg{pt{0, 0}, pt{0, 1}}, seg{pt{1, 0}, pt{1, 1}},
                           seg{pt{0, 0}, pt{1, 0}}}));
}

set<pair<int, int>> FindAllIntersectionsSlow(const vector<seg>& segs) {
  set<pair<int, int>> r;
  for (int i = 0; i < segs.size(); ++i)
    for (int j = 0; j < i; j++) {
      bool i1 = segs[i].inter(segs[j]);
      bool i2 = segs[j].inter(segs[i]);
      assert(i1 == i2);
      if (i1) r.insert(make_pair(j, i));
    }
  return r;
}

constexpr pair<int, int> noInter(-1, -1);

pair<int, int> FindIntersection(vector<seg>& segs) {
  // +x + segs.size() means add segment x-1.
  // +x means check vertical segment x-1.
  // -x means remove it.
  map<int, vector<int>> actions;
  for (int i = 0; i < segs.size(); i++) {
    seg& s = segs[i];
    s.order();
    if (s.vert()) {
      // cerr << "Add check " << i << " " << segs[i] << endl;
      actions[s.p.x].push_back(i + 1);
    } else {
      // cerr << "Add insert and delete " << i << " " << segs[i] << endl;
      actions[s.p.x].push_back(i + 1 + segs.size());
      actions[s.q.x].push_back(-i - 1);
    }
  }
  // Checks if segs[i] is below segs[j] at the smallest x at which they both
  // exist and are not at equal Y. This assumes their projections onto
  // the X axis overlap (the way it's used, non-overlapping segments are
  // never compared).
  auto CompareSegs = [&](int i, int j) -> bool {
    if (segs[i].p == segs[j].p) {
      if (segs[i].q.x > segs[j].q.x) return segs[i].is_above(segs[j].q);
      return !segs[j].is_above(segs[i].q);
    }
    if (segs[i].p.x < segs[j].p.x) return segs[i].is_above(segs[j].p);
    return !segs[j].is_above(segs[i].p);
  };
  set<int, decltype(CompareSegs)> ys(CompareSegs);
  for (auto& [act_x, acts] : actions) {
    // cerr << "Act_x " << act_x << endl;
    // Process removals first, then vertical checks, then insertions,
    // to avoid comparing segments that don't really overlap on X.
    sort(acts.begin(), acts.end());
    for (int a : acts) {
      if (a < 0) {
        int id = -a - 1;
        // Remove it and check the new neighbors.
        // cerr << "Remove " << segs[id] << endl;
        auto it = ys.find(id);
        auto nit = next(it);
        if (it != ys.begin() && nit != ys.end() &&
            segs[*prev(it)].inter(segs[*nit]))
          return {*prev(it), *nit};
        ys.erase(it);
      } else if (a > segs.size()) {
        int id = a - segs.size() - 1;
        // Insert it and check it against its neighbors.
        // cerr << "Insert " << segs[id] << endl;
        auto it = ys.lower_bound(id);
        if (it != ys.end() && segs[*it].inter(segs[id])) return {*it, id};
        if (it != ys.begin() && segs[*prev(it)].inter(segs[id]))
          return {*prev(it), id};
        ys.insert(id);
      } else {
        int id = a - 1;
        // Simply check it.
        // cerr << "Check " << segs[id] << endl;
        // Create a fake segment to represent the two endpoints of the segment
        // we are checking. To simulate "insert point P" we insert a horizontal
        // segment that has P as its left endpoint. That segment is sorted
        // as P would with other segments, because the leftmost point is
        // used for the comparison and because there are no collinear triples,
        // there aren't any endpoints from other segments at the current x.
        segs.push_back(seg{segs[id].p, pt{segs[id].p.x + 1, segs[id].p.y}});
        auto it = ys.lower_bound(segs.size() - 1);
        segs.back() = seg{segs[id].q, pt{segs[id].q.x + 1, segs[id].q.y}};
        auto it2 = ys.lower_bound(segs.size() - 1);
        if (it != it2) return {*it, id};
        segs.pop_back();
      }
    }
  }
  return noInter;
}

pair<int, int> FindIntersectionConst(const vector<seg>& osegs) {
  vector<seg> segs(osegs);
  return FindIntersection(segs);
}

bool HasCollinears(const vector<pt>& pts) {
  for (int i = 0; i < pts.size(); i++)
    for (int j = 0; j < i; j++)
      for (int k = 0; k < j; k++) {
        if (((pts[i] - pts[k]) % (pts[j] - pts[k])) == 0) return true;
      }
  return false;
}

void TestFindIntersection() {
  auto CheckOnInput = [](const vector<seg>& segs) {
    auto ps = FindAllIntersectionsSlow(segs);
    auto p = FindIntersectionConst(segs);
    if (p.first > p.second) swap(p.first, p.second);
    if (ps.count(p)) return true;
    if (ps.empty() && p == noInter) return true;
    if (p != noInter) {
      cerr << "Found false intersection between " << p.first << "("
           << segs[p.first] << ") and " << p.second << "(" << segs[p.second]
           << ")";
    } else {
      cerr << "Missed these intersections: "
           << vector<pair<int, int>>(ps.begin(), ps.end());
    }
    cerr << " in " << segs << endl;
    cerr << "assert(CheckOnInput({";
    for (const seg& s : segs) {
      if (!(s == segs.front())) cerr << ", ";
      cerr << "Seg(" << s.p.x << ", " << s.p.y << ", " << s.q.x << ", " << s.q.y
           << ")";
    }
    cerr << "}));" << endl;
    return false;
  };
  // These failed the stress test before a bugfix.
  assert(CheckOnInput({Seg(535963, 9818235, 422454, 9929490),
                       Seg(422454, 9929490, 13951, 3028792),
                       Seg(422454, 9929490, 353932, 8239751)}));
  assert(CheckOnInput({Seg(411375, 7237807, 504031, 7256896),
                       Seg(532991, 4259044, 537356, 4324965),
                       Seg(538880, 9070001, 587861, 9074304),
                       Seg(971948, 1289028, 993842, 1326447),
                       Seg(169318, 1314701, 236006, 1388343),
                       Seg(57928, 3458823, 58921, 3502442),
                       Seg(79517, 8543567, 144049, 8545664),
                       Seg(10135, 7124072, 31645, 7186949),
                       Seg(361879, 2398318, 373102, 2428837),
                       Seg(173715, 1296440, 186310, 1328380),
                       Seg(366442, 3936243, 404832, 4014171),
                       Seg(741624, 1215348, 768918, 1291984),
                       Seg(46401, 7850279, 67082, 7944261),
                       Seg(309102, 7937601, 314074, 7959276),
                       Seg(481169, 9623772, 572473, 9693276),
                       Seg(264196, 5748733, 306624, 5777900),
                       Seg(663404, 9959686, 716875, 10013337),
                       Seg(256126, 2385591, 278694, 2451657),
                       Seg(838186, 1460347, 917996, 1537658),
                       Seg(192047, 653947, 230495, 677403),
                       Seg(20578, 2017439, 66611, 2076568),
                       Seg(471392, 7397156, 540305, 7448161),
                       Seg(20929, 6036861, 106054, 6113431),
                       Seg(301947, 5905737, 367298, 5933290),
                       Seg(865423, 497556, 903324, 532730),
                       Seg(399499, 5901240, 437185, 5961710),
                       Seg(361587, 737781, 415221, 771629),
                       Seg(908080, 3857305, 936739, 3865739),
                       Seg(391096, 6683916, 469936, 6758608),
                       Seg(81072, 525697, 83073, 573451),
                       Seg(78910, 840676, 159767, 844155),
                       Seg(746413, 4847384, 774601, 4909944),
                       Seg(344941, 697734, 389381, 763823)}));
  assert(CheckOnInput({Seg(0, 0, 0, 1), Seg(0, 0, 1, 0), Seg(1, 0, 1, 1),
                       Seg(0, 1, 1, 1), Seg(0, 0, 1, 1)}));
  assert(CheckOnInput({Seg(0, 0, 0, 1), Seg(0, 0, 1, 0), Seg(1, 0, 1, 1),
                       Seg(0, 1, 1, 0), Seg(0, 0, 1, 1)}));

  // Stress test.
  for (int tt = 0; tt < 100; ++tt) {
    srand(tt + 1000);
    vector<seg> segs;
    while (FindAllIntersectionsSlow(segs).empty()) {
      pt p{rand() % 1000000, rand() % 10000000};
      segs.push_back(
          Seg(p.x, p.y, p.x + rand() % 100000, p.y + rand() % 100000));
      vector<pt> pts;
      for (const seg& s : segs) pts.push_back(s.p), pts.push_back(s.q);
      assert(!HasCollinears(pts));  // Super slow.
      CheckOnInput(segs);
    }
  }

  // Stress test 2.
  for (int tt = 0; tt < 100; ++tt) {
    srand(tt + 1000);
    vector<pt> pts;
    while (pts.size() < max(10, tt / 2) && !HasCollinears(pts))
      pts.push_back({rand() % 1000000, rand() % 10000000});
    vector<seg> allsegs;
    for (int i = 0; i < pts.size(); ++i)
      for (int j = 0; j < i; j++) {
        allsegs.push_back({pts[i], pts[j]});
      }
    random_shuffle(allsegs.begin(), allsegs.end());
    vector<seg> segs;
    while (!allsegs.empty()) {
      segs.push_back(allsegs.back());
      allsegs.pop_back();
      CheckOnInput(segs);
      if (!FindAllIntersectionsSlow(segs).empty()) segs.pop_back();
    }
  }

  // Stress test with verticals.
  for (int tt = 0; tt < 100; ++tt) {
    srand(tt + 1000);
    vector<seg> segs;
    constexpr ll maxc = 100000000;
    for (ll x = 0; x <= maxc; x += maxc / 100) {
      segs.push_back(Seg(x, rand() % maxc, x, rand() % maxc));
    }
    while (FindAllIntersectionsSlow(segs).empty()) {
      pt p{rand() % maxc, rand() % maxc};
      segs.push_back(Seg(p.x, p.y, p.x + rand() % (maxc / 100),
                         p.y + rand() % (maxc / 100)));
      vector<pt> pts;
      for (const seg& s : segs) pts.push_back(s.p), pts.push_back(s.q);
      if (HasCollinears(pts)) {  // Super slow.
        cerr << tt << " " << segs.size() << endl;
        segs.pop_back();
        continue;
      };
      CheckOnInput(segs);
    }
  }
}

vector<pt> ConvexHull(const vector<pt>& pts) {
  vector<pt> res(pts);
  if (res.size() < 3) return res;
  swap(res.front(), *min_element(res.begin(), res.end()));
  const pt& r = res.front();
  sort(res.begin() + 1, res.end(), [&r](const pt& p, const pt& q) {
    return seg{r, p}.is_above(q);
  });
  vector<pt> ch;
  ch.push_back(res[0]);
  ch.push_back(res[1]);
  for (int i = 2; i < res.size(); ++i) {
    while (ch.size() > 1 &&
           !seg{ch[ch.size() - 2], ch[ch.size() - 1]}.is_above(res[i]))
      ch.pop_back();
    ch.push_back(res[i]);
  }
  return ch;
}

void TestConvexHull() {
  auto Check = [](const vector<pt>& exp_out, const vector<pt>& in) {
    srand(100);
    vector<pt> r(in);
    for (int i = 0; i < 10; ++i) {
      if (exp_out != ConvexHull(r)) {
        cerr << "ConvexHull( " << r << ") = " << ConvexHull(r) << " instead of "
             << exp_out << endl;
        return false;
      }
      random_shuffle(r.begin(), r.end());
    }
    return true;
  };
  srand(1020);
  vector<pt> tri = {{0, 10}, {10, 0}, {10, 10}};
  AssertTrue(Check(tri, tri));
  AssertTrue(
      Check(tri, {{0, 10}, {10, 0}, {10, 10}, {6, 6}, {2, 9}, {9, 2}, {9, 8}}));
  vector<pt> quad = {{0, 0}, {10, 0}, {10, 10}, {0, 10}};
  AssertTrue(Check(quad, quad));
  AssertTrue(Check(quad, {{0, 10},
                          {10, 0},
                          {10, 10},
                          {6, 7},
                          {2, 9},
                          {9, 2},
                          {9, 9},
                          {0, 0},
                          {1, 2},
                          {3, 2}}));
}

string JudgeCase(const CaseInput& input, const CaseOutput& attempt) {
  int ch_size = ConvexHull(input.first).size();
  // Convex Hull triangulated has 2 * ch_size - 3 segments. Each additional
  // point p adds 3 segments of the form (p, q) where q is each vertex of
  // the triangle that contains p.
  int correct_total_size = 2 * ch_size - 3 + 3 * (input.first.size() - ch_size);

  if (correct_total_size - 2 > attempt.size())
    return "Number of fences could be larger";

  vector<seg> fences = GetFences(input, attempt);
  auto p = FindIntersection(fences);
  if (p != noInter) {
    if (p.first > p.second) swap(p.first, p.second);
    auto FenceNum = [](int i) {
      ostringstream out;
      if (i < 2) {
        out << "input" << (i + 1);
      } else {
        out << "output" << (i - 1);
      }
      return out.str();
    };
    ostringstream out;
    out << "Fences " << FenceNum(p.first) << " and " << FenceNum(p.second)
        << " intersect";
    return out.str();
  }
  return "";
}

void TestJudgeCase() {
  auto input3 = ParseCaseInput(R"(5
  0 0
  0 1
  2 3
  1 0
  1 1
  1 2
  2 5
  )");
  AssertEqual(
      JudgeCase(input3,
                vector<ppoles>{{2, 3}, {5, 3}, {3, 4}, {1, 5}, {4, 5}, {1, 4}}),
      "");
  AssertEqual(
      JudgeCase(input3, vector<ppoles>{{2, 3}, {5, 3}, {3, 4}, {1, 5}, {4, 5}}),
      "Number of fences could be larger");
  AssertEqual(
      JudgeCase(input3,
                vector<ppoles>{{2, 3}, {5, 3}, {3, 4}, {1, 5}, {4, 5}, {1, 3}}),
      "Fences input2 and output6 intersect");
  AssertEqual(
      JudgeCase(input3,
                vector<ppoles>{{2, 3}, {5, 3}, {3, 4}, {1, 5}, {4, 5}, {2, 4}}),
      "Fences output4 and output6 intersect");
  AssertError(
      JudgeCase(input3,
                vector<ppoles>{{2, 3}, {5, 3}, {3, 4}, {1, 5}, {4, 5}, {1, 2}}),
      "Repeated fence");
  AssertError(
      JudgeCase(input3,
                vector<ppoles>{{2, 3}, {5, 3}, {3, 4}, {1, 5}, {4, 5}, {5, 2}}),
      "Repeated fence");
  AssertError(
      JudgeCase(input3,
                vector<ppoles>{{2, 3}, {5, 3}, {3, 4}, {1, 5}, {4, 5}, {3, 2}}),
      "Repeated fence");
  AssertError(
      JudgeCase(input3,
                vector<ppoles>{{2, 3}, {5, 3}, {3, 4}, {1, 5}, {4, 5}, {3, 0}}),
      "Fence endpoint out of range");
}

void Test() {
  TestParseCaseInput();
  TestParseCaseOutput();
  TestSeg();
  TestGetFences();
  TestFindIntersection();
  TestConvexHull();
  TestJudgeCase();
}

int main(int argc, const char* argv[]) {
  if (argc == 2 && string(argv[1]) == "-2") {
    TestLib();
    Test();
    cerr << "All tests passed!" << endl;
    return 0;
  }
  if (argc != 4) return 1;
  ifstream input_stream(argv[1]);
  ifstream output_stream(argv[2]);
  int num_cases;
  input_stream >> num_cases;
  string e;
  for (int case_idx = 1; case_idx <= num_cases; case_idx++) {
    auto input = ParseCaseInput(input_stream);
    auto attempt = ParseCaseOutput(output_stream, case_idx);
    e = JudgeCase(input, attempt);
    if (e.empty()) continue;
    ostringstream out;
    out << "Case #" << case_idx << ": " << e;
    e = out.str();
    break;
  }
  if (!e.empty()) Error(e);
  string token;
  if (output_stream >> token) Error("Additional output found");
  return 0;
}
