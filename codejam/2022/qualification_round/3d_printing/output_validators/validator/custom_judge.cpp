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

void TestLib() {
  TestStrint();
  TestTruncate();
  TestParseInt();
  TestLowercase();
  TestTokenize();
  TestSplitCases();
}

///////////////////////
// LIBRARY ENDS HERE //
///////////////////////

typedef vector<vector<int>> CaseInput;
typedef vector<int> CaseOutput;

CaseInput ParseCaseInput(istream& in) {
  CaseInput r(3, vector<int>(4));
  for (int i = 0; i < 3; ++i)
    for (int j = 0; j < 4; ++j) in >> r[i][j];
  return r;
}

void TestParseCaseInput() {
  istringstream in(R"(1 2 3 4
5 6 7 8
9 10 11 12
END)");
  AssertEqual(ParseCaseInput(in),
              (CaseInput{{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}}));
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
  if (tokens.size() != 3 && tokens.size() != 6)
    Error("Wrong number of tokens in case output");
  if (Lowercase(tokens[0]) != "case")
    Error("Case output not starting with Case");
  if (tokens[1] != ("#" + to_string(case_idx) + ":"))
    Error("Case number not formatted correctly or not correct number");
  if (tokens.size() == 3) {
    if (Lowercase(tokens[2]) != "impossible") Error("Wrong word in output");
    return {};
  }
  vector<int> r(4);
  for (int i = 0; i < 4; ++i) {
    long long n = ParseInt(tokens[2 + i]);
    if (n < 0 || n > 1000000) Error("Integer out of range");
    r[i] = n;
  }
  return r;
}

CaseOutput ParseCaseOutput(const string& input, int case_idx) {
  stringstream ss(input);
  return ParseCaseOutput(ss, case_idx);
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
  AssertError(ParseCaseOutput("Case #1: 1 2 3", 1),
              "Wrong number of tokens in case output");
  AssertError(ParseCaseOutput("Case #1: non-possible", 1),
              "Wrong word in output");
  AssertEqual(ParseCaseOutput("Case #1: iMPOSsIBlE", 1), CaseOutput());
  AssertEqual(ParseCaseOutput("Case #2: impossible", 2), CaseOutput());
  AssertEqual(ParseCaseOutput("Case #3: IMPOSSIBLE", 3), CaseOutput());
  AssertError(ParseCaseOutput("Case #1: 1 2 3 A", 1),
              "Not an integer in range: a");
  AssertError(ParseCaseOutput("Case #1: 0 2 -3 4", 1), "Integer out of range");
  AssertEqual(ParseCaseOutput("Case #42: 1 2 3 4", 42),
              (CaseOutput{1, 2, 3, 4}));
}

string CheckNumbers(const CaseInput& input, const CaseOutput& output) {
  int sum = 0;

  for (int j = 0; j < 4; ++j) {
    for (int i = 0; i < 3; ++i) {
      if (output[j] > input[i][j]) return "Too much ink";
    }
    sum += output[j];
  }
  if (sum != 1000000) return "Wrong total amount of ink";
  return "";
}

void TestCheckNumbers() {
  AssertEqual(
      CheckNumbers({{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}}, {1, 1, 1, 1}),
      "Wrong total amount of ink");
  AssertEqual(CheckNumbers({{1000000, 1000000, 500000, 500000},
                            {500000, 500000, 1000000, 1000000},
                            {400000, 1000000, 1000000, 1000000}},
                           {400000, 500000, 100000, 1}),
              "Wrong total amount of ink");
  AssertEqual(CheckNumbers({{1000000, 1000000, 500000, 500000},
                            {500000, 500000, 1000000, 1000000},
                            {400000, 1000000, 1000000, 1000000}},
                           {400000, 400000, 100000, 99999}),
              "Wrong total amount of ink");
  AssertEqual(CheckNumbers({{1000000, 1000000, 500000, 500000},
                            {500000, 500000, 1000000, 1000000},
                            {400000, 1000000, 1000000, 1000000}},
                           {500000, 400000, 0, 100000}),
              "Too much ink");
  AssertEqual(CheckNumbers({{1000000, 1000000, 500000, 500000},
                            {500000, 500000, 1000000, 1000000},
                            {400000, 1000000, 1000000, 1000000}},
                           {0, 400000, 500001, 100000}),
              "Too much ink");
  AssertEqual(CheckNumbers({{1000000, 1000000, 500000, 500000},
                            {500000, 500000, 1000000, 1000000},
                            {400000, 1000000, 1000000, 1000000}},
                           {0, 499999, 0, 500001}),
              "Too much ink");
  AssertEqual(CheckNumbers({{1000000, 1000000, 500000, 500000},
                            {500000, 500000, 1000000, 1000000},
                            {400000, 1000000, 1000000, 1000000}},
                           {0, 400000, 500000, 100000}),
              "");
}

string JudgeCase(const CaseInput& input, const CaseOutput& attempt,
                 const CaseOutput& correct_output) {
  if (!attempt.empty()) return CheckNumbers(input, attempt);
  if (correct_output.empty()) return "";
  return "Claimed impossible but it was possible";
}

void TestJudgeCase() {
  AssertEqual(
      JudgeCase({{1000000, 1000000, 500000, 500000},
                 {500000, 500000, 1000000, 1000000},
                 {400000, 1000000, 1000000, 1000000}},
                {0, 400000, 500000, 100000}, {0, 400000, 500000, 100000}),
      "");
  AssertEqual(
      JudgeCase({{1000000, 1000000, 500000, 500000},
                 {500000, 500000, 1000000, 1000000},
                 {400000, 1000000, 1000000, 1000000}},
                {0, 400000, 500000, 100001}, {0, 400000, 500000, 100000}),
      "Wrong total amount of ink");
  AssertEqual(JudgeCase({{1, 1, 1, 1}, {1, 1, 1, 1}, {1, 1, 1, 1}}, {}, {}),
              "");
  AssertEqual(JudgeCase({{1000000, 1000000, 500000, 500000},
                         {500000, 500000, 1000000, 1000000},
                         {400000, 1000000, 1000000, 1000000}},
                        {}, {0, 400000, 500000, 100000}),
              "Claimed impossible but it was possible");
}

void Test() {
  TestParseCaseInput();
  TestParseCaseOutput();
  TestCheckNumbers();
  TestJudgeCase();
}

int main(int argc, const char* argv[]) {
  if (argc == 2 && string(argv[1]) == "-2") {
    TestLib();
    Test();
    cerr << "All tests passed!" << endl;
    return 0;
  }
  if (argc != 5) return 1;
  ifstream input_stream(argv[1]);
  ifstream output_stream(argv[2]);
  ifstream correct_output_stream(argv[3]);
  error_file.open(argv[4]);
  int num_cases;
  input_stream >> num_cases;
  string e;
  for (int case_idx = 1; case_idx <= num_cases; case_idx++) {
    auto input = ParseCaseInput(input_stream);
    auto attempt = ParseCaseOutput(output_stream, case_idx);
    auto correct_output = ParseCaseOutput(correct_output_stream, case_idx);
    e = JudgeCase(input, attempt, correct_output);
    if (e.empty()) continue;
    ostringstream out;
    out << "Case #" << case_idx << ": " << e;
    e = out.str();
    break;
  }
  if (!e.empty()) Error(e);
  string token;
  if (output_stream >> token) Error("Additional output found");
  error_file << "status: VALID" << endl;
  return 0;
}
