T = io.read("*number")
for ti = 1, T do
    N, M = io.read("*number", "*number")
    C = {}
    for ci = 0, N-1 do
        C[ci] = io.read("*number")
    end
    sum = 0
    for ci = 0, N-1 do
        sum = sum + C[ci]
    end
    modulo = sum % M
    print("Case #"..ti..": "..modulo)
    ti = ti + 1
end
