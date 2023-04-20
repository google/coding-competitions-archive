#include <bits/stdc++.h>
using namespace std;

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

#define AssertError(call, err) \
  mocked_error = true;         \
  try {                        \
    call;                      \
  } catch (...) {              \
  }                            \
  assert(last_error == err);   \
  last_error = "";             \
  mocked_error = false;

string Strint128(__int128_t n) {
  if (n < 0) {
    return "-" + Strint128(-n);
  }
  string s;
  do {
    s += (char)('0' + n % 10);
    n /= 10;
  } while (n > 0);
  reverse(s.begin(), s.end());
  return s;
}

void TestStrint128() {
  assert(Strint128(5) == "5");
  assert(Strint128(-21) == "-21");
  assert(Strint128(0) == "0");
  assert(Strint128((__int128_t)1 << 100) == "1267650600228229401496703205376");
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

// Parses ints in [-10^38, 10^38] or raises Error.
__int128_t ParseInt128(const string& ss) {
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
  if (s.empty() || s.size() > 40) Error(error);
  if (s.size() == 40 && s != string("-1") + string(38, '0')) Error(error);
  if (s.size() == 39 && s[0] != '-' && s != string("1") + string(38, '0'))
    Error(error);
  __int128_t r = 0;
  for (const char c : s.substr(s[0] == '-' ? 1 : 0)) {
    r = r * 10 + (c - '0');
  }
  if (s[0] == '-') {
    r = -r;
  }
  return r;
}

void TestParseInt128() {
  __int128_t value_1e38 = 1;
  for (int i = 0; i < 38; ++i) {
    value_1e38 *= 10;
  }
  assert(ParseInt128("0") == 0);
  assert(ParseInt128("0000") == 0);
  assert(ParseInt128("-0") == 0);
  assert(ParseInt128("-0000") == 0);
  assert(ParseInt128("-10") == -10);
  assert(ParseInt128("-010") == -10);
  assert(ParseInt128("010111") == 10111);
  assert(ParseInt128("00009") == 9);
  assert(ParseInt128(string("1") + string(38, '0')) == value_1e38);
  assert(ParseInt128(string("0001") + string(38, '0')) == value_1e38);
  assert(ParseInt128(string("-1") + string(38, '0')) == -value_1e38);
  assert(ParseInt128(string("-0001") + string(38, '0')) == -value_1e38);
  AssertError(ParseInt128(""), "Not an integer in range: ");
  AssertError(ParseInt128("a"), "Not an integer in range: a");
  AssertError(ParseInt128("1a1"), "Not an integer in range: 1a1");
  AssertError(
      ParseInt128(string("1") + string(37, '0') + "1"),
      "Not an integer in range: 100000000000000000000000000000000000001");
  AssertError(
      ParseInt128(string("-1") + string(37, '0') + "1"),
      "Not an integer in range: -100000000000000000000000000000000000001");
  AssertError(ParseInt128("0x10"), "Not an integer in range: 0x10");
  AssertError(ParseInt128("1.0"), "Not an integer in range: 1.0");
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
      if (ParseInt128(case_num) != cases.size() + 1) {
        Error(string("Found case: ") + Truncate(case_num) +
              ", expected: " + Strint128(cases.size() + 1));
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
string JudgeAllCases(const vector<T>& input, const vector<U>& correct_output,
                     const vector<U>& attempt,
                     string JudgeCase(const T&, const U&, const U&)) {
  if (attempt.size() != input.size())
    Error(string("Wrong number of cases in attempt: ") +
          Strint128(attempt.size()) + ", expected: " + Strint128(input.size()));
  for (int i = 0; i < input.size(); ++i) {
    string e = JudgeCase(input[i], correct_output[i], attempt[i]);
    if (e.empty()) continue;
    ostringstream out;
    out << "Case #" << (i + 1) << ": " << e;
    return out.str();
  }
  return "";
}

string JudgeCaseTest(const int& n, const int& m, const int& o) {
  if (n != o) return Strint128(o) + " not equal to input: " + Strint128(n);
  return "";
};

void TestJudgeAllCases() {
  AssertError(JudgeAllCases({1}, {1}, {1, 2}, JudgeCaseTest),
              "Wrong number of cases in attempt: 2, expected: 1");
  AssertError(JudgeAllCases({1, 2}, {1, 2}, {1}, JudgeCaseTest),
              "Wrong number of cases in attempt: 1, expected: 2");
  AssertError(JudgeAllCases({1, 2}, {1, 2}, {}, JudgeCaseTest),
              "Wrong number of cases in attempt: 0, expected: 2");
  assert(JudgeAllCases({1}, {1}, {1}, JudgeCaseTest) == "");
  assert(JudgeAllCases({1}, {1}, {2}, JudgeCaseTest) ==
         "Case #1: 2 not equal to input: 1");
  assert(JudgeAllCases({1, 1}, {1, 1}, {2, 2}, JudgeCaseTest) ==
         "Case #1: 2 not equal to input: 1");
  assert(JudgeAllCases({1, 2}, {1, 2}, {1, 2}, JudgeCaseTest) == "");
  assert(JudgeAllCases({1, 2}, {1, 2}, {1, 1}, JudgeCaseTest) ==
         "Case #2: 1 not equal to input: 2");
}

void TestLib() {
  TestStrint128();
  TestTruncate();
  TestParseInt128();
  TestLowercase();
  TestTokenize();
  TestSplitCases();
  TestJudgeAllCases();
}

//////////////////////////////////////////////

struct CaseInput {
  int N;
  int Q;
  vector<string> answers;
  vector<int> scores;
};

struct CaseOutput {
  string answer;
  string fraction;
};

CaseInput ParseCaseInput(istream& in) {
  int N, Q;
  in >> N >> Q;
  vector<string> answers;
  vector<int> scores;
  for (int i = 0; i < N; i++) {
    string answer;
    in >> answer;
    answers.push_back(answer);
    int score;
    in >> score;
    scores.push_back(score);
  }
  return {.N = N, .Q = Q, .answers = answers, .scores = scores};
}

// Solution copied from yhos.cc.
using Int = __int128_t;

CaseOutput Solve(const CaseInput& input) {
  constexpr int MAX_Q = 120;
  Int bn[MAX_Q + 1][MAX_Q + 1];

  int N, Q;
  char A[3][MAX_Q + 1];
  int S[3];

  for (int n = 0; n <= MAX_Q; ++n) {
    bn[n][0] = bn[n][n] = 1;
    for (int k = 1; k < n; ++k) {
      bn[n][k] = bn[n - 1][k - 1] + bn[n - 1][k];
    }
  }

  N = input.N;
  Q = input.Q;
  for (int i = 0; i < N; ++i) {
    strcpy(A[i], input.answers[i].c_str());
    S[i] = input.scores[i];
  }

  // Duplicate the student to assume that N = 3.
  for (int i = N; i < 3; ++i) {
    strcpy(A[i], A[0]);
    S[i] = S[0];
  }

  // Classify the questions into 4 types.
  vector<int> types(Q, 0);
  int qs[4] = {};
  for (int j = 0; j < Q; ++j) {
    if (A[0][j] != A[1][j]) types[j] |= 1;
    if (A[0][j] != A[2][j]) types[j] |= 2;
    ++qs[types[j]];
  }

  // total := the total count of patterns among 2^Q.
  // cnts[t] := the count of patterns with fixing the answer in A[0] for a
  // question of type t.
  Int total = 0, cnts[4] = {};
  // xs[t] := the number of correct answer in A[0] for questions of type t.
  int xs[4];
  for (xs[0] = 0; xs[0] <= qs[0]; ++xs[0]) {
    xs[1] = (S[0] + S[2] - qs[2] - qs[3]) / 2 - xs[0];
    xs[2] = (S[0] + S[1] - qs[1] - qs[3]) / 2 - xs[0];
    xs[3] = S[0] - xs[0] - xs[1] - xs[2];
    bool ok = true;
    for (int t = 0; t < 4; ++t) {
      ok = ok && (0 <= xs[t] && xs[t] <= qs[t]);
    }
    ok = ok && (S[0] == xs[0] + xs[1] + xs[2] + xs[3]);
    ok = ok && (S[1] == xs[0] + (qs[1] - xs[1]) + xs[2] + (qs[3] - xs[3]));
    ok = ok && (S[2] == xs[0] + xs[1] + (qs[2] - xs[2]) + (qs[3] - xs[3]));
    if (ok) {
      Int prod = 1;
      for (int t = 0; t < 4; ++t) {
        prod *= bn[qs[t]][xs[t]];
      }
      total += prod;
      for (int t = 0; t < 4; ++t) {
        if (qs[t] > 0) {
          cnts[t] += prod * xs[t] / qs[t];
        }
      }
    }
  }

  string ans(Q, '?');
  Int numer = 0;
  for (int j = 0; j < Q; ++j) {
    const int t = types[j];
    if (cnts[t] > total - cnts[t]) {
      ans[j] = A[0][j];
      numer += cnts[t];
    } else if (cnts[t] == total - cnts[t]) {
      // We use ? to represent that this question can be answered either T or F.
      ans[j] = '?';
      numer += cnts[t];
    } else {
      ans[j] = A[0][j] ^ 'F' ^ 'T';
      numer += total - cnts[t];
    }
  }
  Int denom = total;
  const Int g = __gcd(numer, denom);
  numer /= g;
  denom /= g;

  return {.answer = Lowercase(ans),
          .fraction = Strint128(numer) + "/" + Strint128(denom)};
}

const string kInvalidLengthError =
    "Solution length does not match the number of questions.";
const string kInvalidCharactersError =
    "Solution contains characters other than T and F.";
const string kIncorrectAnswerError =
    "Solution gives an answer for a question that is not optimal.";
const string kIncorrectFractionError =
    "Fraction of expected number of correct questions is not correct.";
const string kAccepted = "";

CaseOutput ParseCaseOutput(const vector<vector<string>>& lines) {
  if (lines.size() != 1) Error("Wrong number of lines in case output");
  if (lines[0].size() != 2) Error("Wrong number of tokens in case output");
  string answer = lines[0][0];
  string fraction = lines[0][1];
  return {.answer = answer, .fraction = fraction};
}

string JudgeCase(const CaseInput& input, const CaseOutput& _,
                 const CaseOutput& attempt) {
  // We use the judge output to get the answer string with ?'s for questions
  // that can be answered either T or F.
  CaseOutput judge_output = Solve(input);
  if (attempt.answer.size() != input.Q) {
    return kInvalidLengthError;
  }
  for (int i = 0; i < input.Q; i++) {
    if (attempt.answer[i] != 'f' && attempt.answer[i] != 't') {
      return kInvalidCharactersError;
    }
    if (judge_output.answer[i] == '?') continue;
    if (attempt.answer[i] != judge_output.answer[i]) {
      return kIncorrectAnswerError;
    }
  }

  if (attempt.fraction != judge_output.fraction) {
    return kIncorrectFractionError;
  }

  return kAccepted;
}

void Test() {
  {
    stringstream ss("3 4\nFTTF 1\nFFTT 2\nTTTT 3\n");
    auto input = ParseCaseInput(ss);
    assert(input.N == 3);
    assert(input.Q == 4);
    vector<string> expected_answers{"FTTF", "FFTT", "TTTT"};
    vector<int> expected_scores{1, 2, 3};
    assert(input.answers == expected_answers);
    assert(input.scores == expected_scores);
  }
  assert(JudgeCase({1, 1, {"T"}, {1}}, {}, {"tt", "1/1"}) ==
         kInvalidLengthError);
  assert(JudgeCase({1, 1, {"T"}, {1}}, {}, {"x", "1/1"}) ==
         kInvalidCharactersError);
  assert(JudgeCase({1, 1, {"T"}, {1}}, {}, {"f", "1/1"}) ==
         kIncorrectAnswerError);
  assert(JudgeCase({1, 1, {"T"}, {1}}, {}, {"t", "1/2"}) ==
         kIncorrectFractionError);
  assert(JudgeCase({1, 1, {"T"}, {1}}, {}, {"t", "2/2"}) ==
         kIncorrectFractionError);
  assert(JudgeCase({1, 1, {"T"}, {1}}, {}, {"t", "1/1"}) == kAccepted);

  assert(JudgeCase({1, 2, {"FT"}, {1}}, {}, {"tt", "1/1"}) == kAccepted);
  assert(JudgeCase({1, 2, {"FT"}, {1}}, {}, {"tf", "1/1"}) == kAccepted);
  assert(JudgeCase({1, 2, {"FT"}, {1}}, {}, {"ft", "1/1"}) == kAccepted);
  assert(JudgeCase({1, 2, {"FT"}, {1}}, {}, {"ff", "1/1"}) == kAccepted);
}

int main(int argc, const char* argv[]) {
  if (argc == 2 && string(argv[1]) == "-2") {
    TestLib();
    Test();
    cerr << "All tests passed!" << endl;
    return 0;
  }
  if (argc != 4) return 1;
  auto input = ParseAllInput(argv[1], ParseCaseInput);
  auto attempt = ParseAllOutput(argv[2], ParseCaseOutput);
  auto correct_output = ParseAllOutput(argv[3], ParseCaseOutput);
  string e = JudgeAllCases(input, correct_output, attempt, JudgeCase);
  if (e.empty()) return 0;
  Error(e);
}
