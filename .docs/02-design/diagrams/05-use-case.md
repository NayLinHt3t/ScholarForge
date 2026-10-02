# Diagram 5 — Use-Case / User-Story Map (D2)

```mermaid
flowchart LR
    Student(("👤\nStudent"))

    subgraph SF["ScholarForge"]
        direction TB

        subgraph acct["Account & Session"]
            a1(["Sign up"])
            a2(["Log in"])
            a3(["Log out"])
            a4(["Delete account"])
        end

        subgraph proj["Projects"]
            p1(["Create project"])
            p2(["Open / switch project"])
            p3(["Delete project"])
        end

        subgraph disc["Paper Discovery  ★ core"]
            d1(["Search papers by idea"])
            d2(["Browse ranked result cards"])
            d3(["Save paper to project library"])
            d4(["Remove paper from library"])
        end

        subgraph cite["Citations"]
            c1(["View auto-formatted citation\nAPA · MLA · IEEE"])
            c2(["Switch citation style"])
        end

        subgraph gen["Outline Generation"]
            g1(["Generate outline scaffold"])
            g2(["Regenerate one section"])
        end

        subgraph exp["Review & Export"]
            e1(["Copy section to clipboard"])
            e2(["Copy full outline"])
            e3(["Download PDF  (labeled DRAFT)"])
            e4(["Download Markdown"])
        end
    end

    Student --> a1
    Student --> a2
    Student --> a3
    Student --> a4

    Student --> p1
    Student --> p2
    Student --> p3

    Student --> d1
    Student --> d2
    Student --> d3
    Student --> d4

    Student --> c1
    Student --> c2

    Student --> g1
    Student --> g2

    Student --> e1
    Student --> e2
    Student --> e3
    Student --> e4
```

**One actor** — the entire product serves a single human role (Student). No admin, no supervisor, no compliance officer interacts with the app directly; compliance obligations (CCA §26 logging, PDPA deletion) are met by system behaviour, not a separate actor.

**★ core** marks the Paper Discovery group — the feature the audit confirmed as build-first, and the one all other groups depend on (you need saved papers before you can cite, generate, or export anything).
