# Specification: Consistent Tag Taxonomy Assimilation

## 1. Context & Problem Statement
The personal digital garden at [arunsr.in](https://www.arunsr.in) currently contains 87 notes and section documents. Over time, frontmatter tags accumulated without a central taxonomy, resulting in:
- **Massive umbrella tags**: `books` (34 pages), `tech` (28 pages), `games` (10 pages), `research` (10 pages), `non-fiction` (7 pages), `intro` (5 pages). These mirror directory structures and add no discriminatory value to related notes or search.
- **Widespread singletons**: 65 tags appearing on only a single page (e.g. `ansible`, `docker`, `kubernetes`, `python`, `powershell`, `cryptography`, `about`, `home`). Singletons cannot establish connections between notes.
- **Noise in downstream systems**: `layouts/partials/related-notes.html` had to hardcode `$umbrellaTags` blacklists to avoid showing every book as related to every other book.

## 2. Author Decisions (Phase 1 Interview)
1. **Directory-Hierarchy Tags Stripped**: Remove pure directory tags (`books`, `tech`, `games`, `research`, `intro`, `non-fiction`). Retain meaningful domain/genre tags like `science` (10 pages) and `fiction` (9 pages).
2. **Singleton Assimilation & Pruning**:
   - Singletons that map directly into an existing multi-page topic cluster are assimilated (e.g. `historical` -> `history`, `cryptocurrencies` -> `finance`, `economics` -> `politics`, `language` -> `writing`, `automation`/`cloud` -> `devops`, `editors`/`emacs`/`browsers` -> `tools`, `stoicism`/`ethics`/`logic` -> `philosophy`, `neuroscience` -> `psychology`, `astronomy`/`evolution` -> `science`).
   - Singletons that do not fit into an existing 2+ page cluster are pruned (e.g. self-naming tool names like `docker`, `ansible`, `kafka`, `openssl`, individual game genres on section hubs, etc.).
3. **Meta & Root Pages**: Remove tags entirely from root and meta pages (`_index.md`, `about.md`). Section index pages only retain tags if they share a multi-page cross-cutting topic with child notes (e.g. `books/fiction/sci-fi/_index.md` and `games/sci-fi-cyberpunk/_index.md` share `sci-fi`; `books/fiction/fantasy/_index.md` and `games/fantasy-myth/_index.md` share `fantasy`).

## 3. Strict Taxonomy Guardrails
- **Min Frequency**: Every tag must appear on at least 2 pages (`frequency >= 2`). Zero singletons allowed anywhere on the site.
- **Max Frequency**: Every tag must appear on at most 10 pages (`frequency <= 10`). Zero umbrella tags allowed.
- **Casing & Format**: All tags are strictly lowercase alphanumeric with optional hyphens (e.g. `sci-fi`, `devops`).
- **Sacred Prose Compliance (Rule 9)**: Under no circumstances may any body text, prose, review commentary, or note content be modified. Only YAML frontmatter `tags: [...]` is edited.

## 4. Target Taxonomy (32 Tags)
| Tag | Target Count | Description / Domain |
|---|---|---|
| `science` | 10 | Scientific literature, biology, physics, medicine, epistemology |
| `fiction` | 9 | Fiction books, literary works, classics, genre fiction |
| `devops` | 8 | Infrastructure, CI/CD, automation, cloud tooling, containers |
| `sysadmin` | 7 | Systems administration, Linux internals, networking, OS |
| `programming` | 6 | Software development, programming languages, coding practices |
| `philosophy` | 5 | Stoicism, ethics, logic, philosophical inquiries |
| `tools` | 5 | Developer utilities, editors, browsers, productivity tooling |
| `history` | 4 | Historical events, historical fiction, media histories |
| `linux` | 4 | Linux kernel, package management, systemd, distributions |
| `media` | 4 | News media analysis, journalism, advertising, television/film |
| `people` | 4 | Intellectual biographies, notable figures (Chomsky, Dawkins, Sagan, Stallman) |
| `psychology` | 4 | Human cognition, habits, happiness, flow, mental models |
| `security` | 4 | Cryptography, network security, privacy, OpenSSL |
| `literary` | 3 | Literary fiction, stylistic analysis, Nabokov |
| `math` | 3 | Mathematics, proofs, numerical philosophy |
| `medicine` | 3 | Immunology, anaesthesia, epidemiology |
| `monitoring` | 3 | Observability, metrics, alerting (Grafana, Prometheus, Elastic) |
| `politics` | 3 | Political theory, capitalism, systemic analysis, Chomsky |
| `productivity` | 3 | Deep work, time management, active vs passive hobbies, flow |
| `writing` | 3 | Craft of writing, punctuation, reading methodologies |
| `climate` | 2 | Climate science, global warming discourse |
| `containers` | 2 | Docker, container orchestration, Kubernetes |
| `data` | 2 | Distributed data streams, database architectures |
| `databases` | 2 | Relational and document databases, indexing |
| `environment` | 2 | Ecology, environmentalism |
| `fantasy` | 2 | Fantasy literature and fantasy gaming |
| `finance` | 2 | Economics, accounting, cryptocurrencies |
| `gaming` | 2 | Gaming culture, console gaming, interactive experiences |
| `nabokov` | 2 | Vladimir Nabokov works and analysis (Despair, Pale Fire) |
| `reading` | 2 | Literature appreciation, reading habits |
| `sci-fi` | 2 | Science fiction books and cyberpunk gaming |
| `windows` | 2 | Windows OS, PowerShell scripting |

## 5. Downstream Integration
- `layouts/partials/related-notes.html`: The `$umbrellaTags` blacklist can be streamlined or kept as defense-in-depth. Since `books`, `tech`, `games`, `research`, and `intro` are completely purged from all markdown files, spurious cross-matches are physically impossible.
- `layouts/index.json`: Client search index will be significantly leaner, cleaner, and more precise.

## 6. Verification & Automated Tests
A dedicated regression test script `scripts/test_tags.py` must be added:
1. Validates all frontmatter tags across `home/**/*.md`.
2. Asserts `count >= 2` for all tags (zero singletons).
3. Asserts `count <= 10` for all tags (zero umbrellas).
4. Asserts no prohibited directory tags (`books`, `tech`, `games`, `research`, `intro`, `non-fiction`, `about`, `home`).
5. Asserts valid tag format (lowercase, no spaces, no special characters other than `-`).
6. Enforces UTF-8 stdout reconfiguration and dynamic CI parity per Rules 10-12.
