# Design System — ScholarForge

> Derived from spec, backlog, and the reference UI (ResearchHub screenshot).
> Stack: Jinja2 templates · vanilla CSS (custom properties) · htmx · no JS framework.
> Two breakpoints: **mobile** (`< 768 px`) and **web** (`≥ 768 px`).

---

## 1. Color Tokens

```css
:root {
  /* --- Brand --- */
  --color-primary:        #2563EB;   /* blue-600  — primary actions, active nav */
  --color-primary-hover:  #1D4ED8;   /* blue-700 */
  --color-primary-light:  #EFF6FF;   /* blue-50   — hover state bg, tag highlight */

  /* --- Surface --- */
  --color-bg:             #F8FAFC;   /* slate-50  — page background */
  --color-surface:        #FFFFFF;   /* card, panel, input background */
  --color-sidebar:        #0F172A;   /* slate-900 — web sidebar */
  --color-sidebar-hover:  #1E293B;   /* slate-800 */
  --color-sidebar-active: #1E3A8A;   /* blue-900  — active nav item bg */

  /* --- Border --- */
  --color-border:         #E2E8F0;   /* slate-200 */
  --color-border-focus:   #2563EB;

  /* --- Text --- */
  --color-text-primary:   #0F172A;   /* slate-900 */
  --color-text-secondary: #475569;   /* slate-600 */
  --color-text-muted:     #94A3B8;   /* slate-400 */
  --color-text-inverse:   #F8FAFC;   /* on dark sidebar */
  --color-text-link:      #2563EB;

  /* --- Semantic --- */
  --color-success:        #16A34A;   /* green-600 */
  --color-success-bg:     #F0FDF4;
  --color-warning:        #D97706;   /* amber-600 */
  --color-warning-bg:     #FFFBEB;
  --color-error:          #DC2626;   /* red-600 */
  --color-error-bg:       #FEF2F2;
  --color-info:           #0284C7;   /* sky-600 */
  --color-info-bg:        #F0F9FF;

  /* --- Tag chips --- */
  --color-tag-bg:         #F1F5F9;   /* slate-100 */
  --color-tag-text:       #475569;   /* slate-600 */
  --color-tag-border:     #CBD5E1;   /* slate-300 */

  /* --- Highlight (highly cited badge) --- */
  --color-highlight:      #F59E0B;   /* amber-400 */
}
```

---

## 2. Typography

```css
:root {
  --font-family: 'Inter', system-ui, -apple-system, sans-serif;

  /* Scale */
  --text-xs:   0.75rem;   /* 12px — captions, timestamps */
  --text-sm:   0.875rem;  /* 14px — body, tags, secondary actions */
  --text-base: 1rem;      /* 16px — default body */
  --text-lg:   1.125rem;  /* 18px — card title */
  --text-xl:   1.25rem;   /* 20px — section heading */
  --text-2xl:  1.5rem;    /* 24px — page heading */

  /* Weight */
  --font-normal:    400;
  --font-medium:    500;
  --font-semibold:  600;
  --font-bold:      700;

  /* Line height */
  --leading-tight:  1.25;
  --leading-snug:   1.375;
  --leading-normal: 1.5;
  --leading-relaxed:1.625;
}

body {
  font-family: var(--font-family);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
  color: var(--color-text-primary);
  background: var(--color-bg);
}
```

---

## 3. Spacing & Sizing

```css
:root {
  /* 4 px base grid */
  --sp-1:   0.25rem;   /*  4px */
  --sp-2:   0.5rem;    /*  8px */
  --sp-3:   0.75rem;   /* 12px */
  --sp-4:   1rem;      /* 16px */
  --sp-5:   1.25rem;   /* 20px */
  --sp-6:   1.5rem;    /* 24px */
  --sp-8:   2rem;      /* 32px */
  --sp-10:  2.5rem;    /* 40px */
  --sp-12:  3rem;      /* 48px */

  /* Border radius */
  --radius-sm:   0.25rem;   /* 4px  — tags */
  --radius-md:   0.5rem;    /* 8px  — inputs, cards */
  --radius-lg:   0.75rem;   /* 12px — panels */
  --radius-full: 9999px;    /* pills */

  /* Shadows */
  --shadow-sm:  0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md:  0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.05);
  --shadow-lg:  0 10px 15px -3px rgb(0 0 0 / 0.08), 0 4px 6px -4px rgb(0 0 0 / 0.05);

  /* Layout */
  --sidebar-width:      240px;
  --right-panel-width:  340px;
  --topbar-height:       56px;
  --bottom-nav-height:   60px;
  --content-max-width:  860px;
}
```

