---
title: Home
---

# monitus_code

Notes, snippets and lab runs collected along the way.

<div class="grid cards" markdown>

-   :material-code-braces:{ .lg .middle } __Codes__

    ---

    Short, reusable snippets from daily work — Python, shell, and the odd
    one-liner worth keeping.

    [:octicons-arrow-right-24: Codes](codes/index.md)

-   :material-flask-outline:{ .lg .middle } __Labs__

    ---

    LLM and AI experiments, run as Jupyter notebooks with their outputs
    committed alongside.

    [:octicons-arrow-right-24: Labs](labs/index.md)

-   :material-tools:{ .lg .middle } __Tools__

    ---

    Small interactive utilities that run entirely in the browser.

    [:octicons-arrow-right-24: Token counter](tools/token_count.md)

</div>

## How it's organised

Three sections, split by *what the artifact is* rather than by language:

| Section | What belongs there | Format |
| --- | --- | --- |
| `codes/` | Snippets and notes you paste into a project | Markdown + `snippets/` includes |
| `labs/` | Runs where the output is the point | Jupyter notebooks |
| `tools/` | Interactive, browser-side utilities | Markdown + inline JS |

## Conventions

- **Pages are auto-discovered.** There is no `nav:` block: dropping a `.md` file
  into a section directory publishes it, and the nav label comes from the first
  `#` heading — or front-matter `title:` when you want to override it.
- **Code lives once.** Snippet sources sit in `snippets/`, outside `docs/`, and
  are spliced in with `--8<--`, so one fix propagates everywhere at once.
- **Notebook outputs are executed before committing**, so builds stay fast and
  hermetic, no API tokens are burned per build, and every change to output shows
  up in `git diff` for review.
