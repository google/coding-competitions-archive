import static cocolib.CustomJudgeInterface.judgeError;
import static cocolib.CustomJudgeInterface.wrongAnswer;

import cocolib.CustomJudgeInterface;
import cocolib.JudgeErrorException;
import cocolib.Reader;
import cocolib.WrongAnswerException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

public final class SlideParadeCustomJudge
    implements CustomJudgeInterface<SlideParadeCustomJudge.Input, SlideParadeCustomJudge.Output> {
  static final int MAX_ALLOWED_STEPS = 1000000;

  static class Edge {
    int from;
    int to;

    Edge(int from, int to) {
      this.from = from;
      this.to = to;
    }

    @Override
    public boolean equals(Object o) {
      if (this == o) {
        return true;
      }
      if (!(o instanceof Edge)) {
        return false;
      }
      Edge edge = (Edge) o;
      return from == edge.from && to == edge.to;
    }

    @Override
    public int hashCode() {
      return Objects.hash(from, to);
    }
  }

  static class Input {
    int numBuildings;
    List<Edge> edges;

    Input(int numBuildings, List<Edge> edges) {
      this.numBuildings = numBuildings;
      this.edges = edges;
    }

    @Override
    public boolean equals(Object o) {
      if (this == o) {
        return true;
      }
      if (!(o instanceof Input)) {
        return false;
      }
      Input input = (Input) o;
      return numBuildings == input.numBuildings && Objects.equals(edges, input.edges);
    }

    @Override
    public int hashCode() {
      return Objects.hash(numBuildings, edges);
    }
  }

  static class Output {
    boolean isPossible;
    List<Integer> steps;

    Output(boolean isPossible, List<Integer> steps) {
      this.isPossible = isPossible;
      this.steps = steps;
    }

    static Output possibleCase(List<Integer> steps) {
      return new Output(true, steps);
    }

    static Output impossibleCase() {
      return new Output(false, null);
    }

    @Override
    public boolean equals(Object o) {
      if (this == o) {
        return true;
      }
      if (!(o instanceof Output)) {
        return false;
      }
      Output output = (Output) o;
      return isPossible == output.isPossible && Objects.equals(steps, output.steps);
    }

    @Override
    public int hashCode() {
      return Objects.hash(isPossible, steps);
    }
  }

  public static void main(String[] args) {
    new SlideParadeCustomJudge().runCustomJudgeMultipleCases(args);
  }

  @Override
  public Input readCaseInput(Reader reader) throws IOException {
    int numBuildings = reader.readInt();
    int numEdges = reader.readInt();
    List<Edge> edges = new ArrayList<>();
    for (int i = 0; i < numEdges; i++) {
      int from = reader.readInt();
      int to = reader.readInt();
      edges.add(new Edge(from, to));
    }
    return new Input(numBuildings, edges);
  }

  @Override
  public void judgeCase(Input input, Output judgeOutput, Output contestantOutput)
      throws WrongAnswerException, JudgeErrorException {
    if (!judgeOutput.isPossible) {
      if (!contestantOutput.isPossible) {
        return;
      }
      if (areStepsValid(input, contestantOutput)) {
        judgeError("Got a valid path from contestant's output while expecting case is impossible");
      }
      wrongAnswer("Case is impossible, but answer was given");
    }
    if (!areStepsValid(input, judgeOutput)) {
      judgeError("Path in judge's output is invalid");
    }
    if (!contestantOutput.isPossible) {
      wrongAnswer("Declared impossible, but case is possible");
    }
    verifySteps(input, contestantOutput);
  }

  @Override
  public Output readCaseOutput(Input input, Reader reader)
      throws IOException, WrongAnswerException {
    String token = reader.readString();
    if (token.equalsIgnoreCase("IMPOSSIBLE")) {
      return Output.impossibleCase();
    }

    int numSteps = 0;
    try {
      numSteps = Integer.parseInt(token);
    } catch (NumberFormatException e) {
      wrongAnswer("Unable to parse the number of buildings in the path");
    }

    List<Integer> steps = new ArrayList<>();
    if (numSteps <= 0 || numSteps > MAX_ALLOWED_STEPS + 1) {
      wrongAnswer(
          "Expected the number of buildings in the path to be in range [%d, %d] but was %d",
          1, MAX_ALLOWED_STEPS + 1, numSteps);
    }

    for (int i = 0; i < numSteps; ++i) {
      steps.add(reader.readInt());
    }
    return Output.possibleCase(steps);
  }

  @Override
  public void verifyCaseOutput(Input input, Output output) throws WrongAnswerException {
    if (!output.isPossible) {
      return;
    }
    for (int step : output.steps) {
      if (step <= 0 || step > input.numBuildings) {
        wrongAnswer(
            "Expected building ID to be in range [%d, %d] but was %d", 1, input.numBuildings, step);
      }
    }

    Set<Edge> edges = new HashSet<>();
    edges.addAll(input.edges);
    for (int i = 0; i + 1 < output.steps.size(); ++i) {
      if (!edges.contains(new Edge(output.steps.get(i), output.steps.get(i + 1)))) {
        wrongAnswer(
            "Invalid step with a slide between %d and %d",
            output.steps.get(i), output.steps.get(i + 1));
      }
    }
  }

  static void verifySteps(Input input, Output output) throws WrongAnswerException {
    if (output.steps.get(0) != 1 || output.steps.get(output.steps.size() - 1) != 1) {
      wrongAnswer("Not start and end at building 1");
    }

    Set<Edge> traversedEdges = new HashSet<>();
    int[] nodeCount = new int[input.numBuildings];
    for (int i = 0; i + 1 < output.steps.size(); ++i) {
      traversedEdges.add(new Edge(output.steps.get(i), output.steps.get(i + 1)));
      ++nodeCount[output.steps.get(i) - 1];
    }

    for (int i = 1; i < input.numBuildings; ++i) {
      if (nodeCount[i] != nodeCount[0]) {
        wrongAnswer("Not all buildings visited equally");
      }
    }

    for (Edge edge : input.edges) {
      if (!traversedEdges.contains(edge)) {
        wrongAnswer("Not all slides used");
      }
    }
  }

  static boolean areStepsValid(Input input, Output output) {
    try {
      verifySteps(input, output);
      return true;
    } catch (WrongAnswerException e) {
      return false;
    }
  }
}