---

## 4. Layout

### 4.1 Web (≥ 768 px) — 3-column shell

```
┌─────────────────────────────────────────────────────────┐
│  SIDEBAR (240px fixed)  │  MAIN CONTENT  │  RIGHT PANEL │
│                         │  (flex 1)      │  (340px)     │
│  Logo                   │                │              │
│  ─────────              │  [page body]   │  [context    │
│  Search Papers  ←active │                │   panel]     │
│  Generate       │       │                │              │
│  My Library     │       │                │  shown only  │
│  Projects       │       │                │  on Search + │
│  Settings       │       │                │  Outline     │
│  ─────────      │       │                │  screens     │
│  [project badge]│       │                │              │
│  [user row]     │       │                │              │
└─────────────────────────────────────────────────────────┘
```

```css
.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  min-height: 100vh;
}

/* Right panel present on search + outline screens */
.app-shell.has-panel {
  grid-template-columns: var(--sidebar-width) 1fr var(--right-panel-width);
}

.main-content {
  padding: var(--sp-6);
  overflow-y: auto;
}

.right-panel {
  border-left: 1px solid var(--color-border);
  padding: var(--sp-6);
  overflow-y: auto;
  background: var(--color-surface);
}
```

### 4.2 Mobile (< 768 px) — single column + bottom nav

```
┌──────────────────────┐
│  TOP BAR             │  ← logo + project badge + avatar
│  [page title]        │
├──────────────────────┤
│                      │
│   MAIN CONTENT       │
│                      │
│                      │
├──────────────────────┤
│ 🔍  📚  ➕  📄  ⚙️  │  ← bottom nav (60px)
└──────────────────────┘
```

```css
@media (max-width: 767px) {
  .app-shell,
  .app-shell.has-panel {
    display: block;
  }

  .sidebar { display: none; }
  .right-panel {
    border-left: none;
    border-top: 1px solid var(--color-border);
    width: 100%;
  }

  .main-content {
    padding: var(--sp-4);
    padding-bottom: calc(var(--bottom-nav-height) + var(--sp-4));
  }
}
```

---

## 5. Components

### 5.1 Sidebar (web)

```css
.sidebar {
  width: var(--sidebar-width);
  background: var(--color-sidebar);
  color: var(--color-text-inverse);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0;
  height: 100vh;
  padding: var(--sp-4) 0;
  z-index: 50;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding: 0 var(--sp-4) var(--sp-6);
  font-size: var(--text-base);
  font-weight: var(--font-bold);
  color: var(--color-text-inverse);
}

.sidebar-logo .tagline {
  font-size: var(--text-xs);
  font-weight: var(--font-normal);
  color: var(--color-text-muted);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding: var(--sp-3) var(--sp-4);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: #94A3B8;                      /* slate-400 */
  border-radius: var(--radius-md);
  margin: 0 var(--sp-2);
  text-decoration: none;
  transition: background 150ms, color 150ms;
  cursor: pointer;
}

.nav-item:hover {
  background: var(--color-sidebar-hover);
  color: var(--color-text-inverse);
}

.nav-item.active {
  background: var(--color-sidebar-active);
  color: var(--color-text-inverse);
}

.nav-item svg { width: 18px; height: 18px; flex-shrink: 0; }

/* Active project badge at bottom of nav list */
.project-badge {
  margin: var(--sp-4) var(--sp-4) 0;
  padding: var(--sp-3);
  background: var(--color-sidebar-hover);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  color: #94A3B8;
}

.project-badge .project-name {
  font-weight: var(--font-semibold);
  color: var(--color-text-inverse);
  font-size: var(--text-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* User row */
.sidebar-user {
  margin-top: auto;
  padding: var(--sp-4);
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  border-top: 1px solid #1E293B;
}

.avatar {
  width: 32px; height: 32px;
  border-radius: var(--radius-full);
  background: var(--color-primary);
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  flex-shrink: 0;
}
```

### 5.2 Top Bar (mobile)

