t = gets.to_i
1.upto(t) do |ti|
    n, m = gets.split(" ").map(&:to_i)
    c = gets.split(" ").map(&:to_i)
    sum = 0
    c.each do |ci|
        sum += ci
    end
    modulo = sum % m
    puts "Case ##{ti}: #{modulo}"
end
