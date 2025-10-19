# nse-sma-rsi-scanner Constitution

Purpose
- Create a reproducible, transparent, and testable pipeline that fetches NSE historical prices and identifies equities matching the SMA(20)/SMA(50) + RSI(14) setups described in the user's Zerodha guide. Outputs should be human- and machine-readable (CSV/JSON) and suitable for manual review and watchlist creation.

Scope
- Inputs: daily OHLCV for a configurable universe of NSE equities (watchlists or full list).
- Outputs: a daily candidate list with metrics, reasons, and scores; debug artifacts; optional HTML snapshot for review.
- Non-goals: automated trading, investment advice, paid data provisioning.

Core Principles
- Reproducible: given the same raw data and parameters, the pipeline produces identical results.
- Transparent: every candidate must include the rule triggers and the data used to compute them.
- Minimal external secrets: secrets (API keys) are only accepted from environment variables and not stored in the repo.
- Small, testable units: indicator computation and detection logic are separated into pure functions with unit tests.
- Fail-safe: pipeline must not perform external actions (orders); it only reads and writes local outputs unless explicitly configured.

Data Policy
- Raw data: stored under data/raw/YYYY-MM-DD/<SYMBOL>.csv and treated as immutable.
- Derived data: stored under data/derived/YYYY-MM-DD/<SYMBOL>.parquet or equivalent.
- Retention: default keep 365 days of daily data; full-history optional with user opt-in.
- Validation: incoming data is validated for completeness and trading-day continuity; symbols with insufficient history (default 60 trading days) are skipped and logged.

Security & Secrets
- Credentials must be provided via environment variables (e.g., NSE_API_KEY). No secrets are committed.
- Enforce HTTPS for remote pulls. Optionally allow a `--skip-tls` flag for local testing with explicit warnings.

Testing & Quality
- Unit tests for indicator calculations (SMA, RSI), edge cases, and detection rules.
- Integration tests using small fixtures that represent common scenarios (pullback, breakout, insufficient data).
- Linting and format checks in CI; type hints recommended (Python).

Observability
- Every run writes a run-report summary (outputs count, candidates count, processing time, failures) to outputs/reports/YYYY-MM-DD.
- Failures and skipped symbols are logged; persistent metrics tracked in a small run-metadata file.

Acceptance Criteria
- Pipeline processes the configured universe and produces candidate output with at least 95% coverage on symbols with available data.
- Each candidate row contains the required metrics (close, sma20, sma50, rsi14, vol_avg20, score) and a reason_tags array.
- Unit tests for core logic pass in CI.

Ethics & Disclaimer
- All generated outputs include: "This tool provides screening signals for research and educational purposes only. Not financial advice."

---

## Architecture Plan

Overview
- A small, modular pipeline will fetch and validate OHLCV data, compute indicators, detect SMA+RSI setups (pullback and breakout), score candidates, and export results as CSV/JSON and optional HTML snapshot.

Components
- Config: `config.yml` to declare universe (watchlists), source priorities, parameters (SMA/RSI settings), thresholds, schedule, output paths.
- Data Fetcher: fetches daily OHLCV from configured sources with retry/backoff and caching. Supports multiple sources and a priority/fallback chain.
- Normalizer & Validator: canonicalize source fields to OHLCV, ensure trading-day continuity, check min history length.
- Indicator Engine: compute SMA(20), SMA(50), RSI(14), vol_avg20 and any helper metrics. Choose Wilder's smoothing for RSI by default (configurable).
- Signal Detector: implement rules for Uptrend, Pullback, Breakout, Volume confirmation, and Tagging.
- Scoring Engine: weighted rubric to score and rank candidates; outputs 0-100 score and reason tags.
- Output Writer: writes CSV and JSON to outputs/candidates/YYYY-MM-DD/*.csv/.json, stores debug snippets, and creates run reports.
- CLI & Scheduler: commands for `fetch`, `compute`, `scan`, `export`, and `serve-dashboard`. Schedule with cron/GitHub Actions (default run 16:00 IST daily).

Data storage layout (suggested)
- data/raw/YYYY-MM-DD/<SYMBOL>.csv
- data/derived/YYYY-MM-DD/<SYMBOL>.parquet
- outputs/candidates/YYYY-MM-DD/candidates.csv
- outputs/candidates/YYYY-MM-DD/candidates.json
- outputs/reports/YYYY-MM-DD/report.txt
- config/config.yml

Detection Rules (summary)
- Uptrend: close > sma20 and close > sma50 and sma20 > sma50
- RSI: rsi14 ∈ [40, 70]
- Pullback: price touched/within tolerance of sma20 within last 5 trading days and then bounced; volume on bounce >= 1.2× avg20
- Breakout: current close >= highest close of last 20 trading days; rsi increased and >50; volume >= 1.2× avg20

Scoring (example weights)
- Uptrend confirmation: 30
- RSI quality: 0–20
- Pullback/breakout quality: 0–20
- Volume confirmation: 0–20
- Liquidity/penalty: -0–10

Operational notes
- Run after market close (default 16:00 IST). Use retry/backoff on fetch failures.
- Provide clear run reports and a `last-successful-run` file.
- Keep tests small and fast for CI.

Next steps
- Define exact detection pseudocode and parameter defaults.
- Add unit/integration test definitions and fixtures.
- Implement minimal POC to fetch, compute, and scan a small watchlist.

# [PROJECT_NAME] Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### [PRINCIPLE_1_NAME]
<!-- Example: I. Library-First -->
[PRINCIPLE_1_DESCRIPTION]
<!-- Example: Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries -->

### [PRINCIPLE_2_NAME]
<!-- Example: II. CLI Interface -->
[PRINCIPLE_2_DESCRIPTION]
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats -->

### [PRINCIPLE_3_NAME]
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- Example: TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->

### [PRINCIPLE_4_NAME]
<!-- Example: IV. Integration Testing -->
[PRINCIPLE_4_DESCRIPTION]
<!-- Example: Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas -->

### [PRINCIPLE_5_NAME]
<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
[PRINCIPLE_5_DESCRIPTION]
<!-- Example: Text I/O ensures debuggability; Structured logging required; Or: MAJOR.MINOR.BUILD format; Or: Start simple, YAGNI principles -->

## [SECTION_2_NAME]
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->

[SECTION_2_CONTENT]
<!-- Example: Technology stack requirements, compliance standards, deployment policies, etc. -->

## [SECTION_3_NAME]
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

[SECTION_3_CONTENT]
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

[GOVERNANCE_RULES]
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
