import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.*;
import java.util.*;

public class judge {

  static final int T = 100;
  static final int MAX_INTERACTIONS = 300;
  static final int TEST_CASE_RANDOM = 0;
  static final int TEST_CASE_ADVERSARIAL = 1;

  static final Random rand = new Random();
  static final Scanner in = new Scanner(System.in);

  static final int EXIT_CODE_INVALID_ARGS = 101;
  static final int EXIT_CODE_PRINT_RESULTS_FAILED = 102;

  // Graph of all possible States.
  static int ns;
  static final ArrayList<State> states = new ArrayList<State>();
  static final HashMap<State, Integer> stateMap = new HashMap<State, Integer>();
  static ArrayList<Edge>[] edges;
  static int[] dists;

  static enum AdversarialStrategy {
    // Always choose the resulting bit count that puts the solution as far away from the goal as
    // possible.
    ALWAYS_CHOOSE_FURTHEST,
    // Choose randomly but weight linearly by distance.
    WEIGHT_BY_DISTANCE,
    // Choose randomly but weight by square distance (bias towards further states).
    WEIGHT_BY_SQUARE_DISTANCE
  }

  static final AdversarialStrategy[] STRATEGIES = AdversarialStrategy.values();

  public static void main(String[] args) {
    // Run self tests if requested.
    if (args.length == 1 && args[0].equals("-2")) {
      try {
        runSelfTests();
      } catch (Throwable t) {
        t.printStackTrace();
        System.exit(1);
      }
      return;
    }
    // Check number of arguments.
    if (args.length != 2) {
      System.err.printf(
          "Expected 2 commandline args but received %d\n"
              + "Usage: CustomJudge [testCaseIndex] [resultsFile]\n",
          args.length);
      System.exit(EXIT_CODE_INVALID_ARGS);
    }
    try {
      // Get the case index.
      int caseIndex = Integer.parseInt(args[0]);
      // If this is an adversarial Test Set, build the needed dists array and states map.
      if (caseIndex == TEST_CASE_ADVERSARIAL) {
        buildDistArray();
      }

      // Print the number of test cases.
      output(T);
      for (int ci = 1; ci <= T; ci++) {
        try {
          if (caseIndex == TEST_CASE_RANDOM) {
            // Start a random judge case with a value in the range [1, 255].
            runRandomCase(rand.nextInt(255) + 1);
          } else if (caseIndex == TEST_CASE_ADVERSARIAL) {
            // Choose a starting bit count and strategy to use.
            int bitCount = (ci % 8) + 1;
            int strategyIndex = (ci / 8) % 3;
            // Start an adversarial judge case with the given starting bit count and strategy.
            runAdversarialCase(bitCount, STRATEGIES[strategyIndex]);
          } else {
            // Throw a judge error if this is not a test case we recognize.
            throw new JudgeError("Invalid CaseIndex " + caseIndex);
          }
        } catch (WrongAnswerException | IOException e) {
          // IOExceptions are considered Wrong Answers.
          // Output -1 so the contestant knows to exit.
          output(-1);
          printResults(args[1], "INVALID", e.getMessage());
          return;
        }
      }
      printResults(args[1], "VALID", "");
    } catch (JudgeError e) {
      output(-1);
      printResults(args[1], "INTERNAL_JUDGE_ERROR", e.getMessage());
    } catch (Throwable t) {
      output(-1);
      // Catch all other possible errors and throw a judge error.
      printResults(args[1], "INTERNAL_JUDGE_ERROR", t.getMessage());
    }
  }

  // Runs a case using completely random choices for the rotation amount.
  static void runRandomCase(int startingNumber)
      throws JudgeError, WrongAnswerException, IOException {
    // Check that the starting number is valid.
    if (startingNumber < 1 || startingNumber > 255) {
      throw new JudgeError("Starting number must be in range [1, 255] but is " + startingNumber);
    }
    int x = startingNumber;
    int interaction = 0;
    while (true) {
      interaction++;
      // Read the value from the contestant.
      int v = readValue();
      // Choose a rotation value.
      int r = rand.nextInt(8);
      // Compute the next value of x.
      int w = rotate(v, r);
      x ^= w;
      // If this was the last interaction but the contestant did not reach 0, give WrongAnswer.
      if (x != 0 && interaction == MAX_INTERACTIONS) {
        throw new WrongAnswerException(
            String.format("Did not reach 0 after %d exchanges", MAX_INTERACTIONS));
      }
      // Output the bitcount.
      output(Integer.bitCount(x));
      // If the contestant reached 0, end this case.
      if (x == 0) return;
    }
  }

