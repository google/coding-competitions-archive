def reader = new Scanner(System.in)
def T = reader.nextInt();
1.upto(T) { ti ->
  def N = reader.nextInt();
  def M = reader.nextInt();
  def C = new int[N];
  for (int i = 0; i < N; i++) {
      C[i] = reader.nextInt();
  }
  def sum = 0;
  for (int i = 0; i < N; i++) {
      sum += C[i];
  }
  def modulo = sum % M;
  println("Case #" + ti + ": " + modulo)
}
