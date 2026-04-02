Before doing anything, work through Boyd's OODA loop on the task at hand. Do not write code until all four steps are complete.

## Observe
Read the relevant code, logs, errors, and state. Gather facts. What is actually happening right now? What does the user see? Quote specifics — file paths, line numbers, error messages, actual behavior vs expected.

## Orient
Why is it happening? What assumptions might be wrong? What has been tried before — check git log for prior attempts. How does this fit into the broader system? Are there adjacent things that will break? This is the most important step — take your time here.

## Decide
State the fix or approach in plain language before touching code. If there are multiple options, list tradeoffs. If the diagnosis is uncertain, say so — better to ask than to guess. Keep scope tight: what is the minimum change that resolves the issue?

## Act
Now implement. One thing at a time. Test after each change.

---

Apply this to: $ARGUMENTS