  static void runAdversarialCase(int startingBitCount, AdversarialStrategy strategy)
      throws JudgeError, WrongAnswerException, IOException {
    if (startingBitCount < 1 || startingBitCount > 8) {
      throw new JudgeError("Starting bit count must be in range [1, 8] but is " + startingBitCount);
    }
    // Build a starting state for the given bit count.
    State state = State.fromBitCount(startingBitCount);
    int interaction = 0;
    while (true) {
      interaction++;
      // Read the value from the contestant.
      int v = readValue();
      // Compute the next possible states for all possible bit count values we could commit to.
      State[] nexts = state.next(v);
      // Commit to a state (bit count value) according to our adversarial strategy.
      State next = chooseNextState(nexts, strategy);
      // Check that all values in the next state could be reached from the current state.
      validateTransition(state, next, v);
      // Update our state.
      state = next;
      // If this was the last interaction but the contestant did not reach 0, give WrongAnswer.
      if (state.bitCount() > 0 && interaction == MAX_INTERACTIONS) {
        throw new WrongAnswerException(
            String.format("Did not reach 0 after %d exchanges", MAX_INTERACTIONS));
      }
      // Output the bitcount.
      output(state.bitCount());
      // If the contestant reached 0, end this case.
      if (state.bitCount() == 0) return;
    }
  }

  // Returns the next state to choose according to the chosen strategy.
  static State chooseNextState(State[] states, AdversarialStrategy strategy) throws JudgeError {
    if (strategy == AdversarialStrategy.ALWAYS_CHOOSE_FURTHEST) {
      // Find the state with the largest distance.
      State next = null;
      for (State s : states) {
        if (s == null || s.arr.isEmpty()) continue;
        if (next == null || s.getDist() > next.getDist()) {
          next = s;
        }
      }
      return next;
    }
    // Weight the states accordingly.
    int[] weights = new int[9];
    int totalWeight = 0;
    for (int i = 0; i <= 8; i++) {
      weights[i] = getWeight(states[i], strategy);
      totalWeight += weights[i];
    }
    if (totalWeight == 0) throw new JudgeError("Total weight is 0");
    // Choose a random value in range [0, totalWeight)
    int x = rand.nextInt(totalWeight);
    for (int i = 0; i <= 8; i++) {
      x -= weights[i];
      // If this weight tipped things over, we return this state.
      if (x < 0) return states[i];
    }
    // Unreachable.
    return null;
  }

  // Compute a weight according to the given strategy (null states or empty states are weight 0).
  static int getWeight(State state, AdversarialStrategy strategy) {
    if (state == null || state.arr.isEmpty()) return 0;
    // Add 1 to dist because a 0-distance still technically should have a weight.
    int dist = state.getDist() + 1;
    if (strategy == AdversarialStrategy.WEIGHT_BY_DISTANCE) return dist;
    return dist * dist;
  }

  // Reads an 8-bit value such as 01001011 and returns the integer value it represents.
  // Throws an IOException if no valid 8 character string with only 0's and 1's can be read.
  static int readValue() throws IOException {
    String str;
    try {
      str = in.next();
    } catch (NoSuchElementException | IllegalStateException e) {
      throw new IOException("Unexpected end of input stream");
    }
    // Check the length of the input string.
    if (str.length() != 8) {
      throw new IOException(
          String.format("Value must be an 8-bit integer but was %d characters long", str.length()));
    }
    // Build the integer and check that each character is a 0 or a 1.
    int x = 0;
    for (char c : str.toCharArray()) {
      x <<= 1;
      if (c == '1') x++;
      else if (c != '0')
        throw new IOException(String.format("Value must be an 8-bit integer but was %s", str));
    }
    return x;
  }

  // Outputs the integer x and suppresses any IOExceptions.
  static void output(int x) {
    try {
      // Actually print the integer (System.out.println flushes).
      System.out.println(x);
    } catch (Throwable t) {
      // Ignore exception.
    }
  }

  // Throws a JudgeError if there is a value in b that cannot be reached from a value xoring with
  // some rotation of v.
  // Also throws a JudgeError if two values in b do not have the same bit count.
  static void validateTransition(State a, State b, int v) throws JudgeError {
    // Check that all bitcounts are the same.
    int bc = Integer.bitCount(b.arr.get(0));
    for (int y : b.arr)
      if (Integer.bitCount(y) != bc)
        throw new JudgeError("State has values with different bit counts");
    outer:
    for (int y : b.arr) {
      for (int x : a.arr) {
        for (int r = 0; r < 8; r++) {
          // If this value from a with this rotation could reach y, then we now know y is valid.
          if (normalize(x ^ rotate(v, r)) == y) continue outer;
        }
      }
      // If nothing could reach y, we have a big problem.
      throw new JudgeError(String.format("No way to transition from %s to %s using %d", a, b, v));
    }
  }