```css
.topbar {
  height: var(--topbar-height);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--sp-4);
  position: sticky;
  top: 0;
  z-index: 40;
}

.topbar-logo {
  font-weight: var(--font-bold);
  font-size: var(--text-base);
  color: var(--color-primary);
}

/* Active project pill in topbar */
.project-pill {
  background: var(--color-primary-light);
  color: var(--color-primary);
  padding: var(--sp-1) var(--sp-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

### 5.3 Bottom Navigation (mobile)

```css
.bottom-nav {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  height: var(--bottom-nav-height);
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  display: flex;
  z-index: 40;
}

.bottom-nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  font-size: 10px;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color 150ms;
}

.bottom-nav-item.active { color: var(--color-primary); }
.bottom-nav-item svg { width: 22px; height: 22px; }
```

### 5.4 Search Bar

```css
.search-bar {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  margin-bottom: var(--sp-5);
}

.search-input-wrap {
  flex: 1;
  position: relative;
}

.search-input-wrap svg.icon-search {
  position: absolute;
  left: var(--sp-3);
  top: 50%; transform: translateY(-50%);
  width: 16px; height: 16px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: var(--sp-3) var(--sp-10) var(--sp-3) var(--sp-8);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  box-shadow: var(--shadow-sm);
  transition: border-color 150ms, box-shadow 150ms;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-border-focus);
  box-shadow: 0 0 0 3px rgb(37 99 235 / 0.1);
}

.search-input::placeholder { color: var(--color-text-muted); }

/* Clear button inside input */
.search-clear {
  position: absolute;
  right: var(--sp-3);
  top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer;
  color: var(--color-text-muted);
  padding: 0;
  display: flex; align-items: center;
}
```

### 5.5 Buttons

```css
/* Base */
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-2) var(--sp-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  line-height: 1;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background 150ms, color 150ms, border-color 150ms, box-shadow 150ms;
  text-decoration: none;
  white-space: nowrap;
}

.btn svg { width: 15px; height: 15px; }

/* Primary — main CTA (Search, Generate outline) */
.btn-primary {
  background: var(--color-primary);
  color: white;
}
.btn-primary:hover { background: var(--color-primary-hover); }

/* Full-width primary (Generate Paper panel) */
.btn-primary-full {
  width: 100%;
  justify-content: center;
  padding: var(--sp-3) var(--sp-4);
  font-size: var(--text-base);
}

/* Secondary — outlined */
.btn-secondary {
  background: var(--color-surface);
  color: var(--color-text-primary);
  border-color: var(--color-border);
  box-shadow: var(--shadow-sm);
}
.btn-secondary:hover { background: var(--color-bg); }

/* Ghost — no border, icon actions (PDF, Save, Copy) */
.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
  padding: var(--sp-2) var(--sp-3);
}
.btn-ghost:hover {
  background: var(--color-bg);
  color: var(--color-text-primary);
}

/* Danger */
.btn-danger {
  background: var(--color-error-bg);
  color: var(--color-error);
  border-color: #FECACA;
}
.btn-danger:hover { background: #FEE2E2; }

/* Disabled state */
.btn:disabled, .btn[aria-disabled="true"] {
  opacity: 0.45;
  cursor: not-allowed;
  pointer-events: none;
}

/* Size modifier */
.btn-sm { padding: var(--sp-1) var(--sp-3); font-size: var(--text-xs); }
.btn-lg { padding: var(--sp-3) var(--sp-6); font-size: var(--text-base); }
```

### 5.6 Tag Chip

Used on paper cards (keyword tags), filter pills.

```css
.tag {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-1);
  padding: var(--sp-1) var(--sp-3);
  background: var(--color-tag-bg);
  color: var(--color-tag-text);
  border: 1px solid var(--color-tag-border);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  white-space: nowrap;
}

/* Active filter chip (pressed state) */
.tag.active {
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-color: #BFDBFE;
}
```

### 5.7 Paper Result Card

```css
.paper-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--sp-5) var(--sp-6);
  display: grid;
  grid-template-columns: 1fr auto;
  gap: var(--sp-4);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 150ms;
}

.paper-card:hover { box-shadow: var(--shadow-md); }

/* Mobile: single column */
@media (max-width: 767px) {
  .paper-card { grid-template-columns: 1fr; }
  .paper-card-thumbnail { display: none; }
}

