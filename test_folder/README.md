## Testing

A minimal [**batch script**](tests.cmd) exists to help verify the behavior across multiple permutations of parameters. To do the test-run execute:

```
tests.cmd
```

This captures and gives outputs of `listall.py` against expected results using the basic `comp.exe` feature built-in to most versions of Windows. If the results come back as `Files Compare OK` the tests pass.