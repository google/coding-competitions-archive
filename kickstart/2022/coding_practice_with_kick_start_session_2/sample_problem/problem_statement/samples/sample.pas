var
	T, N: longint;
	C: array[1..100000] of longint;
	M: longint;
	sum: int64;
	i, j: longint;
begin
	readln(T);
	for i := 1 to t do
	begin
		readln(N, M);
		for j := 1 to N do
		begin
			read(C[j]);
		end;
		sum := 0;
		for j := 1 to N do
		begin
			sum := sum + C[j];
		end;
		writeln('Case #', i, ': ', sum mod M);
	end;
end.
