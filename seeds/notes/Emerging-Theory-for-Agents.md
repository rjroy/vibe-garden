Emerging Theoretical Models of AI Agents
Introduction
Recent research is reimagining AI agent design around core computational and cognitive functions rather
than human job titles. Modern LLM-based agents and neural-symbolic systems are being structured to
leverage what AI does best (pattern recognition, language generation, rapid computation) while mitigating
weaknesses (long-term planning, factual consistency). Academic work across multi-agent systems,
cognitive architectures, autonomous reasoning, AI planning, and alignment is converging on
architectures where agents have specialized internal processes (e.g. memory management, reasoning
modules, self-monitoring) or collaborate in groups, instead of mimicking roles like “developer” or “tester.”
Key themes include epistemic delegation (delegating knowledge-related tasks or queries to specialized
components), feedback loop optimization (agents improving via self-reflection or iterative feedback),
adaptive planning (dynamic plan generation with lookahead and adjustment), deviation detection
(monitoring for errors or off-track reasoning), and abstract agent roles tied to cognitive functions. Below,
we review major emerging frameworks and models, highlighting their design principles and findings from
the academic literature.

Brain-Inspired and Modular Cognitive Architectures
One prominent direction is drawing inspiration from human cognition to create modular agent
architectures. For example, Webb et al. (2025) propose a Modular Agentic Planner (MAP) that
decomposes planning into multiple specialized LLM modules modeled after prefrontal cortex functions
  1   2 . In MAP, separate modules handle tasks like error/conflict monitoring, state prediction, state

evaluation, task decomposition, and action proposal, and a coordination module integrates these for goal-
directed planning 2 . Individually, large language models can perform many of these cognitive sub-tasks
in isolation, but they struggle to coordinate them in a single chain 3 4 . By assigning each function to an
LLM-based “expert” and having them interact, MAP yields substantially improved performance on multi-step
reasoning benchmarks (e.g. graph traversal, Tower of Hanoi) compared to a monolithic LLM agent 5 .
Notably, this brain-inspired modular design reduced hallucinated or invalid steps (the error-monitor module
catches infeasible actions) and avoided getting stuck in loops during planning 6 7 . The MAP
architecture underscores how abstract cognitive roles (like a conflict monitor or state evaluator) can replace
human job analogies, resulting in more reliable complex reasoning.

Researchers are also revisiting classical cognitive architectures in light of LLM advances. Sumers et al.
(2024) introduced Cognitive Architectures for Language Agents (CoALA) as a conceptual blueprint that
situates modern LLM agents in terms of memory, action, and decision processes 8 9 . CoALA specifies
an agent with modular memory components (analogous to working vs. long-term memory), a structured set
of internal actions (reasoning, memory recall) and external actions (tool use, environment interaction), and a
general decision-making loop that plans and executes actions 8 9 . This framework provides a taxonomy
to compare recent LLM-agent systems (many of which had been developed ad-hoc with terms like “tool use”
or “chain-of-thought”) and emphasizes the importance of internal cognitive loops. By contextualizing today’s
agents in the broader history of AI (e.g. production systems and cognitive control architectures), CoALA

                                                      1
highlights memory management and iterative planning as core to achieving more “general intelligence” in
language agents 9 .

Memory limitations of LLMs have spurred research into active memory architectures that go beyond
naive retrieval. An example is the Cognitive Workspace proposed by An (2025), which takes inspiration
from human working memory and the extended mind thesis 10 11 . Instead of relying solely on passive
retrieval-augmented generation (RAG) from a static knowledge base, Cognitive Workspace actively curates
and maintains an external memory buffer, with mechanisms for deliberate information curation and
persistence 12 13 . It introduces hierarchical “cognitive buffers” (short-term scratchpads, longer-term
stores) and a task-driven context optimizer that decides what information to keep or discard based on current
goals 12 14 . This resembles how humans use notepads or diagrams as extensions of thought. Empirical
results show such an active memory system can reuse information far more effectively – e.g. achieving ~58%
memory reuse where standard RAG achieved 0% – leading to net efficiency gains despite overhead 15 . The
design includes a form of metacognitive control to prevent context overflow, addressing LLMs’ tendency
to forget earlier details or get distracted. Overall, brain-inspired and modular architectures like MAP, CoALA,
and Cognitive Workspace illustrate a trend: splitting an agent’s cognition into specialized, interacting parts
(planners, evaluators, memory buffers, etc.) yields more robust and scalable problem-solving than a single
LLM prompt. These modules correspond to computational functions (state modeling, error checking,
memory management) that map well to AI strengths, rather than human job titles.

