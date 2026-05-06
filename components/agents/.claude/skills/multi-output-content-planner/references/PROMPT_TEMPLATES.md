# Optimized Prompt Templates by Deliverable Type

Base prompt structure for each deliverable type. Customize based on specific scope and audience. All templates use standardized `{{PLACEHOLDER}}` syntax for easy substitution.

**Section ordering across all templates:**
1. Context & Role
2. Task
3. Output Structure
4. Constraints
5. Advanced Technique

---

## Executive Summary / Briefing Doc

**Applicable Deliverables:** Executive Briefing, Business Case, ROI Summary

**Base Prompt:**
```
## CONTEXT & ROLE

You are a business-focused technical communicator. Your role is to make complex
topics accessible to decision-makers without deep technical background.

## TASK

Create a concise executive briefing that helps busy {{AUDIENCE}} understand
{{TOPIC}} and make informed decisions about {{DECISION_POINT}}.

Success means: Reader finishes with clear understanding of {{KEY_QUESTION}}
and can decide whether to {{ACTION}}.

## OUTPUT STRUCTURE

Structure your briefing as follows:
- What is {{TOPIC}}? (2-3 sentences)
- Why This Matters (business/productivity value)
- Key Capabilities (3-4 capability areas with use cases)
- Getting Started (simple decision framework)
- Next Steps (pointer to deeper resources)

Format: Professional, clear, action-oriented. Use bold for key terms.

## CONSTRAINTS

- Do NOT include technical jargon or architecture details
- DO use business language (time savings, quality, risk, scaling)
- DO keep descriptions to 1-2 sentences per section
- Maximum {{LENGTH}} words

## ADVANCED TECHNIQUE

Use the "Executive Decision Matrix" approach:
- For each capability, explicitly state the business value
- Frame all trade-offs as risk vs. benefit
- End each section with a clear decision point or next action
```

---

## Study Guide / Comprehensive Guide

**Applicable Deliverables:** Study Guide, Technical Guide, Learning Resource

**Base Prompt:**
```
## CONTEXT & ROLE

You are an expert technical analyst specializing in {{DOMAIN}}. Your role is to
synthesize diverse source materials into a comprehensive, coherent learning resource.

## TASK

Create a comprehensive study guide that synthesizes patterns, concepts, and lessons
across all {{SOURCE_COUNT}} sources. The guide should provide deep analysis showing
{{KEY_RELATIONSHIPS}}.

Success means: A {{TARGET_USER}} can understand {{CORE_OBJECTIVE}}—what each capability
does, how they relate, and when to use each pattern.

## OUTPUT STRUCTURE

Structure into topic-based sections:
1. Introduction (context and learning objectives)
2. {{TOPIC_1}} (definition, patterns, use cases)
3. {{TOPIC_2}} (definition, patterns, use cases)
...
N. Summary (synthesized insights and key takeaways)

Format: Use markdown headers, bullet points, and "Key Takeaway" boxes.
Format cross-references as [Topic Name - Source #X: "Title"]

## CONSTRAINTS

- Do NOT speculate beyond source material
- DO cite which sources support each claim
- DO identify common themes across sources
- DO explain relationships between concepts
- Preserve depth—this is comprehensive, not summarized

## ADVANCED TECHNIQUE - Chain-of-Thought Synthesis

For each major pattern, explain using four steps:
1. Identify the pattern (what concept appears across sources?)
2. Show evidence (which sources demonstrate this?)
3. Explain the connection (how does this enable other concepts?)
4. State the insight (what does this tell us about design philosophy?)
```

---

## Slide Deck / Presentation

**Applicable Deliverables:** Slide Deck, Presentation, Visual Narrative

