# Diagram 1 — System Architecture

Everything runs as a single process on the student's own machine (`localhost`) — no cloud hosting, no third-party identity provider, no external LLM API.

```mermaid
flowchart TB
    subgraph Client["Student's Browser"]
        UI[Jinja2 pages + htmx + vanilla JS]
    end

    subgraph Backend["FastAPI Backend (localhost)"]
        Auth[auth: signup / login / session]
        Projects[projects: create / open / delete / switch]
        Search[search: idea -> ranked papers]
        Resources[resources: save / list / delete, scoped to project]
        Citations[citations: APA / MLA / Chicago / IEEE / BibTeX]
        Outlines[outlines: RAG generation read-only / copy / export]
        Ext[external: Semantic Scholar + CrossRef clients]
        LLM[llm: Ollama client]
    end

    DB[(SQLite\napp.db)]
    Ollama[[Ollama\nlocalhost:11434\nnomic-embed-text + llama3.2:3b]]
    SS[[Semantic Scholar API]]
    CR[[CrossRef API]]

    UI <--> Auth
    UI <--> Projects
    UI <--> Search
    UI <--> Resources
    UI <--> Outlines

    Auth <--> DB
    Projects <--> DB
    Resources <--> DB
    Outlines <--> DB

    Projects -. scopes .-> Resources
    Projects -. scopes .-> Outlines

    Search --> Ext
    Ext --> SS
    Ext --> CR

    Search --> LLM
    Resources --> LLM
    Outlines --> LLM
    LLM <--> Ollama

    Resources --> Citations
    Outlines --> Citations
```

**Trust boundary**: only `Ext` (Semantic Scholar/CrossRef) crosses the machine boundary, and it only ever sends the search query text — never account data, saved-library content, or generated outline text. Auth, storage, and the LLM stay entirely local.

**Scoping**: every `Resources` and `Outlines` row carries a `project_id`; `Projects` is the boundary that keeps different assignments from mixing (BL-32–BL-35). Deleting a project cascades to both.