Neural-Symbolic Integration and Cognitive Models
Another line of research seeks to integrate symbolic or cognitive reasoning structures with neural
networks (LLMs) – creating neural-symbolic agents that combine pattern recognition with explicit logic or
models. Wu et al. (2023) present LLM-ACTR, a framework that injects the decision-making patterns of the
ACT-R cognitive architecture into a large language model 16 17 . ACT-R (Adaptive Control of Thought—
Rational) is a well-established symbolic architecture modeling human cognition (with modules for memory,
goal-setting, etc.). In LLM-ACTR, the authors first run tasks through an ACT-R simulation to generate traces
of the cognitive steps a human might follow, then train the LLM (via adapter layers or fine-tuning) to embed
these cognitive priors into its representations 16 18 . The result is an LLM whose generative process is
guided by human-like intermediate steps (e.g. attending to relevant facts or subgoals in a structured way)
rather than solely by statistical co-occurrence. This hybrid architecture showed improved performance on
complex decision-making tasks in manufacturing settings, outperforming vanilla LLM reasoning or chain-of-
thought prompts 19 18 . By grounding the LLM’s reasoning in a symbolic framework, hallucinations and
non-sequitur jumps were reduced, as the model had to conform to ACT-R’s more disciplined flow of
retrieving facts from memory and evaluating actions 17 . LLM-ACTR exemplifies epistemic delegation within
the model: the neural network delegates part of the decision process to an internal symbolic “mentor” (the
ACT-R schema), effectively blending data-driven and rule-based approaches. This aligns with a broader
effort in neuro-symbolic AI to ensure AI agents can explain their reasoning and maintain consistency by
using symbolic structures (logic rules, knowledge graphs, planning algorithms) alongside neural nets.

Beyond ACT-R, various cognitive-computational architectures are being proposed to merge neural
learning with explicit planning and reasoning. LeCun (2022) sketched a differentiable agent architecture
with modules for perception, a predictive world model, cost evaluation (intrinsic goals), and an actor for
planning actions 20 21 . Each module corresponds to a function (e.g. predicting future states or evaluating
outcomes) that can be optimized jointly but operates semi-independently – a design echoing classic sense-
plan-act paradigms but with end-to-end learning. While LeCun’s framework is a high-level vision, it

                                                      2
reinforces the idea of factorizing agent cognition: perception filters the input, a world-model handles
epistemic reasoning about what might happen next, and a critic module detects deviations from desired
goals (analogous to deviation detection of unsafe or suboptimal states) 22 23 . Similarly, other
neurosymbolic approaches use external tools or APIs as symbolic modules guided by LLMs – for instance,
an LLM might recognize a pattern that a formal solver is needed and delegate a subtask (like solving an
equation or querying a database) to a tool, then integrate the result. This kind of epistemic delegation
harnesses the strengths of both worlds: the LLM handles open-ended pattern recognition and language
interface, while the symbolic component ensures accuracy or logical validity in its domain 24 17 . Overall,
neural-symbolic frameworks and cognitive integrations aim to give AI agents a form of “structured common
sense,” letting them abstract certain roles (planner, calculator, memory index, etc.) into distinct components.
These components correspond to the functions AI excels at or can be made to excel at (like fast recall
from a knowledge base, or exhaustive symbolic search), rather than anthropomorphic job roles. Research in
this area is showing that such combinations can produce agents that are more interpretable, reliable, and
aligned in their reasoning than purely end-to-end LLM agents.

