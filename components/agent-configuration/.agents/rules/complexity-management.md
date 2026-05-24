# Complexity Management

## Prompt Optimisation
When crafting prompts for downstream agents, tools, or models, always consider optimising before dispatching.

**Offer to optimise when:**
- The user's request will be sent to a downstream model or search tool where phrasing affects output quality
- The request is ambiguous or underspecified for the target tool
- A well-crafted prompt would meaningfully improve precision or reduce iterations

**Optimisation techniques:**
- **Rephrase for precision** — Replace vague terms with specific ones ("improve performance" → "reduce p99 latency below 200ms for the `/search` endpoint")
- **Add role context** — "You are an expert in X" primes the model for the right frame of reference
- **Specify output format** — "Return a JSON array of objects with keys: name, type, description"
- **Add constraints** — Length limits, required sections, forbidden approaches, tone requirements
- **Use targeted keywords** — For search queries, include domain-specific vocabulary that improves recall precision
- **Chain-of-thought priming** — "Think step by step before answering" for complex reasoning tasks

**When to optimise silently vs. offer it:** For agent-to-agent calls, optimise silently and proceed. When preparing a prompt on behalf of the user (e.g. a query for a search skill or an external API), show the optimised version and get approval before dispatching.

## 4D Methodology
Apply the 4D process whenever input is complex, ambiguous, multi-layered, or structurally disorganised.

**Trigger conditions — apply 4D when:**
- A single request contains multiple interlinked tasks or concepts
- The input contains inconsistent or contradictory information
- Output requirements or success criteria are unclear
- The input is structurally messy (unformatted text, mixed concerns, implicit dependencies)
- Misinterpreting intent would be costly or hard to reverse

**The 4D Process:**

### 1. Deconstruct
Extract the signal from the noise before doing anything.
- Identify the **core intent**: what outcome does the user actually want?
- List key entities, actors, and constraints
- Separate what is explicitly provided from what needs to be inferred or requested
- Define the output requirements: what does "done" look like?

### 2. Diagnose
Audit the input for quality issues before proceeding.
- **Ambiguity** — Where could this be interpreted multiple ways?
- **Incompleteness** — What required information is missing?
- **Inconsistency** — Do any statements contradict each other?
- **Structural complexity** — Is this a flat list, a set of nested dependencies, or a workflow with sequencing constraints?

### 3. Develop
Select the technique that matches the request type:

| Request type | Technique |
|---|---|
| Creative | Multi-perspective generation + tone/voice emphasis |
| Technical | Constraint-based decomposition + precision focus |
| Educational | Few-shot examples + clearly scaffolded structure |
| Complex reasoning | Chain-of-thought + systematic frameworks (pros/cons, decision matrix) |
| Ambiguous | Clarify via AskUserQuestion before proceeding |

### 4. Deliver
Construct the response with intentional structure.
- Format based on complexity: simple → prose; structured → headers + bullets; complex → sections with sub-structure
- Lead with the most important information, not the preamble
- Separate *what* from *why* from *how* when all three are present
- If you decomposed a messy input, show the structure you imposed — it lets the user verify your interpretation before you act on it
