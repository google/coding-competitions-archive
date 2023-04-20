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
string JudgeAllCases(const vector<T>& input, const vector<U>& correct_output,
                     const vector<U>& attempt,
                     string JudgeCase(const T&, const U&, const U&)) {
  if (attempt.size() != input.size())
    Error(string("Wrong number of cases in attempt: ") +
          Strint(attempt.size()) + ", expected: " + Strint(input.size()));
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
  if (n != o) return Strint(o) + " not equal to input: " + Strint(n);
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
  TestStrint();
  TestTruncate();
  TestParseInt();
  TestLowercase();
  TestTokenize();
  TestSplitCases();
  TestJudgeAllCases();
}

//////////////////////////////////////////////

typedef vector<string> CaseInput;
typedef string CaseOutput;

const string kBadImpossibleClaimError =
    "Contestant claims a solution does not exist while judge finds a solution";
const string kOutputTooShortError = "Solution string is too short";
const string kOutputTooLongError = "Solution string is too long";
const string kInvalidCharacterError = "A non-English character found";

string OutputDoesNotMatchPatternError(int pattern_index) {
  return "Solution string does not match pattern #" + Strint(pattern_index);
}

const CaseOutput kImpossibleKeyword = "*";
const int kMinOutputLength = 1;
const int kMaxOutputLength = 10000;

CaseInput ParseCaseInput(istream& in) {
  int N;
  in >> N;

  CaseInput input(N);
  for (int i = 0; i < N; ++i) {
    in >> input[i];
    input[i] = Lowercase(input[i]);
  }
  return input;
}

CaseOutput ParseCaseOutput(const vector<vector<string>>& lines) {
  if (lines.size() != 1) Error("Wrong number of lines in case output");
  if (lines[0].size() != 1) Error("Wrong number of tokens in case output");
  return lines[0][0];
}

vector<int> KmpPreprocess(const string& s) {
  vector<int> kmp(s.size());
  for (int i = 1, k = 0; i < s.size(); ++i) {
    while (k && s[k] != s[i]) {
      k = kmp[k - 1];
    }
    if (s[k] == s[i]) {
      ++k;
    }
    kmp[i] = k;
  }
  return kmp;
}

int NextMatchEndIndex(
    const string& pattern, const string& full_string, int start_index) {
  vector<int> kmp = KmpPreprocess(pattern);
  int k = 0;
  for (int i = start_index; i < full_string.size(); ++i) {
    while (k && pattern[k] != full_string[i]) {
      k = kmp[k - 1];
    }
    if (pattern[k] == full_string[i]) {
      ++k;
    }
    if (k == pattern.size()) {
      return i;
    }
  }
  return INT_MAX;
}

void TestNextMatchEndIndex() {
  assert(NextMatchEndIndex("hello", "hello", 0) == 4);
  assert(NextMatchEndIndex("hellos", "hello", 0) == INT_MAX);
  assert(NextMatchEndIndex("hello", "hello", 1) == INT_MAX);
  assert(NextMatchEndIndex("llo", "hello", 1) == 4);
  assert(NextMatchEndIndex("l", "hello", 1) == 2);
  assert(NextMatchEndIndex("l", "hello", 2) == 2);
  assert(NextMatchEndIndex("l", "hello", 3) == 3);
  assert(NextMatchEndIndex("l", "hello", 4) == INT_MAX);
  for (const string& s :
       {"a", "aa", "ab", "aaa", "aab", "aba", "abab", "abba", "abbabbabbab",
        "abbabbabb", "ababababababbabaabbab"}) {
    for (int i = 0; i < s.size(); ++i)
      for (int j = i + 1; j <= s.size(); ++j) {
        const string pattern = s.substr(i, j - i);
        for (int k = 0; k <= s.size() + 2; ++k) {
          int exp = s.find(pattern, k);
          if (exp >= s.size()) {
            exp = INT_MAX;
          } else {
            exp += j - i - 1;
          }
          assert(NextMatchEndIndex(pattern, s, k) == exp);
        }
      }
  }
}