Adaptive Planning and Self-Reflective Agents
A major challenge for autonomous AI agents is adaptive long-horizon planning – the ability to make
multi-step decisions, adjust when outcomes deviate from expectations, and learn from mistakes. Emerging
solutions often introduce an explicit feedback loop within an agent’s operation, so the agent can critique
and refine its own outputs. One example is the Reflexion framework by Shinn et al. (2023), which treats an
LLM agent’s interaction with tasks as an iterative trial-and-error process 25 26 . In Reflexion, the agent
maintains an episodic memory of its past actions and the feedback or results they yielded. After each trial (or
each significant action), the agent generates a natural language self-reflection: a commentary on what
went wrong or could be improved, based on the feedback signals it received 27 . These reflections are
stored and consulted on the next attempt, effectively letting the agent “learn” from failures without
gradient updates by updating its context rather than its weights 28 26 . For example, a coding agent that
produced a bug would receive a test failure message, generate a reflective note like “I see the error, next
time I should handle edge-case X,” and then incorporate that note into its next code generation attempt.
This self-reinforcement via language led to dramatic improvements on tasks like code generation (Reflexion
attained 91% success on the HumanEval benchmark, versus 80% for GPT-4 without self-reflection) 26 . The
key innovation is leveraging the LLM’s own capacity to evaluate and modify its reasoning – closing the
feedback loop with textual critique, which serves as an internal guide to avoid repeating mistakes. This
approach embodies both feedback optimization (continually refining output with feedback) and deviation
detection, as the agent explicitly notes when an outcome deviated from the goal and formulates a fix.

Another strategy for adaptive planning is to have the agent explore multiple solution paths in parallel and
evaluate their outcomes before committing. Yao et al. (2023) introduce the Tree-of-Thoughts (ToT)
framework, which generalizes the idea of chain-of-thought prompting into a tree-based search process 29
  30 . Instead of having the LLM generate a single stream of reasoning, ToT allows the agent to branch out

at certain points, creating a tree of possible “thoughts” or intermediate states. The agent then uses heuristic
evaluations (which are themselves generated by the LLM as reflective judgments) to decide which branch of
the tree is most promising to follow 30 31 . It can backtrack if a line of reasoning leads to a dead end, and
dynamically adjust its plan – much like a classical AI search algorithm but guided by the semantic
knowledge of an LLM. This approach reintroduces ideas from early AI (Newell and Simon’s heuristic search
in problem spaces 32 ) into the context of LLMs. Empirically, Tree-of-Thoughts enabled state-of-the-art
performance on tasks that stump greedy one-shot LLM reasoning, such as complex puzzles, math word

                                                      3
problems, or crosswords that require filling in multiple interconnected answers 33 34 . The agent’s ability
to look ahead and reason about “what if I try this approach?” via internal simulation of outcomes is a form
of adaptive planning that leverages LLMs’ strength in diverse idea generation. Importantly, ToT also
involves an internal self-evaluation mechanism: at each step, the model assesses partial solutions
(“thoughts”) for how likely they are to lead to a correct final answer 30 . This can be seen as a built-in
deviation check – if a thought appears to be leading astray (low heuristic score), the search can prune it.

Both Reflexion and Tree-of-Thoughts demonstrate how adding reflective and evaluative loops inside the
agent’s reasoning process can greatly improve reliability and performance. These methods move away from
treating the LLM as a one-pass oracle, instead making the agent an active problem-solver that can
question its own outputs. In effect, the agent takes on roles like student and teacher: it generates proposals
(student) and then critiques them (teacher), an interplay that drives learning. This is a departure from static
role-play prompts (e.g. “Coder AI” vs “Reviewer AI” as separate agents); instead, the single agent itself does
both generative and critical work in phases. The success of such techniques highlights that pattern-
recognition machines can benefit from an internalized form of pattern-mismatch detection – noticing when
current reasoning doesn’t fit the problem requirements and adjusting accordingly. This idea of self-
correction is becoming a cornerstone in theoretical models of AI agents.

