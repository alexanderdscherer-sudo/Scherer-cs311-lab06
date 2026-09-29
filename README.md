# Lab 6: The Threaded Buffer

Public template: https://github.com/cwillpinto/cs311-lab06-threaded-buffer

Full assignment: `Lab_06_The_Threaded_Buffer.md`.

## Run
```bash
python run_buffer_sim.py
```
Fix the `OrderQueue` class only -- do not touch anything under the
"SIMULATOR + VERIFICATION SUITE" line. The script runs 20 trials of
50 producers / 10 consumers and checks for crashes and lost/duplicated
orders. Success Token prints only if all 20 trials pass.

Note: the buggy starter includes a deliberate `time.sleep(0)` inside
`dequeue`'s check-then-act sequence. That's intentional, not a second
bug to remove -- see the class docstring. Without it, CPython's GIL
makes a single `list.append`/`list.pop` call atomic enough that the
race rarely shows up in a short run; the sleep(0) widens the window so
the bug is reliably observable (confirmed empirically: 20/20 trials
crash unfixed, 20/20 pass once properly locked).

## Submit
1. `Lab6_Theory.pdf` (or `.md`)
2. `run_buffer_sim.py`
3. The Success Token