/* Left column */
.paper-card-body { min-width: 0; }

.paper-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-1);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-highlight);
  margin-bottom: var(--sp-2);
}

.paper-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  line-height: var(--leading-snug);
  margin-bottom: var(--sp-1);
  cursor: pointer;
}
.paper-title:hover { color: var(--color-primary); }

.paper-meta {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--sp-3);
}
/* · separator between authors, year, venue */
.paper-meta span + span::before {
  content: ' · ';
  color: var(--color-text-muted);
}

.paper-abstract {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--sp-3);
  /* 3-line clamp */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.paper-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sp-2);
  margin-bottom: var(--sp-4);
}

.paper-actions {
  display: flex;
  align-items: center;
  gap: var(--sp-1);
}

/* Right column: thumbnail */
.paper-card-thumbnail {
  width: 88px;
  height: 88px;
  border-radius: var(--radius-md);
  object-fit: cover;
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  flex-shrink: 0;
  align-self: start;
}

/* "Already saved" state */
.paper-card.is-saved {
  border-color: #BBFBCE;
  background: #F0FDF4;
}
```

### 5.8 Library Resource Row

```css
.library-item {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--sp-4) var(--sp-5);
  display: flex;
  align-items: flex-start;
  gap: var(--sp-4);
}

.library-item-num {
  width: 24px;
  height: 24px;
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.library-item-body { flex: 1; min-width: 0; }

.citation-text {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  font-family: 'Georgia', serif;    /* matches citation formatting convention */
}

.library-item-actions {
  display: flex;
  gap: var(--sp-1);
  flex-shrink: 0;
}
```

### 5.9 Outline Section Card

```css
.outline-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-bottom: var(--sp-4);
}

.outline-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--sp-4) var(--sp-5);
  border-bottom: 1px solid var(--color-border);
}

.outline-section-title {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.outline-section-actions { display: flex; gap: var(--sp-2); }

.outline-section-body {
  padding: var(--sp-4) var(--sp-5);
}

/* Bullet ideas */
.outline-section-body ul {
  padding-left: var(--sp-5);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--sp-4);
}

/* Draft prose passage */
.draft-passage {
  background: var(--color-bg);
  border-left: 3px solid var(--color-primary);
  padding: var(--sp-3) var(--sp-4);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
}

.draft-passage-label {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-warning);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--sp-2);
}

/* Read-only guard — no pointer on text content */
.outline-section-body * { user-select: text; cursor: default; }
```

### 5.10 Form Inputs & Selects

```css
.form-group { display: flex; flex-direction: column; gap: var(--sp-1); }

.form-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: var(--sp-2) var(--sp-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-family: inherit;
  color: var(--color-text-primary);
  background: var(--color-surface);
  box-shadow: var(--shadow-sm);
  transition: border-color 150ms, box-shadow 150ms;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-border-focus);
  box-shadow: 0 0 0 3px rgb(37 99 235 / 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 96px;
  line-height: var(--leading-relaxed);
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%2394A3B8' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14L2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right var(--sp-3) center;
  padding-right: var(--sp-8);
}

/* Two-column select grid (Choose Settings panel) */
.form-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-3);
}

@media (max-width: 767px) {
  .form-grid-2 { grid-template-columns: 1fr; }
}
```

### 5.11 Panel / Card Container

Used for the right-hand "Generate outline" panel and modal dialogs.

```css
.panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: var(--sp-4);
  padding: var(--sp-4) var(--sp-5);
  border-bottom: 1px solid var(--color-border);
}

.panel-tab {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-2) 0;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-muted);
  border-bottom: 2px solid transparent;
  cursor: pointer;
  text-decoration: none;
}

.panel-tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.panel-body {
  padding: var(--sp-5);
  display: flex;
  flex-direction: column;
  gap: var(--sp-5);
}