Multi-Agent Systems and Epistemic Delegation
Rather than a single agent handling all aspects of cognition, researchers are also exploring multi-agent
frameworks where different agents (often LLM-driven) assume different specialized roles and collaborate.
The goal is to leverage collective intelligence – multiple agents can cross-verify each other, divide complex
tasks, and delegate subtasks to the member best suited for each. Crucially, these roles are defined by
functional expertise (e.g. information retrieval, planning, verification) rather than by human job titles. For
instance, Wang et al. (2024) propose MACRec, a multi-agent framework for recommendations that includes
agents such as a Manager, Reflector, Searcher, Analysts, and a Task Interpreter 35 . Each agent has a distinct
responsibility: the Manager plans the overall strategy and assigns subtasks, User/Item Analysts focus on
understanding user profiles or item data, the Searcher performs epistemic actions by querying external
knowledge, and the Reflector analyzes the workflow for errors or inconsistencies 35 36 . These agents
communicate in natural language to share findings and updates. By dividing the recommendation task this
way, MACRec was able to outperform single-agent approaches, especially on complex tasks that involve
nuanced judgments and long reasoning chains 37 35 . Notably, the Reflector agent in this setup embodies
deviation detection – it monitors the intermediate results for anomalies or mistakes (for example, if a
recommended item contradicts known user preferences) and feeds that back into the loop for correction.
This mirrors a human team where one member double-checks the work of others, but here it’s framed as a
cognitive function (quality assurance) rather than a mere “tester” role.

Multi-agent cooperation also facilitates epistemic delegation: an agent can ask a peer for information or
verification, rather than handling it all internally. An LLM agent that encounters a question outside its
knowledge can delegate to a specialized knowledge agent (e.g. a wiki browser or a domain-specific model),
then integrate the answer. This idea is evident in frameworks like HuggingGPT (where an LLM delegates
subtasks to various expert models) and is formalized in some multi-agent simulations. The CAMEL
framework (2023) demonstrated that two LLM-based agents could role-play as user and assistant to
iteratively solve programming tasks, implicitly delegating the creation and critique of code between them in
dialogue. The general finding is that agents with complementary skillsets can tackle problems none could
solve alone, by exchanging information and requests in natural language. Such interactions are often

                                                      4
governed by simple protocols (ask, refine, confirm), but they result in emergent problem-solving
capabilities.

In addition to cooperative roles, adversarial roles have been studied as a way to achieve higher reliability –
a concept borrowed from alignment research. AI Safety via Debate (Irving et al., 2018) is a paradigm where
two agents take on the roles of proponent and critic on a given question 38 . The proponent attempts to
convince a human judge of a certain answer, while the critic’s job is to point out flaws or counterarguments.
The human only sees the agents’ arguments and then decides which agent was more convincing/truthful.
Theoretically, if the agents are optimal, this zero-sum debate should surface the truth, because any
incorrect or deceptive argument by one agent can be highlighted by the other 38 39 . This setup abstracts
the roles of “teacher” and “student” (or “liar” and “truth-teller”) into distinct agents that incentivize the
exposure of errors. It’s another form of epistemic delegation: the human delegate’s the task of scrutinizing
an answer to an AI adversary. While debate is an alignment-motivated idea, it has inspired practical
implementations in which an agent will generate an answer and then spawn a second agent (or a second
pass of itself) to stress-test that answer with pointed questions. A related concept is iterated amplification
(Christiano et al., 2018), where a strong agent is trained by delegating tasks to a team of weaker sub-agents
recursively 40 . In that model, a question is broken down by an agent into sub-questions, which are
answered by other agents; those answers are combined and checked, emulating a hierarchy of experts. This
can be seen as an abstract organizational chart of cognitive roles: each sub-agent handles a manageable
chunk (pattern recognition in a sub-problem or simple decision), and a top-agent aggregates them –
analogous to how a manager delegates to subordinates in a company, but here the delegation is purely
epistemic (about facts and sub-solutions) and the “employees” are copies of an AI.

In summary, multi-agent theoretical models emphasize role abstraction at the system level: instead of one
giant black-box model, we have a constellation of agents each excelling at a particular function (e.g. planner
vs. critic, solver vs. verifier). These roles map to core AI competencies: searching a knowledge base,
generating creative options, monitoring consistency, etc. By allowing agents to interact (cooperatively or
adversarially), the system can self-correct and self-improve: one agent’s output is another’s input,
enabling feedback loops across agents. This collective approach addresses the key themes directly – for
example, deviation detection is naturally handled when one agent is tasked as a dedicated checker, and
epistemic exploration is enhanced when one agent can solely focus on information gathering. The research
so far suggests that carefully designed multi-agent systems can outperform single-agent systems on
complex tasks 37 , and they provide a promising path to scaling AI capabilities in a controllable way. There
is active work on formalizing these interactions (communication protocols, trust boundaries, learning
dynamics) to ensure the multi-agent system remains aligned and efficient as it grows.

