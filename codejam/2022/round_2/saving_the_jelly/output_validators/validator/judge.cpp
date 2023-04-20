#include <bits/stdc++.h>
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

using vp = vector<pair<long long, long long>>;
typedef pair<vp, vp> CaseInput;
typedef pair<string, vp> CaseOutput;

long long dist2(pair<long long, long long> a, pair<long long, long long> b) {
  long long dx = a.first - b.first;
  long long dy = a.second - b.second;
  return dx * dx + dy * dy;
}

string checkIsCorrect(const vp& permutation, const vp& children,
                      const vp& sweets) {
  vector<bool> taken(sweets.size(), false);
  vector<bool> assigned(children.size(), false);
  int n = children.size();
  for (auto [a, b] : permutation) {
    ostringstream out;
    // Check the a (child) is valid.
    if (a < 1 || a > n) {
      out << "child number " << a << " is not in range [1, " << n << "].";
      return out.str();
    }
    // Check that the chosen child has not been used.
    if (assigned[a - 1]) {
      out << "child number " << a << " appears multiple times.";
      return out.str();
    }
    // Make sure the forbidden sweet is not given out.
    if (b == 1) {
      out << "child number " << a << " is getting forbidden sweet #1";
      return out.str();
    }
    // Check that the sweet number is valid.
    if (b < 2 || b > n + 1) {
      out << "sweet number " << b << " is not in range [2, " << n + 1 << "]";
      return out.str();
    }
    // Make sure that the sweet has not already been eaten.
    if (taken[b - 1]) {
      out << "sweet number " << b << " has already been eaten.";
      return out.str();
    }
    // Mark the child and sweet as used.
    assigned[a - 1] = true;
    taken[b - 1] = true;
    // Check that the distance from the child to this sweet is <= all other
    // available sweets.
    auto d0 = dist2(children[a - 1], sweets[b - 1]);
    for (int i = 1; i <= n + 1; i++) {
      long long d1 = dist2(children[a - 1], sweets[i - 1]);
      if (!taken[i - 1] && d1 < d0) {
        out << "child " << a << " can't be assigned sweet " << b
            << " which is at a distance^2 = " << d0 << " because sweet " << i
            << " is still free and is at a smaller distance from them = " << d1;
        return out.str();
      }
    }
  }
  return "";
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

CaseInput ParseCaseInput(istream& in) {
  int n;
  in >> n;
  vp children(n), sweets(n + 1);
  for (auto& [x, y] : children) in >> x >> y;
  for (auto& [x, y] : sweets) in >> x >> y;
  return CaseInput(children, sweets);
}

CaseInput ParseCaseInput(const string& s) {
  istringstream in(s);
  return ParseCaseInput(in);
}

CaseOutput ParseCaseOutput(const CaseInput& input, istream& in, int case_idx) {
  vector<string> tokens;
  // Read "Case #X: POSSIBLE|IMPOSSIBLE"
  tokens = GetNextNonEmptyLineTokens(in);
  if (tokens.size() != 3) Error("Wrong number of tokens in case output");
  if (Lowercase(tokens[0]) != "case")
    Error("Case output not starting with Case");
  if (tokens[1] != ("#" + to_string(case_idx) + ":"))
    Error("Case number not formatted correctly or not correct number");

  string possibility = tokens[2];
  possibility = Lowercase(possibility);
  vp permutation;
  // If possible, read the permutation (n pairs of ints).
  if (possibility == "possible") {
    permutation.resize(input.first.size());
    for (auto& [a, b] : permutation) {
      tokens = GetNextNonEmptyLineTokens(in);
      if (tokens.size() != 2)
        Error("Wrong number of tokens in permutation line");
      a = ParseInt(tokens[0]);
      b = ParseInt(tokens[1]);
    }
  }
  return CaseOutput(possibility, permutation);
}

CaseOutput ParseCaseOutput(const CaseInput& input, string output,
                           int case_idx) {
  stringstream ss(output);
  return ParseCaseOutput(input, ss, case_idx);
}

string JudgeCase(const CaseInput& input, const CaseOutput& judge,
                 const CaseOutput& attempt) {
  // Check that the judge's output is valid.
  string judge_error = checkIsCorrect(judge.second, input.first, input.second);
  // If the judger's output is invalid, throw a judge error.
  if (!judge_error.empty()) JudgeError(judge_error);
  // Check that the contestant's output is valid.
  string contestant_error =
      checkIsCorrect(attempt.second, input.first, input.second);
  // If the contestant's output is invalid, return that error.
  if (!contestant_error.empty()) return contestant_error;
  // If both the contestant and judge said the same for possible/impossible
  // return correct (empty string).
  if (judge.first == attempt.first) return "";
  // If the contestant found an answer but the judge didn't, throw a judge
  // error.
  if (attempt.first == "possible")
    JudgeError("Contestant found answer judge did not find!");
  return "Contestant did not find an answer but the judge did";
}

void TestParseCaseInput() {
  istringstream in(R"(2
-1 0
1 0
10 0
0 -1
0 1
END)");
  AssertEqual(ParseCaseInput(in),
              make_pair(vp{{-1, 0}, {1, 0}}, vp{{10, 0}, {0, -1}, {0, 1}}));
  string s;
  in >> s;
  AssertEqual(s, "END");
}

void TestParseCaseOutput() {
  auto case_1 = CaseInput(vp{{0, 0}}, vp{{1, 1}, {2, 2}});
  auto case_2 = CaseInput(vp{{-1, 0}, {1, 0}}, vp{{10, 0}, {0, -1}, {0, 1}});
  // Reading header + possibility
  AssertError(ParseCaseOutput(case_1, "", 1),
              "Wrong number of tokens in case output");
  AssertError(ParseCaseOutput(case_1, "1", 1),
              "Wrong number of tokens in case output");
  AssertError(ParseCaseOutput(case_1, "1\n2\n", 1),
              "Wrong number of tokens in case output");
  AssertError(ParseCaseOutput(case_1, "abcd #1: IMPOSSIBLE", 1),
              "Case output not starting with Case");
  AssertError(ParseCaseOutput(case_1, "Case #2: IMPOSSIBLE", 1),
              "Case number not formatted correctly or not correct number");
  AssertError(ParseCaseOutput(case_1, "Case #4: IMPOSSIBLE", 42),
              "Case number not formatted correctly or not correct number");
  AssertError(ParseCaseOutput(case_1, "Case #1 IMPOSSIBLE", 1),
              "Case number not formatted correctly or not correct number");

  // Possible cases, reading permutation
  AssertError(ParseCaseOutput(case_1, "Case #7: POSSIBLE\n1\n", 7),
              "Wrong number of tokens in permutation line");
  AssertError(ParseCaseOutput(case_2, "Case #7: POSSIBLE\n1 2\n2\n", 7),
              "Wrong number of tokens in permutation line");
  AssertError(ParseCaseOutput(case_2, "Case #7: POSSIBLE\n1 a\n2 3\n", 7),
              "Not an integer in range: a");
  AssertError(ParseCaseOutput(case_2, "Case #7: POSSIBLE\na 2\n2 3\n", 7),
              "Not an integer in range: a");

  // Valid outputs
  AssertEqual(ParseCaseOutput(case_1, "Case   #8:    iMpossIBLE   ", 8),
              CaseOutput("impossible", vp{}));
  AssertEqual(ParseCaseOutput(
                  case_1, "Case   #8:    poSSiblE   \n  1   2\n2\t3\r\n", 8),
              CaseOutput("possible", vp{{1, 2}}));
  AssertEqual(ParseCaseOutput(
                  case_2, "Case   #8:    poSSiblE   \n  1   2\n2\t3\r\n", 8),
              CaseOutput("possible", vp{{1, 2}, {2, 3}}));
}

void TestJudgeCase() {
  // Impossible case.
  auto case_1 = CaseInput(vp{{0, 0}}, vp{{1, 1}, {2, 2}});
  auto case_1_ac = CaseOutput("impossible", vp{});
  auto case_1_wa = CaseOutput("possible", vp{{1, 2}, {2, 3}});

  // Possible case.
  auto case_2 = CaseInput(vp{{-1, 0}, {1, 0}}, vp{{10, 0}, {0, -1}, {0, 1}});
  auto case_2_ac = CaseOutput("possible", vp{{2, 2}, {1, 3}});
  auto case_2_wa = CaseOutput("impossible", vp{});

  // Judge's output is invalid.
  AssertError(JudgeCase(case_1, case_1_wa, case_1_ac),
              "JUDGE_ERROR! child 1 can't be assigned sweet 2 which is at a "
              "distance^2 = 8 because sweet 1 is still free and is at a "
              "smaller distance from them = 2");
  // Contestant's output is invalid.
  AssertEqual(JudgeCase(case_1, case_1_ac, case_1_wa),
              "child 1 can't be assigned sweet 2 which is at a "
              "distance^2 = 8 because sweet 1 is still free and is at a "
              "smaller distance from them = 2");
  // Both contestant and judge say IMPOSSIBLE.
  AssertEqual(JudgeCase(case_1, case_1_ac, case_1_ac), "");

  // Judge says IMPOSSIBLE but contestant finds an answer.
  AssertError(JudgeCase(case_2, case_2_wa, case_2_ac),
              "JUDGE_ERROR! Contestant found answer judge did not find!");
  // Judge finds an answer but contestant says impossible.
  AssertEqual(JudgeCase(case_2, case_2_ac, case_2_wa),
              "Contestant did not find an answer but the judge did");
  // Both judge and contestant find an answer.
  AssertEqual(JudgeCase(case_2, case_2_ac, case_2_ac), "");
}

void Test() {
  TestParseCaseInput();
  TestParseCaseOutput();
  TestJudgeCase();
}

int main(int argc, char **argv) {
  if (argc == 2 && string(argv[1]) == "-2") {
    TestLib();
    Test();
    cerr << "All tests passed!" << endl;
    return 0;
  }
  if (argc != 4) return 1;
  ifstream input_stream(argv[1]);
  ifstream output_stream(argv[2]);
  ifstream judge_output_stream(argv[3]);
  int num_cases;
  input_stream >> num_cases;
  string e;
  for (int case_idx = 1; case_idx <= num_cases; case_idx++) {
    auto input = ParseCaseInput(input_stream);
    auto attempt = ParseCaseOutput(input, output_stream, case_idx);
    auto judge = ParseCaseOutput(input, judge_output_stream, case_idx);
    e = JudgeCase(input, judge, attempt);
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