.panel-step-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--sp-3);
}
```

### 5.12 Alert / Error Banner

```css
.alert {
  display: flex;
  align-items: flex-start;
  gap: var(--sp-3);
  padding: var(--sp-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
}

.alert svg { width: 18px; height: 18px; flex-shrink: 0; margin-top: 1px; }

.alert-error   { background: var(--color-error-bg);   color: var(--color-error);   border: 1px solid #FECACA; }
.alert-warning { background: var(--color-warning-bg); color: var(--color-warning); border: 1px solid #FDE68A; }
.alert-success { background: var(--color-success-bg); color: var(--color-success); border: 1px solid #BBF7D0; }
.alert-info    { background: var(--color-info-bg);    color: var(--color-info);    border: 1px solid #BAE6FD; }

/* Ollama-specific error (GENC-FR-02 / BL-21) */
.alert-ollama-error::after {
  content: '';
  /* icon + message set in HTML */
}
```

### 5.13 Empty State

```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--sp-12) var(--sp-6);
  gap: var(--sp-4);
}

.empty-state-icon {
  width: 48px; height: 48px;
  color: var(--color-text-muted);
}

.empty-state-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.empty-state-body {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  max-width: 320px;
}
```

### 5.14 Project Card (My Projects screen)

```css
.project-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--sp-5);
  display: flex;
  align-items: center;
  gap: var(--sp-4);
  box-shadow: var(--shadow-sm);
  transition: box-shadow 150ms;
  cursor: pointer;
}

.project-card:hover { box-shadow: var(--shadow-md); }

.project-card-icon {
  width: 40px; height: 40px;
  border-radius: var(--radius-md);
  background: var(--color-primary-light);
  display: flex; align-items: center; justify-content: center;
  color: var(--color-primary);
  flex-shrink: 0;
}

.project-card-body { flex: 1; min-width: 0; }

.project-card-name {
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-card-meta {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: var(--sp-1);
}
```

### 5.15 Recent Item Row (right panel)

```css
.recent-item {
  display: flex;
  align-items: flex-start;
  gap: var(--sp-3);
  padding: var(--sp-3) 0;
  border-bottom: 1px solid var(--color-border);
}
.recent-item:last-child { border-bottom: none; }

.recent-item-icon {
  color: var(--color-primary);
  flex-shrink: 0;
  margin-top: 2px;
}

.recent-item-body { flex: 1; min-width: 0; }

.recent-item-title {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recent-item-meta {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: 2px;
}

.recent-item-menu {
  color: var(--color-text-muted);
  flex-shrink: 0;
  cursor: pointer;
}
```

### 5.16 Loading / Skeleton State

```css
@keyframes shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}

.skeleton {
  background: linear-gradient(90deg, #E2E8F0 25%, #F1F5F9 50%, #E2E8F0 75%);
  background-size: 800px 100%;
  animation: shimmer 1.4s ease-in-out infinite;
  border-radius: var(--radius-sm);
}

.skeleton-text  { height: 14px; width: 100%; }
.skeleton-title { height: 20px; width: 70%; }
.skeleton-card  { height: 120px; border-radius: var(--radius-lg); }
```

### 5.17 Modal / Confirmation Dialog

Used for delete-project and delete-account confirmations (BL-34, BL-39 require explicit confirmation step).

```css
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgb(0 0 0 / 0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
  padding: var(--sp-4);
}

.modal {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 420px;
  padding: var(--sp-6);
}

.modal-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  margin-bottom: var(--sp-3);
}

.modal-body {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--sp-5);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--sp-3);
}
```

---

## 6. htmx Interaction Patterns

```html
<!-- Search: submit on Enter, swap results into #results -->
<form hx-post="/projects/{{project_id}}/search"
      hx-target="#results"
      hx-swap="innerHTML"
      hx-indicator="#search-spinner">
  <div class="search-input-wrap">
    <svg class="icon-search">…</svg>
    <input class="search-input" name="idea" placeholder="Describe your research idea…">
  </div>
  <button class="btn btn-primary" type="submit">Search</button>
</form>

<!-- Save paper: swap just the button to show "Already saved" -->
<button class="btn btn-ghost"
        hx-post="/projects/{{project_id}}/library"
        hx-vals='{"resource_id": "{{resource.id}}"}'
        hx-swap="outerHTML"
        hx-target="this">
  Save
</button>

<!-- Remove from library: remove the row on success -->
<button class="btn btn-ghost"
        hx-delete="/projects/{{project_id}}/library/{{resource.id}}"
        hx-confirm="Remove this paper from the library?"
        hx-swap="outerHTML swap:300ms"
        hx-target="closest .library-item">
  Remove
</button>