Comparison of Agent Frameworks by Core Attributes
To synthesize the above findings, the following table compares selected emerging frameworks for AI
agents, highlighting their core ideas and strengths:

                                                      5
Framework
                      Key Idea/Architecture               Key Strengths/Findings
(Year)

                      Cognitive Architecture Blueprint:
                      Organizes LLM agents around         Provides a unified framework to compare/
CoALA (Sumers et      modular memory systems,             design agents; highlights memory and
al., 2024)            internal vs. external actions,      planning as core elements for language-
                      and an interactive decision loop    based general intelligence 8 9 .
                        8   9 .

                      Brain-Inspired Modular Planning:
                                                          Achieves significantly better planning (fewer
                      Multiple specialized LLM
Modular Agentic                                           hallucinations, no looping) than a single LLM;
                      modules (error monitor, state
Planner (MAP)                                             transferable across tasks and effective even
                      predictor, etc.) coordinate via a
(Webb et al., 2025)                                       with smaller LMs, due to synergistic
                      central planner to perform
                                                          specialized skills 5 .
                      multi-step reasoning 2 .

                      Active Memory System:
                      Maintains external “working         Improves long-range context handling with
Cognitive             memory” buffers and actively        ~58% memory reuse vs. 0% in passive
Workspace (An,        curates context, mimicking          retrieval systems; yields ~17% efficiency gains
2025)                 human strategies of note-           by focusing on relevant information and
                      taking and information              discarding distractions 15 .
                      offloading 12 41 .

                      Neural-Symbolic Integration:
                                                          Reduces reasoning errors and hallucinations
                      Injects patterns from the ACT-R
                                                          by grounding the LLM in a structured
                      cognitive architecture into an
LLM-ACTR (Wu et                                           cognitive process; showed improved task
                      LLM via learned adapters,
al., 2023)                                                performance and more explainable reasoning
                      aligning the LLM’s internal
                                                          compared to LLM-only chain-of-thought
                      reasoning with human-like
                                                          baselines 17 .
                      decision steps 16 17 .

                      Self-Reflective Loop: Agent uses
                                                          Enables rapid learning from mistakes without
                      linguistic feedback (from the
                                                          weight updates; demonstrated dramatic
Reflexion (Shinn      environment or self-critique) to
                                                          gains (e.g. +11% accuracy on code generation
et al., 2023)         write reflections into memory
                                                          vs. GPT-4) by iteratively correcting errors and
                      and adjust subsequent actions
                                                          refining plans in natural language 26 .
                        27 .

                      Deliberative Search: Agent
                                                          Yields stronger results on tasks requiring
                      explores a branching tree of
                                                          strategic planning (math puzzles, logic games,
                      possible thoughts (solutions),
Tree-of-Thoughts                                          crosswords) by enabling lookahead and global
                      using the LLM to evaluate and
(Yao et al., 2023)                                        search instead of linear greedy reasoning; the
                      decide which branches to
                                                          LLM’s self-evaluation serves as an on-the-fly
                      expand or prune (with
                                                          heuristic for complex problem-solving 33 34 .
                      backtracking) 30 31 .

                                                    6
  Framework
                        Key Idea/Architecture                Key Strengths/Findings
  (Year)

                        Adversarial Agents: Two agents
                                                             Theoretically can produce honest, high-fidelity
                        engage in a zero-sum debate—
                                                             answers beyond the judge’s own ability, by
                        one proposes an answer, the
  Debate (Irving et                                          leveraging competing agents to uncover
                        other critiques it—forcing the
  al., 2018)                                                 hidden flaws or deceptive reasoning; an early
                        revelation of flaws, with a
                                                             alignment strategy to ensure AI outputs stay
                        human judge deciding the
                                                             truthful under scrutiny 39 .
                        winner 38 .

                                                             Demonstrated improved performance on
                        Collaborative Specialists: A team
                                                             complex decision-making tasks
                        of LLM agents with distinct
  Multi-Agent                                                (recommendations, planning problems) by
                        functions (planner “Manager”,
  Collaboration                                              dividing cognitive labor; specialization +
                        information “Searcher”, error-
  (e.g. MACRec)                                              communication allowed handling of subtasks
                        checking “Reflector”, etc.)
  (Wang et al., 2024)                                        that overwhelmed single agents, and the
                        cooperate on tasks via
                                                             Reflector agent caught and corrected
                        communication 35 .
                                                             deviations in real time 37 35 .