  static String convertToPrintableAscii(String str) {
    StringBuilder sb = new StringBuilder();
    for (char c : str.toCharArray()) {
      if (c == '\n') sb.append("\\n");
      else if (c == '\r') sb.append("\\r");
      else if (c >= 32 && c < 127) sb.append(c);
      else sb.append(String.format("\\u%04x", (int) c));
    }
    return sb.toString();
  }
  // Print the judge results proto.
  static void printResults(String outputFile, String status, String message) {
    try (PrintWriter resultsWriter =
        new PrintWriter(
            new BufferedWriter(new OutputStreamWriter(new FileOutputStream(outputFile), UTF_8)))) {
      resultsWriter.printf("status: %s\n", status);
      resultsWriter.printf(
          "status_message: \"%s\"\n", convertToPrintableAscii(message).replace("\\", "\\\\").replace("\"", "\\\""));
    } catch (IOException e) {
      e.printStackTrace();
      System.exit(EXIT_CODE_PRINT_RESULTS_FAILED);
    }
  }

  static void runSelfTests() throws JudgeError {
    // Test rotate.
    expectEqual(rotate(0), 0);
    expectEqual(rotate(1), 2);
    expectEqual(rotate(0b10001100), 0b00011001);
    expectEqual(rotate(0b10001100, 3), 0b01100100);

    // Test normalize.
    expectEqual(normalize(0), 0);
    expectEqual(normalize(1), 1);
    expectEqual(normalize(0b01000000), 1);
    expectEqual(normalize(0b10000000), 1);
    expectEqual(normalize(0b01010001), 0b00010101);

    // Check that all states are solvable.
    buildDistArray();
    for (int i = 0; i < ns; i++) {
      if (dists[i] == -2) {
        throw new JudgeError("Not all states are solvable");
      }
    }
  }

  static void expectEqual(int a, int b) {
    if (a != b) System.exit(1);
  }

  static void expectEqual(State a, State b) {
    if (!a.equals(b)) System.exit(1);
  }

  // Populates dists[] to hold what the shortest distance to 0 is for an optimal solution against an
  // adversarial judge.
  static void buildDistArray() throws JudgeError {
    buildGraph();
    // Initialize all distances to -2.
    dists = new int[ns];
    Arrays.fill(dists, -2);
    // Start a BFS from the ending state.
    State end = new State();
    end.add(0);
    int ei = stateMap.get(end);
    dists[ei] = 0;
    while (true) {
      // This BFS is a bit weird because a new state is only solvable if all possible bit counts
      // that
      // it could map to for a given value v have been found.
      boolean found = false;
      for (int i = 0; i < ns; i++) {
        // Find a state we haven't solved for yet.
        if (dists[i] != -2) continue;
        outer:
        for (Edge e : edges[i]) {
          int dist = 0;
          for (int j = 0; j <= 8; j++) {
            // If this edge points to an invalid/impossible state, it's not a real edge.
            if (e.next[j] == -1) continue;
            // If some rotation could result in a state we haven't seen yet, we can't do this state
            // yet.
            if (dists[e.next[j]] == -2) continue outer;
            // The judge will work against us so we maximize the distance of all possible bit count
            // results.
            dist = Math.max(dist, dists[e.next[j]] + 1);
          }
          // We get to choose the value we use so we take the min of all edges from here.
          dists[i] = dists[i] == -2 ? dist : Math.min(dists[i], dist);
          found = true;
          break;
        }
      }
      // If we didn't update anything else then we are done.
      if (!found) break;
    }
  }

  // Creates a graph between all possible states with all possible values given from any state.
  static void buildGraph() {
    // Build all possible states.
    buildStates();
    edges = new ArrayList[ns];
    for (int i = 0; i < ns; i++) {
      // Each state has "256" edges coming out of it (one for every unique value we could provide).
      // Each edge points to up to 9 states (each possible resultant bit count value from all
      // possible rotations the judge could choose).
      edges[i] = new ArrayList<>();
      State s = states.get(i);
      for (int v = 1; v <= 255; v++) {
        // If this is not a unique value, we ignore it.
        if (normalize(v) != v) continue;
        Edge e = new Edge();
        // Set the edge's value.
        e.v = v;
        int idx = 0;
        // Set all the edge's next's (states it could transition to depending on what the judge
        // does).
        for (State ss : s.next(v)) {
          e.next[idx++] = ss.arr.isEmpty() ? -1 : stateMap.get(ss);
        }
        // Add the edge to the proper adjacency list.
        edges[i].add(e);
      }
    }
  }