**Base Prompt:**
```
## CONTEXT & ROLE

You are a strategic communicator creating a presentation for {{AUDIENCE}}.
Your role is to make a compelling, visual case for {{VALUE_PROPOSITION}}.

## TASK

Create a professional slide deck that helps {{AUDIENCE}} understand
{{KEY_UNDERSTANDING}} and {{DESIRED_OUTCOME}}.

Each slide should be diagram-heavy with minimal text, driving conversation
rather than standing alone.

## OUTPUT STRUCTURE

Slide progression:
1. Title: {{MAIN_MESSAGE}}
2. The Problem: {{CHALLENGE_DESCRIPTION}}
3. The Solution: {{SOLUTION_OVERVIEW}}
4. {{CAPABILITY_AREAS}}: {{PROGRESSION_VISUAL}}
5. Real-World Impact: {{CONCRETE_EXAMPLES}}
6. Quantified Value: {{METRICS}}
7. Implementation Path: {{TIMELINE}}
8. Comparison: {{VS_ALTERNATIVES}}
9. Getting Started: {{NEXT_STEPS}}
10. Closing: {{CALL_TO_ACTION}}

## CONSTRAINTS

- Maximum 2 lines of text per slide—use visuals instead
- Do NOT use technical jargon
- DO include quantified metrics (time saved, quality improvements, cost)
- DO use business language (time savings, scaling, quality)

## ADVANCED TECHNIQUE - Visual Design Principles

- Use icons and diagrams instead of bullet points
- Use arrows to show progression and relationships
- Use consistent colors (same color per category across all slides)
- Keep text large and visible
- One high-impact visual per slide
```

---

## Infographic / Visual Overview

**Applicable Deliverables:** Infographic, Visual Ecosystem Map, Diagram

**Base Prompt:**
```
## CONTEXT & ROLE

You are a visual information designer. Your role is to make {{TOPIC}} immediately
understandable through visual hierarchy and relationships.

## TASK

Create a single-page infographic showing {{TOPIC}} as {{VISUAL_STRUCTURE}}.
The graphic should answer: "{{KEY_QUESTION_1}}?" and "{{KEY_QUESTION_2}}?"

Success means: A {{READER_TYPE}} can glance at the infographic and immediately
understand {{CORE_UNDERSTANDING}}.

## OUTPUT STRUCTURE

Visual architecture: {{STRUCTURE_DESCRIPTION}}

For each layer/section, include:
1. Clear label (3-4 words max)
2. Distinctive icon
3. Key capability (1-2 words)
4. Concrete use case example
5. Visual complexity indicator

Information hierarchy:
1. Most prominent: {{PRIMARY_VISUAL_ELEMENT}}
2. Secondary: {{SECONDARY_INFORMATION}}
3. Tertiary: {{SUPPORTING_DETAILS}}

Output: Single page, {{ORIENTATION}} orientation. Color scheme: {{COLORS}}.
Design for printing and digital sharing.

## CONSTRAINTS

- Do NOT include technical implementation details
- Do NOT use jargon or complex terminology
- DO use business/user language
- DO show relationships with visual connectors (arrows, nesting)
- Do NOT crowd the design—clarity over completeness

## ADVANCED TECHNIQUE - Information Hierarchy

Use nested/concentric visual structure to show relationships:
- Center: Core concept
- Inner layers: Direct relationships
- Outer layers: Supporting details
- Use color gradients to show progression or importance
- Use size variation to indicate significance
```

---

## Video Overview / Tutorial

**Applicable Deliverables:** Video Explainer, Narrated Walkthrough, Educational Video

**Base Prompt:**
```
## CONTEXT & ROLE

You are a {{FACILITATOR_TYPE}} synthesizing {{SOURCE_COUNT}} sources on {{TOPIC}}.
Your role is to {{CREATE_PERSPECTIVE}}.

## TASK

Create {{VIDEO_TYPE}} that {{OBJECTIVE}}.

Success means: Viewers finish with clear understanding of {{CORE_MESSAGE}}
and can {{VIEWER_OUTCOME}}.

## OUTPUT STRUCTURE

Structure:
{{CUSTOM_STRUCTURE_DETAILS}}

Target duration: {{DURATION}}
Tone: {{TONE_DESCRIPTION}}
Visual style: {{VISUAL_STYLE}}

## CONSTRAINTS

- Do NOT speculate beyond source material
- DO maintain narrative flow throughout
- DO cite sources when making claims
- DO use clear, accessible language
- DO break complex ideas into digestible segments

## ADVANCED TECHNIQUE - Narrative Storytelling

Frame your explanation as a story with:
1. Hook (why should viewer care?)
2. Context (what's the landscape?)
3. Challenge (what problem are we solving?)
4. Solution progression (step-by-step explanation)
5. Impact (why this matters and what's next)
```

---

## Interactive / Quiz / Assessment

**Applicable Deliverables:** Quiz, Assessment Tool, Knowledge Check, Flashcards