Conclusion
Across these emerging theoretical models, a clear trend is the shift towards architectural modularity,
feedback-rich loops, and role abstraction grounded in computation. Rather than viewing an AI agent as
a monolithic “artificial worker,” researchers are decomposing intelligence into interoperating components –
be it internal modules for memory, planning, and error detection, or multiple agents interacting in a society.
This rethinking leverages the complementary strengths of AI systems: superhuman pattern recognition
and recall, tireless iterative optimization, and fast symbolic computation. By delegating subtasks to
specialized modules or agents, the overall system becomes more robust – for example, it can catch its own
mistakes (through a critic module or agent), adapt its plan when new information arrives (through
deliberative search or a manager agent), and maintain knowledge over long horizons (through active
memory management or epistemic actions like tool use). The inclusion of human-inspired cognitive
mechanisms (like working memory buffers, self-reflection, and conflict monitoring) and multi-agent
consensus mechanisms (like debate or cross-checking answers) is leading to agents that are not only more
capable, but also more transparent and alignable. We can trace a unifying goal in this research: to achieve
adaptive, reliable AI agents that can reason and learn in open-ended tasks, we must move beyond one-
shot prompt->response paradigms and equip agents with internal structure and interactions that mirror the
complexities of reasoning.

These theoretical frameworks are still evolving, and ongoing work is testing their limits (e.g. scaling to very
large knowledge domains, ensuring convergent behavior in multi-agent settings, and maintaining
alignment of all sub-parts with human values). Nonetheless, the progress to date – from modular LLM
planners solving puzzles they once couldn’t 5 , to reflective agents that teach themselves from mistakes
  26 , to coordinated agent teams tackling multi-faceted problems – suggests that rethinking agent design

around computational and epistemic functions is a fruitful path. By abstracting agent “roles” to things
like planner, critic, memory, or model, we tap into the intrinsic competencies of AI and open up new
possibilities for building AI agents that are both powerful and trustworthy. The convergence of ideas from

                                                      7
cognitive science, AI planning, and multi-agent systems in these models is paving the way toward more
general, robust AI agents that operate on principles very different from a simplistic human job analogy – an
exciting step toward AI that can truly complement and extend human cognitive capabilities 8 9 .

 1   2     3   4    5    6    7    A brain-inspired agentic architecture to improve planning with LLMs | Nature
Communications
https://www.nature.com/articles/s41467-025-63804-5?error=cookies_not_supported&code=c66ec69a-4dcf-4e85-
a907-0701fd4904d8

 8   9    [2309.02427] Cognitive Architectures for Language Agents
https://ar5iv.labs.arxiv.org/html/2309.02427v3

10   11   12   13   14   15   41   Cognitive Workspace: Active Memory Management for LLMs An Empirical Study of
Functional Infinite Context
https://arxiv.org/html/2508.13171v1

16   17   18   19   24   neurosymbolic-ai-journal.com
https://neurosymbolic-ai-journal.com/system/files/nai-paper-791.pdf

20   21   22   23   openreview.net
https://openreview.net/pdf?id=BZ5a1r-kVsf

25   26   27   28   [2303.11366] Reflexion: Language Agents with Verbal Reinforcement Learning
https://arxiv.org/abs/2303.11366

29   30   31   32   33   34   proceedings.neurips.cc
https://proceedings.neurips.cc/paper_files/paper/2023/file/271db9922b8d1f4dd7aaef84ed5ac703-Paper-Conference.pdf

35   36   37   Multi-Agent Collaboration Framework for Recommender Systems
https://arxiv.org/html/2402.15235v1

38   39   [1805.00899] AI safety via debate
https://ar5iv.labs.arxiv.org/html/1805.00899

40   [1810.08575] Supervising strong learners by amplifying weak experts
https://arxiv.org/abs/1810.08575

                                                              8