  // Enumerates all possible states.
  static void buildStates() {
    State start = new State();
    // Sort all unique values by their bit counts (two numbers are the same if they are cyclic
    // rotations of each other).
    ArrayList<Integer>[] lists = new ArrayList[9];
    for (int i = 0; i <= 8; i++) lists[i] = new ArrayList<Integer>();
    for (int x = 0; x < 256; x++) {
      if (normalize(x) != x) continue;
      // The starting state has ALL possible values.
      start.add(x);
      lists[Integer.bitCount(x)].add(x);
    }
    int idx = 0;
    states.add(start);
    stateMap.put(start, idx++);
    for (int i = 0; i <= 8; i++) {
      int n = lists[i].size();
      // Each state could be any subset of any of our 9 values lists.
      for (int mask = 1; mask < 1 << n; mask++) {
        State state = new State();
        for (int j = 0; j < n; j++) if (((1 << j) & mask) != 0) state.add(lists[i].get(j));
        states.add(state);
        stateMap.put(state, idx++);
      }
    }
    // Store the number of states.
    ns = states.size();
  }

  static class Edge {
    // The value we guess for this edge.
    int v;
    // The state index this edge could possibly transition to (-1's should be ignored).
    int[] next = new int[9];
  }

  static class State implements Comparable<State> {
    // The list of values the judge's secret number could currently be.
    ArrayList<Integer> arr = new ArrayList<Integer>();

    // Constructs a new State for a given bit count.
    static State fromBitCount(int bitCount) {
      State state = new State();
      for (int x = 0; x < 256; x++) {
        // If this is a unique value and has the right bit count, add it.
        if (normalize(x) == x && Integer.bitCount(x) == bitCount) state.add(x);
      }
      return state;
    }

    // Returns the bit count of our state (this is valid on all but the starting state).
    int bitCount() {
      return Integer.bitCount(arr.get(0));
    }

    // Return this distance this state is from the solution state [0].
    int getDist() {
      return dists[stateMap.get(this)];
    }

    // Computes an array of all 9 possible transition states if we provided the value v.
    // Each State in the array is for that index's bit count.
    State[] next(int v) {
      State[] states = new State[9];
      for (int i = 0; i <= 8; i++) states[i] = new State();
      int w = v;
      // Consider all possible rotations of v.
      for (int r = 0; r < 8; r++) {
        // Map each current value with this rotation.
        for (int x : arr) {
          int y = x ^ w;
          // Categorize these by bit count.
          states[Integer.bitCount(y)].add(y);
        }
        w = rotate(w);
      }
      return states;
    }

    // Adds a value (but normalizes it first) to our list.
    void add(int x) {
      x = normalize(x);
      if (arr.contains(x)) return;
      arr.add(x);
      // Sort the list so we can just check equality of the lists.
      Collections.sort(arr);
    }

    public int hashCode() {
      return arr.hashCode();
    }

    // compareTo is provided to make hash collisions resolve faster.
    public int compareTo(State s) {
      int res = Integer.compare(arr.size(), s.arr.size());
      if (res != 0) return res;
      for (int i = 0; i < arr.size(); i++) {
        res = Integer.compare(arr.get(i), s.arr.get(i));
        if (res != 0) return res;
      }
      return 0;
    }

    public boolean equals(Object o) {
      if (o == null || !(o instanceof State)) return false;
      return compareTo((State) o) == 0;
    }

    public String toString() {
      String res = "[";
      for (int i = 0; i < arr.size(); i++) {
        if (i > 0) res += ", ";
        String tmp = Integer.toBinaryString(arr.get(i));
        while (tmp.length() < 8) tmp = "0" + tmp;
        res += tmp;
      }
      res += "]";
      return res;
    }
  }

  // For a given 8-bit integer x, return the minimum cyclic shift of that number.
  static int normalize(int x) {
    int min = x;
    for (int i = 0; i < 7; i++) {
      x = rotate(x);
      if (x < min) min = x;
    }
    return min;
  }

  // Cyclicly shift x by n bits
  static int rotate(int x, int n) {
    for (int i = 0; i < n; i++) x = rotate(x);
    return x;
  }

  // Cyclicly shift x one bit.
  static int rotate(int x) {
    x <<= 1;
    x |= x >> 8;
    return x & 0b11111111;
  }

  static class JudgeError extends Exception {
    public JudgeError(String message) {
      super(message);
    }
  }

  static class WrongAnswerException extends Exception {
    public WrongAnswerException(String message) {
      super(message);
    }
  }
}
