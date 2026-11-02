---
title: Other useful tools online
---

# Online resources

## Articles

- [ChunkerLite](https://chunker.veristamp.in/): A visualized chunking dashboard
- [Contextual retrieval in AI system](https://www.anthropic.com/research/contextual-retrieval)


## Videos

- [Karpathy's Method] (https://www.youtube.com/watch?v=7zZy1QTvokM)
  
??? "Summary"
    In the video **"Stop Prompting Claude. Use Karpathy's Method Instead"** ([http://www.youtube.com/watch?v=7zZy1QTvokM](http://www.youtube.com/watch?v=7zZy1QTvokM)), host Austin Marchese breaks down a framework based on Andrej Karpathy's methodology for using AI agents effectively.

    The core takeaway is that AI models struggle with non-measurable context. Relying on simple, high-level prompting or default "plan modes" often fails because models make blind assumptions. Instead, Karpathy's framework relies on a **three-layer architecture** centered on human understanding and direction:

    ---

    ### Layer 1: The Spec (Blueprint)

    [[00:27](https://www.youtube.com/watch?v=7zZy1QTvokM&t=27)] – [[03:22](https://www.youtube.com/watch?v=7zZy1QTvokM&t=202)]

    * **The Problem:** AI lacks real-world contextual reasoning (e.g., asking AI whether to walk or drive to a car wash 50 meters away; models often suggest walking because of the short distance, missing the key context that you need the car there).
    * **The Solution:** Deliver detailed understanding to the AI using an agile, tightly-scoped specification.
    * **Key Steps:**
    1. **Uncover the Goal:** Have Claude interview you to extract the underlying decision or intent behind a task.
    2. **Work Agile (Not Waterfall):** Break large tasks into small, compartmentalized buckets with frequent checkpoints rather than giving everything at once.
    3. **Precision & Verification:** Require explicit verification on key decisions to prevent the AI from making unwanted assumptions.



    ---

    ### Layer 2: The Verifier (Quality Control)

    [[03:32](https://www.youtube.com/watch?v=7zZy1QTvokM&t=212)] – [[08:12](https://www.youtube.com/watch?v=7zZy1QTvokM&t=492)]

    * **Mental Model (Animals vs. Ghosts / Robot Librarians):** AI doesn't have intrinsic motivation ("animals"); it operates like a statistical simulation ("ghost") or a robot librarian that can only draw from its existing books and may confidently hallucinate missing context. Yelling or asking it vaguely to "make this better" doesn't work.
    * **Key Steps:**
    1. **Set Up Front Criteria:** Define exact rules for what high quality looks like before building (e.g., specific section constraints).
    2. **Use a Second AI Model as a Critic:** Use another model (e.g., running Codex alongside Claude Code) to review and cross-check outputs.
    3. **Pull External Signals:** Ground verification with live data or external context (e.g., deployment status checks or historical baseline documents).



    ---

    ### Layer 3: The Environment (The Workshop)

    [[08:47](https://www.youtube.com/watch?v=7zZy1QTvokM&t=527)] – [[12:37](https://www.youtube.com/watch?v=7zZy1QTvokM&t=757)]

    * **Build a Compounding System:** Avoid starting from a blank chat canvas every time.
    * **Key Steps:**
    1. **Optimize your `CLAUDE.md` file:** Automatically inject workspace rules, repo architecture, custom skills, and mandatory multi-step verification checks.
    2. **Curate an LLM Knowledge Base:** Store ingested data in structured machine-readable folders so context is easily reachable.
    3. **Develop Custom Reusable Skills:** Build step-by-step handbooks/routines for repetitive tasks and refine them over time.
    4. **Enforce Hard Guardrails:** Use tool-level pre-hooks (e.g., pre-tool-use hooks) for critical files ("never touch/edit") rather than soft text prompts. Group actions into *Always Do*, *Ask First*, and *Never Do*.



    ---

    > **The Big Takeaway:** [[12:46](https://www.youtube.com/watch?v=7zZy1QTvokM&t=766)]
    > As AI intelligence becomes cheaper, Karpathy emphasizes: *"You can outsource your thinking, but you can't outsource your understanding."* Success comes down to your high-level strategic direction and your ability to build feedback loops around the AI.