<!-- Regenerate one section (BL-37): swap only that section -->
<button class="btn btn-ghost btn-sm"
        hx-post="/projects/{{project_id}}/outlines/{{outline.id}}/sections/{{n}}/regenerate"
        hx-swap="outerHTML"
        hx-target="closest .outline-section"
        hx-indicator="closest .outline-section">
  Regenerate
</button>

<!-- Citation style switcher: re-render entire library list -->
<select class="form-select"
        hx-get="/projects/{{project_id}}/library"
        hx-target="#library-list"
        hx-swap="innerHTML"
        name="style">
  <option value="ieee">IEEE</option>
  <option value="apa">APA</option>
  <option value="mla">MLA</option>
  <option value="chicago">Chicago</option>
</select>
```

---

## 7. Page-Level Templates

### 7.1 Search screen (web 3-column)

```
SIDEBAR │ [Search bar]                                    │ PANEL
        │ [Filter row: Year · Type · Relevance]           │ ─ Generate Outline ─
        │                                                  │  1. Describe idea
        │ [Paper card]                                     │     [textarea]
        │ [Paper card]                                     │  2. Choose settings
        │ [Paper card]                                     │     [4 selects]
        │ …                                               │  3. Add references
        │                                                  │     [search]
        │                                                  │ [Generate btn]
        │                                                  │ Recent outlines
```

### 7.2 Search screen (mobile)

```
[TopBar: SF logo · "Project Name" pill · avatar]
[Search bar — full width]
[Filter chips — horizontal scroll]
[Paper card]
[Paper card]
…
[Bottom nav: 🔍 Search | 📚 Library | ➕ Projects | 📄 Outline | ⚙️]
```

### 7.3 Library screen

```
SIDEBAR │ My Library — "Project Name"                      │ (no right panel)
        │ [Citation style: IEEE ▾]   [N resources]         │
        │                                                   │
        │ [1] Author. "Title."...  [Copy] [BibTeX] [✕]     │
        │ [2] Author. "Title."...  [Copy] [BibTeX] [✕]     │
        │ …                                                  │
        │                                                   │
        │ [Generate outline from this library →]            │
```

### 7.4 Outline screen

```
SIDEBAR │ 📋 Outline scaffold                              │ PANEL
        │ "Project Name"  [Copy all] [↓ PDF] [↓ MD]        │ ─ Outline info ─
        │                                                   │  Generated: 2 hrs ago
        │ ⚠ Draft banner                                   │  Resources: 5 papers
        │                                                   │  Style: IEEE
        │ [I. Introduction section card]                    │
        │   • bullet ideas                                  │  [Regenerate all]
        │   Draft passage…                                  │
        │   [Copy] [Regenerate]                             │
        │ [II. Related Work …]                              │
        │ …                                                 │
        │ [References]                                      │
```

---

## 8. Iconography

Use [Lucide Icons](https://lucide.dev) (MIT, inline SVG). Consistent 18 px stroke icons in nav; 15–16 px in buttons.

| Context | Icon name |
|---|---|
| Search Papers (nav) | `search` |
| Generate Outline (nav) | `file-pen` |
| My Library (nav) | `bookmark` |
| Projects (nav) | `folder` |
| Settings (nav) | `settings` |
| Save / Bookmark | `bookmark` / `bookmark-check` |
| Remove | `trash-2` |
| Copy | `copy` |
| Download PDF | `file-down` |
| Download Markdown | `file-text` |
| Regenerate | `refresh-cw` |
| Ollama error | `alert-circle` |
| Highly cited | `star` |
| PDF link | `file-text` |
| BibTeX | `code` |
| Add | `plus` |
| Chevron / expand | `chevron-down` |
| Duplicate blocked | `ban` |
| Success saved | `check-circle` |

---

## 9. Accessibility Baseline

- All interactive elements must have visible focus rings (the `box-shadow` ring already defined on inputs).
- Sidebar nav items use `aria-current="page"` on the active item.
- Error alerts include `role="alert"` so screen readers announce them.
- Buttons use descriptive labels; icon-only buttons require `aria-label`.
- Confirmation modals use `role="dialog"` and `aria-labelledby`.
- Color is never the sole means of communicating state (icons + text always accompany color changes).
- Minimum touch target 44 × 44 px on mobile (enforced by `min-height: 44px` on `.bottom-nav-item` and `.btn-lg`).
