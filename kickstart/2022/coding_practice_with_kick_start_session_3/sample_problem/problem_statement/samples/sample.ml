let solve n m c =
  (* Calculate the total number of candies *)
  let total = Array.fold_left (+) 0 c in
  (* Calculate and return the division remainder *)
  total mod m

let main =
  (* Read the number of tests *)
  let t = Scanf.scanf "%d" (fun t -> t) in
  (* For each test *)
  for test = 1 to t do
    (* Read the number of bags and kids *)
    let n, m = Scanf.scanf " %d %d" (fun n m -> n, m) in
    (* Read the number of candies per bag *)
    let c = Array.init n (fun _ -> Scanf.scanf " %d" (fun h -> h)) in
    (* Solve the task *)
    let result = solve n m c in
    (* Print the result *)
    Printf.printf "Case #%d: %d\n" test result
  done

