---
description: Test if agents can write files
allowed-tools: Task, Bash
---

First, get the absolute working directory with `pwd`.

Then invoke the hello-world agent with the ABSOLUTE path:

```
Task(
  subagent_type="waystone:hello-world",
  prompt="Create [ABSOLUTE_PATH]/.audit/hello-world.md with the text HI. Use the Write tool with the full absolute path."
)
```

After it completes, run `cat [ABSOLUTE_PATH]/.audit/hello-world.md` to verify.
