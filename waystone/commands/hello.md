---
description: Test if agents can write files
allowed-tools: Task
---

Invoke the hello-world agent:

```
Task(
  subagent_type="waystone:hello-world",
  prompt="Create .audit/hello-world.md with HI in it"
)
```

After it completes, check if `.audit/hello-world.md` exists and contains "HI".