**Base Prompt:**
```
## CONTEXT & ROLE

You are an educational assessment designer. Your role is to create tools that
verify understanding of {{TOPIC}} across different knowledge levels.

## TASK

Create {{ASSESSMENT_TYPE}} with {{QUESTION_COUNT}} questions covering:
1. {{CONCEPT_1}} (foundational understanding)
2. {{CONCEPT_2}} (application)
3. {{CONCEPT_3}} (synthesis)

Success means: Assessments accurately measure {{LEARNING_OBJECTIVE}} and identify
knowledge gaps in {{TARGET_AUDIENCE}}.

## OUTPUT STRUCTURE

Question types:
- Multiple choice (foundational understanding)
- Short answer (application of concepts)
- Scenario-based (synthesis and transfer)

For each question:
- Clear, unambiguous wording
- Plausible but distinct answer options
- Correct answer with brief explanation of why
- {{DIFFICULTY}} progression from easier to harder

## CONSTRAINTS

- Questions should be clear and unambiguous
- Options should be plausible but distinct
- Avoid trick questions; focus on genuine understanding
- Avoid ambiguous language or cultural assumptions
- Ensure difficulty progression throughout

## ADVANCED TECHNIQUE - Bloom's Taxonomy Alignment

Structure questions to test increasing cognitive levels:
- Foundational: Recall, define, identify (basic memory)
- Application: Apply, analyze, compare (using knowledge)
- Synthesis: Evaluate, create, synthesize (creating new understanding)

Use scenario-based questions for higher-order thinking.
```

---

## How to Use These Templates

1. **Select the appropriate template** based on your deliverable type
2. **Replace all `{{PLACEHOLDER}}` tokens** with your specific context:
   - `{{AUDIENCE}}` = your target audience
   - `{{TOPIC}}` = the main subject
   - `{{SOURCE_COUNT}}` = number of sources
   - etc.
3. **Customize constraints** for your specific context
4. **Pass the completed prompt** to NotebookLM as the `custom_prompt` parameter

### Example Completed Prompt (Executive Summary)

```
## CONTEXT & ROLE

You are a business-focused technical communicator. Your role is to make complex
topics accessible to decision-makers without deep technical background.

## TASK

Create a concise executive briefing that helps busy engineering leaders understand
Claude agent capabilities and make implementation decisions.

Success means: A CTO finishes with clear understanding of "When should we
adopt agent teams vs sub-agents?" and can decide whether to pilot agents.

## OUTPUT STRUCTURE

Structure your briefing as follows:
- What are Claude agents? (2-3 sentences)
- Why This Matters (business/productivity value)
- Key Capabilities (agent autonomy, planning, tool use, reasoning)
- Getting Started (simple go/no-go decision framework)
- Next Steps (link to detailed technical guide)

Format: Professional, clear, action-oriented. Use bold for key terms.

## CONSTRAINTS

- Do NOT include implementation details or API information
- DO use business language (speed to market, quality, reduced manual work)
- DO keep descriptions to 1-2 sentences per section
- Maximum 1,200 words

## ADVANCED TECHNIQUE

Use the "Executive Decision Matrix" approach:
- For each capability, explicitly state the business value
- Frame all trade-offs as risk vs. benefit
- End each section with a clear decision point or next action
```

---

## Placeholder Reference

**Common placeholders used across all templates:**

| Placeholder | Description | Example |
|---|---|---|
| `{{AUDIENCE}}` | Target reader type | "engineering leaders", "product managers" |
| `{{TOPIC}}` | Main subject | "Claude agents", "distributed systems" |
| `{{SOURCE_COUNT}}` | Number of sources | "15", "20 research papers" |
| `{{KEY_QUESTION}}` | Central question to answer | "Should we adopt this technology?" |
| `{{LENGTH}}` | Word/page limit | "1,500 words", "5 pages" |
| `{{TARGET_USER}}` | Specific end user | "senior engineer", "product manager" |
| `{{CORE_OBJECTIVE}}` | Learning or decision goal | "understand patterns for system design" |
| `{{DURATION}}` | Video/content length | "8-10 minutes", "30 seconds" |
| `{{OUTCOME}}` | Desired result | "can implement a solution" |
| `{{CONSTRAINT}}` | Specific limitation | "no code examples", "visual only" |

---

## Tips for Template Customization

1. **Be specific in placeholders** — "engineering leaders deciding on adoption" beats "engineers"
2. **Match constraints to audience** — C-level content has "no jargon"; technical content cites sources
3. **Test placeholder coverage** — After filling in all placeholders, read the prompt as a complete sentence
4. **Preserve section order** — All templates follow: Context & Role → Task → Output → Constraints → Advanced Technique
5. **Maintain tone consistency** — If your audience is academic, use academic language throughout