bool PatternMatch(string long_string, string pattern) {
  if (count(pattern.begin(), pattern.end(), '*') == 0) {
    return long_string == pattern;
  }

  for (int i = 0; i < 2; ++i) {
    while (pattern.back() != '*') {
      if (long_string.back() != pattern.back()) {
        return false;
      }
      long_string.pop_back();
      pattern.pop_back();
    }
    reverse(long_string.begin(), long_string.end());
    reverse(pattern.begin(), pattern.end());
  }

  int current_long_string_index = 0;
  string current_pattern = "";
  for (int i = 0; i < pattern.size(); ++i) {
    if (pattern[i] == '*') {
      if (current_pattern.size() > 0) {
        current_long_string_index = NextMatchEndIndex(
            current_pattern, long_string, current_long_string_index);
        if (current_long_string_index > long_string.size()) {
          return false;
        }
        ++current_long_string_index;
        current_pattern = "";
      }
    } else {
      current_pattern += pattern[i];
    }
  }

  return true;
}

void TestPatternMatch() {
  assert(PatternMatch("codejam", "codejam"));
  assert(PatternMatch("googlecodejam", "*codejam"));
  assert(PatternMatch("googlecodejam", "*code*"));
  assert(PatternMatch("googlecodejam", "*"));
  assert(PatternMatch("googlecodejam", "*************************"));
  assert(PatternMatch("googlecodejam", "*o*o*o*"));
  assert(PatternMatch("googlecodejam", "*oo*"));
  assert(PatternMatch("helpiamtrappedinaunittestfactory",
                      "h*i*trap*unit*test*ry"));
  assert(!PatternMatch("google", "codejam"));
  assert(!PatternMatch("googlecodejam", "code"));
  assert(!PatternMatch("googlecodejam", "*code"));
  assert(!PatternMatch("googlecodejam", "code*"));
  assert(!PatternMatch("googlecodejam", "*ooo*"));
  assert(!PatternMatch("helpiamtrappedinaunittestfactory", "*unit*test*h*"));
}

string JudgeCase(const CaseInput& input, const CaseOutput& correct_output,
                 const CaseOutput& attempt) {
  if (attempt == kImpossibleKeyword) {
    return correct_output == kImpossibleKeyword ? "" : kBadImpossibleClaimError;
  }

  if (attempt.size() < kMinOutputLength) {
    return kOutputTooShortError;
  }
  if (attempt.size() > kMaxOutputLength) {
    return kOutputTooLongError;
  }
  if (any_of(
      attempt.begin(),
      attempt.end(),
      [](char c) { return !islower(c); })
  ) {
    return kInvalidCharacterError;
  }

  for (int i = 0; i < input.size(); ++i) {
    if (!PatternMatch(attempt, input[i])) {
      return OutputDoesNotMatchPatternError(i + 1);
    }
  }
  return "";
}

void TestJudgeCase() {
  assert(JudgeCase({"*", "**"}, "codejam", "") == kOutputTooShortError);
  assert(JudgeCase({"*", "**"}, "codejam", "*") == kBadImpossibleClaimError);
  assert(JudgeCase({"*", "**"}, "codejam", string(kMaxOutputLength + 1, 'a')) ==
         kOutputTooLongError);
  assert(JudgeCase({"*", "**"}, "codejam", "yes!") == kInvalidCharacterError);
  assert(JudgeCase({"*", "**"}, "codejam", "google") == "");

  assert(JudgeCase({"g*", "*e"}, "ge", "codejam") ==
         OutputDoesNotMatchPatternError(1));
  assert(JudgeCase({"g*", "*e"}, "ge", "googlecodejam") ==
         OutputDoesNotMatchPatternError(2));
  assert(JudgeCase({"g*", "*e"}, "ge", "google") == "");
}

void Test() {
  TestNextMatchEndIndex();
  TestPatternMatch();
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
  auto input = ParseAllInput(argv[1], ParseCaseInput);
  auto attempt = ParseAllOutput(argv[2], ParseCaseOutput);
  auto correct_output = ParseAllOutput(argv[3], ParseCaseOutput);
  string e = JudgeAllCases(input, correct_output, attempt, JudgeCase);
  if (e.empty()) return 0;
  Error(e);
}
