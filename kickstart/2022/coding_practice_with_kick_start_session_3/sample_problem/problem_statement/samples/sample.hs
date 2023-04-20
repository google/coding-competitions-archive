import Control.Monad (forM_)

test :: IO ()
test = do
    -- Read integers N and M from the standard input.
    ~[n, m] <- map read . words <$> getLine
    -- Read N integers from the standard input into a list C.
    c <- map read . words <$> getLine
    -- Compute the value of the sum of the values of C modulo M.
    let modulo = mod (sum c) m
    -- Print the result onto the standard output.
    print modulo

main :: IO ()
main = do
    -- Read the number of test cases.
    t <- readLn
    -- Loop over the number of test cases.
    forM_ [1..t] $ \test_no -> do
        -- Print case number
        putStr $ "Case #" ++ show test_no ++ ": "
        -- and solve each test.
        test

