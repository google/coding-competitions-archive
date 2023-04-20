#include <algorithm>
#include <cctype>
#include <csignal>
#include <functional>
#include <iostream>
#include <numeric>
#include <optional>
#include <ostream>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

#include "recruiting/arena/problem_dev/cocolib/cc/exceptions.h"
#include "recruiting/arena/problem_dev/cocolib/cc/judges/extended_judge_output.h"
#include "recruiting/arena/problem_dev/cocolib/cc/reader.h"
#include "recruiting/arena/problem_dev/cocolib/cc/tokenizer.h"

using int64 = int64_t;

namespace cocolib {
namespace internal {

std::vector<std::string> Args(int argc, char** argv) {
  std::vector<std::string> r(argc - 1);
  for (int i = 0; i < argc - 1; ++i) {
    r[i] = argv[i + 1];
  }
  return r;
}

std::mt19937 cocolib_rnd_generator;

void RandInit(const std::string& seed_str) {
  cocolib_rnd_generator.seed(std::hash<std::string>{}(seed_str));
}

}  // namespace internal

template <typename T, std::enable_if_t<std::is_integral_v<T>>* = nullptr>
T Rand(T min, T max) {
  std::uniform_int_distribution<T> dis(min, max);
  return dis(internal::cocolib_rnd_generator);
}

template <typename T>
void Shuffle(std::vector<T>& v) {
  std::shuffle(v.begin(), v.end(), internal::cocolib_rnd_generator);
}

namespace {
std::function<int(int, int)> override_rand_int = Rand<int>;
std::function<int64(int64, int64)> override_rand_int64 = Rand<int64>;
std::optional<std::function<std::vector<int>(int)>>
    override_random_permutation = std::nullopt;
}  // namespace
void OverrideRandInt(std::function<int(int, int)> rand_int) {
  override_rand_int = rand_int;
}
void OverrideRandInt64(std::function<int64(int64, int64)> rand_int64) {
  override_rand_int64 = rand_int64;
}
void OverrideRandomPermutation(
    std::function<std::vector<int>(int)> random_permutation) {
  override_random_permutation = random_permutation;
}
int Rand(int min, int max) { return override_rand_int(min, max); }
int64 Rand(int64 min, int64 max) { return override_rand_int64(min, max); }

std::vector<int> RandomPermutation(int n) {
  if (override_random_permutation) return (*override_random_permutation)(n);
  std::vector<int> r(n);
  std::iota(r.begin(), r.end(), 0);
  Shuffle(r);
  return r;
}

#ifdef NDEBUG
#define COCOLIB_MAIN(ClassName, Method)  // NOOP
#else
#define COCOLIB_MAIN(ClassName, Method)                             \
  int main(int argc, char** argv) {                                 \
    cocolib::internal::RandInit(#ClassName #Method "_#g00g13");     \
    return ClassName().Method(cocolib::internal::Args(argc, argv)); \
  }
#endif

#define COCOLIB_MULTIPLE_CASES_MAIN(ClassName) \
  COCOLIB_MAIN(ClassName, RunAndJudgeMultipleCases)

namespace internal {

class Writer {
 public:
  explicit Writer(std::ostream& out) : out_(out) {}

  template <typename Arg, typename... Args>
  void WriteL(Arg arg, Args... args) {
    out_ << arg;
    ((out_ << " " << args), ...);
    out_ << std::endl;
  }

 private:
  std::ostream& out_;
};

class ToStringWriter : public Writer {
 public:
  ToStringWriter() : Writer(out_) {}

  std::string output() const { return out_.str(); }

 private:
  std::ostringstream out_;
};

class ToStdoutWriter : public Writer {
 public:
  ToStdoutWriter() : Writer(std::cout) {}
};

template <typename Case, typename Result>
class InteractiveJudge {
 public:
  using CaseType = Case;
  using ResultType = Result;

  InteractiveJudge() = default;
  virtual ~InteractiveJudge() = default;

  int RunAndJudgeMultipleCases(const std::vector<std::string>& args) {
    if (args == std::vector<std::string>{"-2"}) return 0;  // no self tests
    if (args.size() != 2) return 1;
    int test_set_index;
    try {
      test_set_index = std::stoi(args[0]);
    } catch (...) {
      return 1;
    }
    FromStdin<LenientReader> reader;
    ToStdoutWriter writer;
    ExtendedJudgeOutput out;

    // This is needed to properly detect broken pipes if the
    // users' code crashes while we are alive.
    signal(SIGPIPE, SIG_IGN);
    try {
      out = RunAndJudgeMultipleCases(test_set_index, reader, writer);
    } catch (const Exception& e) {
      out = WrongAnswer(e.message());
    }
    std::cerr << "Finished successfully with output:" << std::endl;
    std::cerr << out.AsTextProto(ExtendedJudgeOutput::UNESCAPED) << std::endl;
    out.WriteToFile(args[1]);
    std::cerr << "Output written to output file" << std::endl;
    return 0;
  }

 protected:
  ExtendedJudgeOutput RunAndJudgeMultipleCases(int test_set_index,
                                               LenientReader& reader,
                                               Writer& writer) {
    return RunAndJudgeMultipleCases(test_set_index, GetCases(test_set_index),
                                    reader, writer);
  }

  ExtendedJudgeOutput RunAndJudgeMultipleCases(int test_set_index,
                                               const std::vector<Case>& cases,
                                               LenientReader& reader,
                                               Writer& writer) {
    std::vector<Result> results;
    results.reserve(cases.size());
    writer.WriteL(cases.size());
    for (int case_num = 1; case_num <= cases.size(); ++case_num) {
      try {
        results.push_back(RunAndJudgeCase(test_set_index, cases[case_num - 1],
                                          reader, writer));
      } catch (Exception& e) {
        e.set_message("Case #" + std::to_string(case_num) + ": " + e.message());
        throw;
      }
    }
    reader.AssertEof();
    return CombineResults(test_set_index, results);
  }

  virtual Result RunAndJudgeCase(int test_set_index, const Case& c,
                                 LenientReader& reader, Writer& writer) = 0;
  virtual ExtendedJudgeOutput CombineResults(
      int test_set_index, const std::vector<Result>& results) = 0;

 protected:
  template <typename... Args>
  static void Assert(bool condition, Args... args) {
    if (!condition) throw WrongAnswerException(args...);
  }

  template <typename T>
  static int CountIf(const std::function<bool(const T&)>& pred,
                     const std::vector<T>& results) {
    int r = 0;
    for (const auto& result : results) {
      if (pred(result)) ++r;
    }
    return r;
  }

  static int CountTrue(const std::vector<bool>& results) {
    return CountIf<bool>([](bool result) { return result; }, results);
  }

  template <typename T>
  static T Fold(std::function<T(const T&, const T&)> comb,
                const std::vector<T>& results) {
    T r = results[0];
    for (int i = 1; i < results.size(); ++i) {
      r = comb(r, results[i]);
    }
    return r;
  }

  template <typename T, std::enable_if_t<std::is_arithmetic_v<T>>* = nullptr>
  static T Sum(const std::vector<T>& results) {
    return Fold([](const T& t1, const T& t2) { return t1 + t2; }, results);
  }

  template <typename T, std::enable_if_t<std::is_arithmetic_v<T>>* = nullptr>
  static T Max(const std::vector<T>& results) {
    return Fold(std::max, results);
  }

  template <typename T, std::enable_if_t<std::is_arithmetic_v<T>>* = nullptr>
  static T Min(const std::vector<T>& results) {
    return Fold(std::min, results);
  }

  static std::vector<Case> FromCasesSet(const std::set<Case>& cases_set) {
    std::vector<Case> cases(cases_set.begin(), cases_set.end());
    std::sort(cases.begin(), cases.end());
    Shuffle(cases);
    return cases;
  }

  virtual std::vector<Case> GetCases(int test_set_index) {
    throw IncorrectInteractiveJudgeCallException(
        "Must override GetCases() to call RunAndJudgeMultipleCases");
  }
};

template <typename Case>
class ResultlessInteractiveJudge : public InteractiveJudge<Case, void*> {
 public:
  ResultlessInteractiveJudge() = default;

  virtual void RunCase(int test_set_index, const Case& c, LenientReader& reader,
                       Writer& writer) = 0;

 protected:
  void* RunAndJudgeCase(int test_set_index, const Case& c,
                        LenientReader& reader, Writer& writer) override {
    RunCase(test_set_index, c, reader, writer);
    return nullptr;
  }
  ExtendedJudgeOutput CombineResults(
      int test_set_index, const std::vector<void*>& results) override {
    return cocolib::Correct();
  }
};

class Dialog {
 public:
  enum Origin { UNKNOWN, JUDGE, USER };

  struct Message {
    Origin origin;
    std::string message;
  };

  static std::vector<Message> ParseMessages(const std::string& messages_str) {
    std::vector<Message> messages;
    for (size_t i = 0, next_i; i < messages_str.size(); i = next_i + 1) {
      next_i = messages_str.find('\n', i);
      if (next_i == std::string::npos) next_i = messages_str.size();
      // Skip leading spaces.
      while (i < next_i && std::isspace(messages_str[i])) ++i;
      if (next_i - i < 1) continue;  // Skip empty lines.
      if (next_i - i < 4 ||
          (messages_str[i] != 'J' && messages_str[i] != 'U') ||
          messages_str[i + 1] != ':' || messages_str[i + 2] != ' ') {
        throw Exception("Could not parse messages, error at line ",
                        messages.size() + 1, ":\n", messages_str.substr(0, i),
                        "--- error below ---\n", messages_str.substr(i));
      }
      messages.push_back(
          {.origin = messages_str[i] == 'J' ? JUDGE : USER,
           .message = messages_str.substr(i + 3, next_i - i - 3)});
    }
    return messages;
  }

  Dialog(const std::vector<Message>& messages)  // NOLINT
      : reader_(Lines(USER, messages)),
        writer_(),
        expected_judge_output_(Lines(JUDGE, messages)) {}

  Dialog(const std::string& messages_str)  // NOLINT
      : Dialog(ParseMessages(messages_str)) {}

  Dialog(const char* messages_str)  // NOLINT
      : Dialog(ParseMessages(messages_str)) {}

  // This can be done better with StatusOr once we port this code
  // to a test-only library that can use full google3.
  void CheckOutput() const {
    if (writer_.output() != expected_judge_output_) {
      throw Exception("Unexpected judge output.\n Expected:\n",
                      expected_judge_output_, "\nActual:\n", writer_.output());
    }
  }
  Writer& writer() { return writer_; }
  LenientReader& reader() { return reader_; }

 private:
  static std::string Lines(Origin origin,
                           const std::vector<Message>& messages) {
    std::string r;
    for (const Message& message : messages) {
      if (message.origin == origin) r += message.message + "\n";
    }
    return r;
  }

  FromString<LenientReader> reader_;
  ToStringWriter writer_;
  std::string expected_judge_output_;
};

template <typename T>
class TestOf : public T {
 public:
  TestOf() = default;

  typename T::ResultType RunAndJudgeCaseOnDialog(int test_set_index,
                                                 const typename T::CaseType& c,
                                                 Dialog dialog) {
    typename T::ResultType r =
        T::RunAndJudgeCase(test_set_index, c, dialog.reader(), dialog.writer());
    dialog.CheckOutput();
    return r;
  }

  ExtendedJudgeOutput RunAndJudgeMultipleCasesOnDialog(
      const std::vector<typename T::CaseType>& cases, Dialog dialog) {
    return RunAndJudgeMultipleCasesOnDialog(0, cases, dialog);
  }

  ExtendedJudgeOutput RunAndJudgeMultipleCasesOnDialog(
      int test_set_index, const std::vector<typename T::CaseType>& cases,
      Dialog dialog) {
    ExtendedJudgeOutput r = T::RunAndJudgeMultipleCases(
        test_set_index, cases, dialog.reader(), dialog.writer());
    dialog.CheckOutput();
    return r;
  }

  using T::CombineResults;
  using T::GetCases;

 private:
  using T::RunAndJudgeMultipleCases;
};

}  // namespace internal

using internal::InteractiveJudge;
using internal::ResultlessInteractiveJudge;
using internal::TestOf;
using internal::ToStringWriter;
using internal::Writer;

}  // namespace cocolib

using cocolib::Int;
using cocolib::LenientReader;
using cocolib::List;
using cocolib::Rand;
using cocolib::RandomPermutation;
using cocolib::Set;
using cocolib::Writer;

struct Edge {
  int a, b;
  void normalize() {
    if (a > b) std::swap(a, b);
  }
  std::string ToString() const {
    return std::to_string(a + 1) + "-" + std::to_string(b + 1);
  }
  bool operator<(const Edge& o) const {
    if (a != o.a) return a < o.a;
    return b < o.b;
  }
  bool operator==(const Edge& o) const { return a == o.a && b == o.b; }
};

// For tests
std::ostream& operator<<(std::ostream& o, const Edge& e) {
  return o << e.a << "-" << e.b;
}

using Graph = std::vector<Edge>;
using Perm = std::vector<int>;

Graph ReadGraph(int n, int m, LenientReader& reader) {
  Graph g(m);
  for (Edge& edge : g) {
    std::tie(edge.a, edge.b) = reader.ReadL(Int("A", 1, n), Int("B", 1, n));
    edge.a--;
    edge.b--;
  }
  return g;
}

Graph Normalized(const Graph& g) {
  Graph r(g);
  for (Edge& edge : r) {
    edge.normalize();
  }
  std::sort(r.begin(), r.end());
  return r;
}

std::optional<Edge> FindLoop(const Graph& g) {
  for (const Edge& edge : g) {
    if (edge.a == edge.b) return edge;
  }
  return std::nullopt;
}

std::optional<Edge> FindRepeatedEdge(const Graph& g) {
  for (int i = 0; i < g.size() - 1; ++i) {
    if (!(g[i] < g[i + 1])) return g[i];
  }
  return std::nullopt;
}

Graph Permuted(const Graph& graph, const Perm& perm) {
  Graph r;
  r.reserve(graph.size());
  for (const Edge& edge : graph) {
    r.push_back({perm[edge.a], perm[edge.b]});
  }
  return r;
}

void WriteGraph(Writer& writer, const Graph& g) {
  for (const Edge& edge : g) {
    writer.WriteL(edge.a + 1, edge.b + 1);
  }
}

struct Case {
  int C, L;  // NOLINT
  bool operator<(const Case& o) const {
    if (C != o.C) return C < o.C;
    return L < o.L;
  }
};

class RingPreservingNetworksInteractiveJudge
    : public cocolib::InteractiveJudge<Case, bool> {
 public:
  RingPreservingNetworksInteractiveJudge() = default;

  static constexpr int MAX_C = 10000;  // NOLINT

 protected:
  std::vector<Case> GetCases(int test_set_index) override {
    auto MaxL = [test_set_index](int C) {
      return std::min<int64>(static_cast<int64>(C) * (C - 1) / 2,
                             test_set_index == 0 ? C + 10 : 2 * MAX_C);
    };
    std::set<Case> r;
    auto InsertInteresting = [MaxL, &r](int C, bool random_half = false) {
      for (int L = 2*C-4; L <= 2*C; L++) {
        if (C <= L && L <= MaxL(C)) {
          if (!random_half || Rand(1,2) == 1) {
            r.insert({C, L});
          }
        }
      }
    };
    if (test_set_index == 0) {
      for (int C : {3, 4, 5, 6, MAX_C / 2, MAX_C / 2 + 1, MAX_C - 1, MAX_C}) {
        int MAX_L = MaxL(C);
        for (int L = C; L <= MAX_L; ++L) {
          r.insert({C, L});
        }
      }
      r.insert({7, 15});
      for (int C = 7; C <= 13; C++) {
        InsertInteresting(C);
      }
    } else {
      for (int C : {199, 200, 201, MAX_C / 2, MAX_C / 2 + 1, MAX_C - 2,
                    MAX_C - 1, MAX_C}) {
        int MAX_L = MaxL(C);
        r.insert({C, MAX_L});
        r.insert({C, MAX_L - 1});
        for (int d = 2; d <= 9; ++d) {
          int MID_L = (MAX_L - C) * d / 10 + C;
          int L = Rand(MID_L - 10, MID_L + 10);
          if (C == MAX_C || C == 200 || Rand(1,2) == 1) {
            r.insert({C, L});
          }
        }
        InsertInteresting(C, C != MAX_C);
      }
    }
    while (r.size() < 100) {
      int C = Rand(MAX_C / 2, MAX_C);
      int MAX_L = MaxL(C);
      int L = Rand(C, MAX_L);
      r.insert({C, L});
    }
    return FromCasesSet(r);
  }

  bool RunAndJudgeCase(int test_set_index, const Case& c, LenientReader& reader,
                       Writer& writer) override {
    writer.WriteL(c.C, c.L);
    Graph g = Normalized(ReadGraph(c.C, c.L, reader));

    std::vector<int> perm = RandomPermutation(c.C);
    Graph perm_g = Normalized(Permuted(g, perm));
    WriteGraph(writer, perm_g);

    std::vector<int> path = reader.ReadL(List(Int("Trace", 1, c.C), c.C));

    if (FindLoop(g) || FindRepeatedEdge(g)) return false;

    if (std::set<int>(path.begin(), path.end()).size() != c.C) return false;
    std::set<Edge> perm_g_edges(perm_g.begin(), perm_g.end());
    for (int i = 0; i < path.size(); ++i) {
      Edge e = {path[i] - 1, path[(i + 1) % path.size()] - 1};
      e.normalize();
      if (perm_g_edges.count(e) == 0) return false;
    }
    return true;
  }
  cocolib::ExtendedJudgeOutput CombineResults(
      int test_set_index, const std::vector<bool>& results) override {
    int correct = CountTrue(results);
    if (correct == results.size()) {
      return cocolib::Correct();
    } else {
      return cocolib::WrongAnswer("Only ", correct, " out of ", results.size(),
                                  " cases solved correctly");
    }
  }
};

COCOLIB_MULTIPLE_CASES_MAIN(RingPreservingNetworksInteractiveJudge)