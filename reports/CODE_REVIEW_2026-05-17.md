# Code Review — DB_Security_Testing

**Date:** 2026-05-17
**Scope:** Full repository (`backend/`, `frontend/`, `data-generator/`, `install/`, Docker, docs)
**Branch reviewed:** `claude/code-review-report-2Idtk`
**Reviewer focus:** Logic errors and broken code paths (per request), plus missing tests, missing functionality, and documentation accuracy.

---

## 0. Important framing — intentional vs unintentional vulnerabilities

This is a **deliberately-vulnerable security research lab** (BU CS674). Code paths gated on `security_mode == 'vulnerable'` that skip validation, run raw SQL from the LLM, or expose PHI are **by-design** and out of scope for "fix". I have separated those into §6 ("Intentional vulnerabilities — by design").

Everything in §1–§5 is an **unintentional bug** — code that fails even on its own terms, or that breaks even the lab's "secure mode" demonstration.

---

## 1. Summary

| Severity | Count | Description |
|---|---|---|
| **Critical** | 7 | Code does not run / login is broken / secure mode silently fails |
| **High** | 14 | Wrong behavior, broken endpoints, XSS, dead "fixes", broken commands |
| **Medium** | 18 | Logic errors, mismatches, duplication risk, drift |
| **Low** | 9 | Polish, dead code, log noise |
| **Tests** | 0 | No tests of any kind exist; coverage harness present but empty |

The most damaging individual issues:

1. **`setup_database.sql:101`** — `CREATE USER healthcare_admihn` (typo), missing semicolon, GRANTs reference yet a third user. SQL execution aborts mid-script.
2. **`setup_database.sql:172–179`** — every seeded user shares the same hand-pasted bcrypt hash that does **not** verify against `password123`, so the README test accounts cannot log in if you bootstrap via SQL alone.
3. **`frontend/src/app.js:77–82`** — token-revalidation on page load POSTs to `/api/login` with `method:'GET'`. The endpoint is POST-only; verification always fails and the user is bounced to the login screen on every reload.
4. **`backend/llm_client.py:317–336`** — secure-mode "row-level filter" appends the literal string `WHERE patient_id = {user_patient_id}` to the SQL. The placeholder is never substituted; Postgres errors out and every patient query fails.
5. **`backend/database.py:213–223`** — the comment claims "CRITICAL FIX: Add query timeout enforcement to prevent DoS", but `execution_options(timeout=...)` is not a real SQLAlchemy/psycopg2 statement timeout. No timeout is actually applied; the DoS protection does not exist.
6. **`data-generator/database.py`** vs **`data-generator/config.py`** — `database.py` reads `Config.DATABASE_HOST/PORT/NAME`, `config.py` exports `DB_HOST/DB_PORT/DB_NAME`. The container raises `AttributeError` on startup.
7. **Duplicate forks of `database.py`, `models.py`, `config.py`, `generate_sample_data.py` in `/backend` and `/data-generator`** — already diverged; security fixes in one will not reach the other.

---

## 2. Critical issues

### C1. `setup_database.sql:101–103` — broken `CREATE USER` block

```sql
CREATE USER healthcare_admihn WITH PASSWORD 'Postgresql17!'   -- typo + missing ;
GRANT CONNECT ON DATABASE healthcare_security TO healthcare_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO healthcare_admin;
```

Three users named in three statements: `healthcare_admihn` (created), `healthcare_user` (granted CONNECT but not created here), `healthcare_admin` (granted ALL, also never created). Missing `;` after line 101 merges it into the next statement, causing a syntax error that aborts the rest of the file. **None of the table creation downstream of line 101 will run** if you execute the script as-is.

**Fix:**
```sql
CREATE USER healthcare_user WITH PASSWORD 'CHANGE_ME';
GRANT CONNECT ON DATABASE healthcare_security TO healthcare_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO healthcare_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO healthcare_user;
```
Move the block to *before* table creation, or to a separate role-bootstrap script.

---

### C2. `setup_database.sql:172–179` — bogus hashes, login is impossible from SQL bootstrap

All eight seeded users share the identical hash `$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewkQjl.YuqnF6C2K`. This is a copy-pasted public example hash; it does **not** hash `password123` under the bcrypt parameters this codebase uses. `bcrypt.checkpw('password123', <hash>)` returns False, so every documented "default test account" fails to authenticate if the user only ran the SQL.

The Python `generate_sample_data.py` generates a fresh hash dynamically (`bcrypt.hashpw('password123', bcrypt.gensalt())`) and works correctly. So the lab is only usable if you run `generate_sample_data.py` *after* the SQL — but the SQL inserts duplicate-username conflicts that will then fail.

**Fix:** Either (a) remove the `INSERT INTO admin_users` block from `setup_database.sql` entirely and document that `generate_sample_data.py` is the canonical seed, or (b) replace each hash with `crypt('password123', gen_salt('bf', 12))` using the `pgcrypto` extension and add `CREATE EXTENSION IF NOT EXISTS pgcrypto;` at the top.

---

### C3. `frontend/src/app.js:77–82` — token re-verification uses wrong endpoint and wrong method

```js
const response = await this.callAuthAPI('/api/login', {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${this.authToken}` }
});
```

`/api/login` is POST-only (`backend/app.py:179`). The correct endpoint is `/api/verify` (`backend/app.py:233`). Every page reload throws "HTTP 405", the catch block runs, the user is forced back to the login modal.

**Fix:**
```js
const response = await this.callAuthAPI('/api/verify', {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${this.authToken}` }
});
```

(The well-written `frontend/src/utils/api.js:87` already does this correctly — it's just dead code; see M11.)

---

### C4. `backend/llm_client.py:322–326` — placeholder never substituted in secure-mode patient queries

```python
if 'patients' in sql_query.lower() and 'where' not in sql_query.lower():
    if sql_query.endswith(';'):
        sql_query = sql_query[:-1] + ' WHERE patient_id = {user_patient_id};'
    else:
        sql_query += ' WHERE patient_id = {user_patient_id}'
```

The literal string `{user_patient_id}` is never `.format()`-substituted with the real ID, because (a) the function has no access to it and (b) no `.format()` call follows. PostgreSQL receives the literal SQL `WHERE patient_id = {user_patient_id}` and errors with `syntax error at or near "{"`.

This means secure-mode patient queries **always fail**, defeating the lab's own demonstration of the secure path.

**Fix:** Move row-level filtering out of `_apply_security_filters` and rely solely on `SecurityManager.filter_results_by_role()` (`backend/security.py:217`), which already does this correctly *after* execution using the user's `patient_id`. Delete the broken substitution. Optionally have `generate_sql` accept `user_patient_id` and use a parameterized query.

---

### C5. `backend/database.py:213–223` — fake query timeout

```python
result = conn.execute(
    text(sql_query).execution_options(timeout=Config.QUERY_TIMEOUT)
)
```

The `timeout` key on `execution_options` is not a SQLAlchemy- or psycopg2-recognized option for statement timeout. SQLAlchemy silently ignores unknown keys. The comment block above it claims a "CRITICAL FIX… to prevent DoS"; the fix does nothing. A maliciously crafted query in vulnerable mode (or any slow query in secure mode) runs without limit.

**Fix (PostgreSQL):** set the statement timeout at connection scope:
```python
with self.engine.connect() as conn:
    conn.execute(text(f"SET LOCAL statement_timeout = {Config.QUERY_TIMEOUT * 1000}"))
    result = conn.execute(text(sql_query), parameters or {})
```
or pass `options='-c statement_timeout=30000'` in the engine connect args. Add a test that asserts a deliberately-sleeping query (`SELECT pg_sleep(60)`) is aborted.

---

### C6. `data-generator/database.py` vs `data-generator/config.py` — undefined attribute access

`data-generator/database.py:40–41` reads `Config.DB_HOST`, `Config.DB_PORT`, `Config.DB_NAME`. `data-generator/config.py` defines `DATABASE_HOST/PORT/NAME` (not `DB_*`). Result: `AttributeError: type object 'Config' has no attribute 'DB_HOST'` at container startup.

**Fix:** Rename in `database.py` to match `Config.DATABASE_HOST/PORT/NAME` (consistent with the backend copy), or expose both names as aliases on the Config class.

---

### C7. Source duplication between `/backend` and `/data-generator`

Four files (`database.py`, `models.py`, `config.py`, `generate_sample_data.py`) exist in both directories with nontrivial divergence (variable naming, Docker DATABASE_URL handling, the `Omar Cox` deterministic patient, non-interactive mode detection, default LLM model). The data-generator copy contains C6 above; the backend copy contains C5. A security fix in one will not propagate.

**Fix:** Pick one. Recommended:
- Move shared code to a top-level `common/` package, install with `pip install -e .` in both Dockerfiles.
- Delete the duplicates; have data-generator import from `common.models`, `common.database`, etc.
- As a stopgap, replace the duplicates with file-system symlinks and document it.

---

## 3. High-severity issues

### H1. `backend/app.py:111, 117` — `/api/health` is logged on every request despite the filter

```python
if request.endpoint not in ['health']:
```

The route function is `health_check` (`@app.route('/api/health') def health_check`), so Flask's `request.endpoint` is `'health_check'`, not `'health'`. The filter never matches; every health probe (Docker, Kubernetes, NGINX) is logged. Fix: change `['health']` → `['health_check']`, or check `request.path == '/api/health'`.

### H2. `backend/security.py:413` + `Config.SQL_INJECTION_PATTERNS` — secure mode flags its own valid SQL

`Config.SQL_INJECTION_PATTERNS[0]` is `r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)"`. `SecurityManager._check_sql_injection_patterns` runs these against the LLM-generated SQL. **Every** valid `SELECT` statement matches, adding +2 to `risk_score` and a "SQL injection pattern detected: SELECT" warning to every secure-mode result. Combined with other warnings (e.g. UNION +3) this can push past the threshold and block legitimate queries. Fix: only run these patterns against the *natural-language question*, not against the post-LLM SQL; or scope them to suspicious contexts (e.g. comments, stacked semicolons).

### H3. `attack_scenarios.py:373–391` — `--username` / `--password` CLI args ignored

`argparse` registers `--username` and `--password` (with sensible documentation), but `main()` never passes them through to `runner.authenticate(...)`. The README documents `--username admin --password password123` (`README.md:176`) but it has no effect. Fix:
```python
runner.username = args.username
runner.password = args.password
# and in run_comprehensive_test():
if not self.authenticate(self.username, self.password): ...
```

### H4. `attack_scenarios.py` payload usernames don't exist

`AttackScenarioRunner.authenticate(...)` defaults to `test_doctor`/`password123`. That user is created by `generate_sample_data.py` but **not** by `setup_database.sql` (which creates `dr.johnson`/`dr.chen`/`testuser` instead). On a fresh SQL-only setup, the attack script can't even authenticate.

### H5. `frontend/src/app.js:478–484` — XSS via query history

```js
historyItem.innerHTML = `
    <div class="history-timestamp">${timeString} ${item.malicious ? '⚠️' : ''}</div>
    <div class="history-query">${item.query}</div>
`;
```

`item.query` is user-controlled and inserted as HTML. A history entry like `<img src=x onerror=alert(document.cookie)>` will fire. Persists across sessions because it's in `localStorage`. Fix: use `textContent` on a `<div>` child, not `innerHTML` interpolation.

### H6. `frontend/src/app.js:367–399` — XSS via `displayAuditInfo`

`response.securityFlags.authenticatedUser`, `userRole`, `allowedOperations.map(op => ...).join('<br>')`, and `this.authToken.substr(0,20)` are all interpolated directly into innerHTML. `authenticatedUser` is the JWT-claimed username and is user-controllable at registration. Same fix as H5.

### H7. `frontend/src/app.js:390–394` — fabricated audit data shown to user

```js
<strong>Session ID:</strong> sess_${Math.random().toString(36).substr(2, 9)}<br>
<strong>IP Address:</strong> 192.168.100.${Math.floor(Math.random() * 254) + 1}<br>
```

These values are **randomly generated client-side** every time the audit tab is opened. They look like real audit fields but mean nothing. For a security-research lab, this is actively misleading — students will think the system is tracking real session IDs and source IPs. Either remove these lines or have the backend return the real values from the audit log (the backend already records them).

### H8. `frontend/src/app.js:563` — wrong Ollama health endpoint

`checkSystemStatus()` probes `getUrl('LLM', '/health')`. Ollama has no `/health` endpoint — the backend's own `LLMClient.test_connection()` (`backend/llm_client.py:48–52`) correctly hits `/api/tags`. The LLM status dot will always show "error" or "warning" in production. Fix: probe `/api/tags`, or rely solely on the backend `/api/health` like the DB check does.

### H9. `frontend/src/app.js:566–593` — DB status code path is largely dead

The DB branch fetches `192.168.0.245:5432` (`postgresql://...`) as if it were HTTP, *then* falls through and hits the backend `/api/health`. The first fetch always throws CORS/protocol errors but is caught by the outer `catch`; only the backend probe matters. Either delete the dead path or implement just one strategy.

### H10. `backend/app.py:35` — CORS misconfiguration

```python
CORS(app, resources={r"/api/*": {"origins": "*", ...}}, supports_credentials=True)
```

Browsers refuse `Access-Control-Allow-Origin: *` together with credentialed requests; either origin must be an explicit list or `supports_credentials` must be False. As written, real cross-origin credential requests will fail with `The value of the 'Access-Control-Allow-Origin' header in the response must not be the wildcard '*' when the request's credentials mode is 'include'`. Fix: set `origins` from `Config.CORS_ORIGINS` (already read in config.py:76) and drop `supports_credentials` if not needed for the SPA's same-origin proxy.

### H11. `frontend/vite.config.js:11` — hard-coded VM proxy target

`target: 'http://192.168.0.245:5000'` is one developer's machine. The dev server will silently 502 for anyone else. Fix: read from `process.env.BACKEND_URL` with a sane default of `http://localhost:5000`.

### H12. `frontend/package.json:13–23` — every `npm test*` script is broken

All `test` scripts run Jest against `tests/**/*.test.js`. No `tests/` directory exists. `jest.setupFilesAfterEach` references `<rootDir>/tests/setup.js` which is also missing. `npm test` exits with `No tests found`. `coverage/lcov.info` is 0 bytes.

### H13. `backend/llm_client.py:281–286` — silent return path

```python
except Exception as e:
    ...
    if attempt == self.max_retries - 1:
        raise
    time.sleep(1)
```

If `_call_ollama` exhausts the loop on a non-Timeout/non-Connection exception, it falls off the end and returns `None`. `generate_sql` then passes `None` into `_post_process_sql`, which calls `.strip()` → `AttributeError`. Add an explicit `raise RuntimeError("LLM retries exhausted")` after the loop, or restructure as a `for...else` with `raise` in the `else`.

### H14. `backend/config.py:39–48` — Config raises at import time

`DB_HOST` and `DB_PASSWORD` are required at import. Any tool importing `config` (the diagnose script, future tests, `setup.py`) cannot run without a populated `.env`. The diagnostic tool that is meant to help when login is broken can't even load. Fix: defer the validation into a `validate()` classmethod called by `app.py` at startup, not at import.

---

## 4. Medium-severity issues

### M1. `data-generator/generate_sample_data.py:259` and `backend/generate_sample_data.py:259`
`random.choice([d for d in doctors if d.is_active])` raises `IndexError` if the random ~10% inactive rate happens to flag all doctors. Add a non-empty guard.

### M2. `backend/generate_sample_data.py:421–451` vs README test accounts
README documents `admin` / `test_doctor` / `test_nurse` / `test_patient` / `vulnerable_user`. The Python generator creates all five (good), but `setup_database.sql` creates none of them (it creates `dr.johnson`, `nurse.smith`, `patient.john`, `testuser`). Pick one source of truth.

### M3. `backend/app.py:38–39` — module-level singletons crash on missing DB/LLM
`db_manager = DatabaseManager()` and `llm_client = LLMClient()` run at import time. If Postgres or Ollama is down at boot, the whole API process exits. Lazy-initialize, or wrap in try/except with a degraded-mode flag.

### M4. `backend/utils.py:357–378` — mixed logging libraries
`log_security_event` uses `logging.getLogger('security')` while the rest of the app uses `loguru`. Output goes to different sinks; security events bypass the configured audit log file. Use `logger` from loguru with `bind(type="AUDIT")`.

### M5. `backend/utils.py:33` — log handlers stack on each `setup_logging()` call
`setup_logging()` first calls `logger.remove()` (good). But the function is only called once from `app.py:41`. If imported from tests or scripts repeatedly, fine. Document or guard with `_already_initialized`.

### M6. `backend/utils.py:289–306` — `generate_response` is dead
Imported in `app.py:31` but never called. The app always uses `jsonify` directly. Either use it (for the documented security headers `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`) or delete.

### M7. `backend/security.py:209–213` — sensitivity filter on schema is whole-word, but `Config.SENSITIVE_COLUMNS` contains entries like `social_security_number` and `card_number` — column names in the schema use `ssn`, `insurance_id`, `license_number`. Verify the actual column-name → sensitive-pattern matrix; today only direct-name matches are caught.

### M8. `backend/database.py:332` — table-name regex misses `INTO` columns
The regex captures `FROM/JOIN/UPDATE/INTO/DELETE FROM`. For multi-part `INSERT INTO patients(col1, col2) VALUES ...`, the regex catches `INTO patients` fine. But the regex captures with `(\w+)` so quoted/qualified table names like `"public"."patients"` slip through. Use `sqlparse` or `sqlglot` for real parsing.

### M9. `backend/database.py:280–341` `_validate_query_permissions` — WHERE-clause check is regex-only
`WHERE.*PATIENT_ID\s*=\s*(\d+)` accepts `WHERE 1=1 OR PATIENT_ID = <my_id>` — an attacker can satisfy the regex while the WHERE clause still matches everything. Parse the AST or run the query inside a row-level security policy in Postgres.

### M10. `backend/security.py:339–344` — keyword-only role check
Nurse/patient asking *"how do I read administrator notes"* is flagged because `admin` is a substring. Use word boundaries on each keyword: `re.search(rf'\b{re.escape(kw)}\b', q)`.

### M11. `frontend/src/utils/api.js` + `frontend/src/utils/storage.js` — dead code
Both modules are well-written and *fix* several bugs in `app.js` (correct `/api/verify`, no XSS, central error handling) — but nothing imports them. Either wire them into `app.js` (recommended) or delete.

### M12. `frontend/public/config.js:13–17` — `getEnvVar` ignores the key
The function signature reads `(key, defaultValue)` but the body returns `defaultValue` unconditionally. The `VITE_*` envPrefix in vite.config.js is therefore unused. Either inject env at build time via Vite's `import.meta.env` or document that runtime overrides require editing `config.js` directly.

### M13. `frontend/src/app.js:393` — `substr` is deprecated
Minor — modern browsers warn. Use `slice(0, 20)`.

### M14. `backend/app.py:355–356` — `executionTime` units inconsistency
`executionTime` is sent in **milliseconds**, but `llmProcessingTime` is also in ms (line 383) — yet the frontend renders `query-time` as `response.executionTime` (raw ms with no suffix) and `llm-time` as `(response.llmProcessingTime / 1000).toFixed(1)` (seconds). Pick one unit per field and document it.

### M15. `backend/setup.py:121–125` — looks for `requirements.txt` in `self.project_root`
`self.project_root = Path(__file__).parent`, i.e. `backend/`. The README tells users to install from project root (`uv pip install -r requirements.txt`), but `requirements.txt` only exists at `backend/requirements.txt`. README's command will fail.

### M16. `backend/llm_client.py:317` `_apply_security_filters` for `nurse` role
The "redact" step rewrites the SQL: `SELECT ssn` becomes `SELECT '***REDACTED***' as ssn`. Functional, but breaks when `ssn` is used in WHERE/ORDER BY or with a table prefix (`p.ssn`). The redaction happens **client-side** at the SQL level — easier and correct to leave SQL alone and let `filter_results_by_role` redact the result set.

### M17. `LabDocumentation/`docs — drift on env vars
Sample env documented in README uses `DB_HOST=192.168.100.30` (the VM lab address); `.env.docker` uses `DB_HOST=postgres` (the compose service name). Document both setups explicitly in one place to avoid users copy/pasting the wrong one.

### M18. `install/QUICK_START.md:6` — absolute path leak
`/home/sunds/Code/Database_Security_TestApp/install` is hard-coded. Replace with relative path or `$(pwd)`.

---

## 5. Low-severity issues

- **L1.** `backend/utils.py:608–619` — `get_system_info` uses `psutil.disk_usage('/')` (Linux/Mac) or `C:` (Windows); breaks on WSL paths or read-only roots.
- **L2.** `backend/llm_client.py:301` — `(SELECT\s+.*?)(?:;|\n\n|$)` truncates multi-paragraph SELECTs at the first `\n\n`.
- **L3.** `backend/security.py:478–479` — security-event list cap is in-process only; if you run multiple Gunicorn workers each has its own capped list, and `/api/audit` shows only the current worker's view.
- **L4.** `backend/database.py:107` — `.filter(AdminUser.is_active)` works but `.filter(AdminUser.is_active.is_(True))` is clearer and lint-friendly.
- **L5.** `backend/app.py:553` — `attack/scenarios` endpoint requires admin auth (good) but returns a hard-coded sample list, not the rich set in `attack_scenarios.py`. Drift hazard.
- **L6.** Multiple files start with hand-copied docstring blocks containing the author's email — fine, but the GitHub URL differs between files (`DB_Security_Testing` vs `Database_Security_TestApp` in `attack_scenarios.py:8` and `frontend/public/config.js:5`).
- **L7.** `backend/diagnose_login.py` imports `bcrypt`, `requests`, `sqlalchemy` at module top. If any are missing it dies before printing its own diagnostic message. Wrap the imports in a try/except with a helpful "missing dependencies" hint (the script already does this for `from database import DatabaseManager` but not for everything).
- **L8.** `.gitignore` — `*.bak`, `_*` are fine, but missing common entries like `*.pyc`, `dist/`, `node_modules/` (the last only matters if you stop using `package-lock.json` as the source of truth).
- **L9.** `frontend/test-login-debug.html`, `verify-fixes.html`, `test-config.html` — appear to be one-off scratch files. Either move to `dev-tools/` or delete to reduce noise.

---

## 6. Intentional vulnerabilities — by design (do NOT "fix")

These exist for the lab's research purpose and are correctly gated on `security_mode == 'vulnerable'`:

- Direct execution of unparameterized LLM-generated SQL (`backend/database.py:206`).
- Skipping `validate_question`/`validate_sql` in vulnerable mode (`backend/security.py:74, 122`).
- Full schema (including `admin_users`, `audit_log`) exposed to LLM context in vulnerable mode (`backend/security.py:188`).
- No result filtering for non-admins in vulnerable mode (`backend/security.py:219`).
- Default `SECURITY_MODE=vulnerable` in `.env.docker` and `Config`.
- Weak default password (`password123`) for all seeded test accounts.

These are *features* of the lab. The README's "SECURITY NOTICE" already warns users.

⚠️ **However**, the secure mode is supposed to demonstrate the *fix* — and several "fixes" in secure mode are broken (C4, C5, H2 above). The pedagogical value of the lab is undermined if students can't see a working contrast.

---

## 7. Missing functionality

### F1. No `/api/logout` endpoint
Frontend logout (`app.js:156`) just clears `localStorage`. The JWT is still valid until expiry. A real logout would server-side blacklist the token. Document this gap or add a minimal in-memory revocation list.

### F2. `/api/security/mode` only flips an in-memory flag
`SecurityManager.set_mode` (`security.py:46`) mutates `self.current_mode` on the singleton. With multiple workers, only one sees the change. Persist to DB or use a shared cache (Redis).

### F3. `validate_email` / `validate_phone` / `validate_ssn` (`utils.py:327–342`) unused
Defined but never called. Either wire into the data-generator and login flow or drop.

### F4. `escape_sql_identifier`, `analyze_query_complexity`, `create_test_data_generator`, `export_security_logs`, `get_system_info` (`utils.py`) — defined, never called.
~150 lines of unused infrastructure. Wire it into the API (a `/api/system` admin endpoint? a `/api/security/analyze` for query complexity?) or remove.

### F5. `SecurityManager.generate_security_report` (`security.py:500`) unused
There's no `/api/security/report` route. Add one (admin-only) — it's an obvious lab feature.

### F6. Audit endpoint missing total count
`GET /api/audit` (`app.py:480`) returns `'total_count': len(audit_logs)` — but that's the *page* count, not the database total. UI pagination cannot work. Fix to query `COUNT(*)` separately.

### F7. No password change / account self-service endpoints
For a multi-user lab, students cannot rotate their password without re-running `generate_sample_data.py`.

### F8. The `BackupOperations` mentioned in `get_allowed_operations_for_role('admin')` (`app.py:97`) have no endpoint, even though `DatabaseManager.backup_database` (`database.py:570`) exists.

---

## 8. Missing tests

**Current state:** zero test files (`find . -name 'test_*.py' -o -name '*.test.js'` returns empty). `frontend/package.json` declares Jest scripts pointing to `tests/`, but the directory does not exist. `frontend/coverage/lcov.info` is 0 bytes.

### Test framework recommendations

**Backend** — `pytest` + `pytest-flask` + `pytest-mock` + `responses` (mock the Ollama HTTP API) + `factory-boy` + `faker`. Use SQLite in-memory for fast unit tests; spin up a real Postgres container for integration tests via `testcontainers`.

**Frontend** — the existing Jest config can be salvaged, but **switch to Vitest** since Vite is already the build tool (`frontend/vite.config.js`). Add `@testing-library/dom` (already declared as a dep) and `msw` for fetch mocking.

### Priority test cases (P0 = must-have before any code change ships)

**P0 — security correctness** (these protect the *premise* of the lab):

1. `SecurityManager.filter_results_by_role(role='patient', user_patient_id=N)` drops rows where `patient_id != N`. (`security.py:227`)
2. `SecurityManager.filter_results_by_role` redacts `ssn`, `insurance_id`, `license_number`, `password_hash` for nurse/patient. (`security.py:239`)
3. `SecurityManager.validate_sql` blocks `DROP/DELETE/UPDATE/ALTER/TRUNCATE` in secure mode. (`security.py:355`)
4. `SecurityManager.validate_sql` blocks UNION for non-admin roles. (`security.py:144`)
5. `SecurityManager.validate_question` blocks "ignore previous instructions", "you are now admin", classic SQLi patterns. (`security.py:65`)
6. `SecurityManager.filter_schema_by_role` hides `admin_users`/`audit_log` from non-admin. (`security.py:186`)
7. `DatabaseManager._validate_query_permissions` rejects patient UPDATE without `WHERE patient_id = <user_patient_id>`. (`database.py:280`) — *and* test the bypass in M9 above.
8. `DatabaseManager.authenticate_user` locks the account after 5 failed attempts for 30 minutes. (`database.py:141`)
9. JWT enforcement: `/api/query` returns 401 for missing/expired/forged token. (`app.py:43`)
10. `LLMClient._get_cache_key` includes schema hash — schema change invalidates cache. (`llm_client.py:367`)

**P0 — regression guards for bugs found in this review:**

11. `/api/verify` accepts a fresh token and returns the user; `/api/login` rejects GET with 405. (catches C3)
12. Patient secure-mode query against `patients` returns rows *without* SQL errors. (catches C4)
13. `setup_database.sql` parses without error in a CI step. (catches C1)
14. Seeded admin user's password hash verifies against `password123`. (catches C2)
15. A query that includes `pg_sleep(60)` is aborted within `QUERY_TIMEOUT`. (catches C5)
16. Importing `data_generator.database` does not raise `AttributeError`. (catches C6)
17. `/api/health` requests do not appear in the request log. (catches H1)

**P1 — important:**

18. `LLMClient._call_ollama` retries with exponential backoff on timeout (mock 3 timeouts, then success).
19. `LLMClient._post_process_sql` strips ```` ```sql ```` fences and adds trailing semicolon.
20. `validate_json_input` returns 400 with missing-fields list when payload is incomplete.
21. `User.can_access_patient(pid)` returns True for admin/doctor/nurse; True for patient iff their `patient_id == pid`.
22. `QueryResult.filter_sensitive_data` leaves data unchanged for admin role.
23. Health endpoint returns 503 if either DB or LLM is unreachable.
24. Frontend: login flow stores `authToken` to localStorage and routes to main app.
25. Frontend: `displayAuditInfo` does **not** render unescaped HTML from `securityFlags` fields (catches H5, H6).
26. Frontend: `executeQuery` short-circuits to a friendly error if no `authToken`.

**P2 — nice-to-have:**

27. Cache TTL eviction and 100-entry cap on `LLMClient.cache`.
28. `analyze_query_complexity` scores joins/subqueries/UNION correctly.
29. `mask_sensitive_data` keeps last 4 chars visible.
30. CORS headers present on responses.

### Refactors to make code testable

- **`SecurityManager` module-level singleton** (`app.py:39`) — tests that toggle mode leak state. Use a request-scoped instance via Flask `g`, or accept a fresh instance per test via fixture.
- **`DatabaseManager` constructor connects to Postgres on init** — tests can't import `app.py` without a real DB. Make the connection lazy or accept an injected engine.
- **`Config` raises on import without env vars** (H14) — tests need a sentinel mode.

---

## 9. Documentation gaps

Cross-checked against §6 from the Documentation Audit (and verified against code):

| # | Doc | Issue |
|---|---|---|
| D1 | `README.md:2`, `INSTALL.md:8`, `QUICKSTART.md:8` | Image paths use Windows backslashes (`LabDocumentation\docs\images\logo-trnsp.png`) — broken on Linux/Mac and GitHub web UI. |
| D2 | `attack_scenarios.py:8`, `frontend/public/config.js:5` | GitHub URL points to `Database_Security_TestApp`; everything else points to `DB_Security_Testing`. |
| D3 | `QUICKSTART.md:43` | LLM default model listed as `ds2-coder:latest`; code defaults to `qwen-coder-sql:latest`. |
| D4 | `QUICKSTART.md` test-account table | Lists `admin`/`doctor`/`nurse`; only `admin` exists. Generator creates `test_doctor`, `test_nurse`, etc. |
| D5 | `README.md:77`, `QUICKSTART.md:64` | `pip install -r requirements.txt` from project root fails — the file is at `backend/requirements.txt`. |
| D6 | `README.md` Prerequisites | Does not mention Node.js 22.12+; `package.json` requires it. |
| D7 | `DOCKER_QUICKSTART.md:29–145` | Inconsistently references `docker-compose-all.yml` vs `docker-compose-infra.yml` + `docker-compose.app.yml`. Document the difference. |
| D8 | `install/QUICK_START.md:6` | Absolute path `/home/sunds/...` baked in. |
| D9 | `README.md` API table | Documents `/api/query`, `/api/login`, etc., but doesn't list `/api/verify`, `/api/security/mode`, `/api/attack/scenarios`, all implemented. |
| D10 | Docstrings | Module headers are present and good. But `SecurityManager`, `LLMClient`, `DatabaseManager` lack class-level usage examples; `_validate_query_permissions` has no docstring explaining the patient-row-level-security contract (which has the M9 bypass). |
| D11 | `.env.docker` vs `README.md` env block | Different variable names referenced (`API_HOST` vs `DB_HOST`-only set in README example); no canonical reference. |
| D12 | Missing `CONTRIBUTING.md` / `SECURITY.md` for a security-research repo. |

---

## 10. Recommended remediation order

If I had to ship one PR per week against this codebase, I'd sequence:

1. **Week 1 — make the secure-mode demo work again**
   Fix C1, C2, C3, C4, C5, C6, H1, H2, H8. Tests #11–17 from §8.
2. **Week 2 — wire up tests and CI**
   Stand up pytest + vitest, port the P0 test list. Add a GitHub Actions workflow that runs them and parses `setup_database.sql` with `psql --dry-run` (or actually executes it in a Postgres container).
3. **Week 3 — eliminate duplication (C7)**
   Move shared code to `common/`, update both Dockerfiles. Re-run all tests to confirm parity.
4. **Week 4 — frontend security cleanup**
   Fix H5/H6 XSS, replace `app.js` direct fetches with `utils/api.js`, delete fabricated audit fields (H7). Add P1 frontend tests.
5. **Week 5 — documentation reconciliation**
   Update README/QUICKSTART/DOCKER_QUICKSTART; pick one canonical setup path; fix all D1–D12.
6. **Ongoing — backlog of M and L issues, missing functionality (F1–F8).**

---

## Appendix A — files reviewed

```
backend/app.py, attack_scenarios.py, config.py, database.py,
diagnose_login.py, generate_sample_data.py, llm_client.py, models.py,
security.py, setup.py, setup_database.sql, utils.py, requirements.txt,
backend/Dockerfile, backend/entrypoint.sh
data-generator/{config.py, database.py, models.py, generate_sample_data.py, Dockerfile}
frontend/src/{app.js, main.js, utils/api.js, utils/storage.js}
frontend/{package.json, vite.config.js, nginx.conf, Dockerfile, public/config.js}
docker-compose-all.yml, docker-compose-infra.yml, docker-compose.app.yml
deploy.sh, docker-debug.sh, .env.docker, .gitignore
install/{install.sh, install_backend_frontend.sh, install_ollama.sh,
         install_postgresql.sh, validate_installation.sh, common_utils.sh}
README.md, INSTALL.md, QUICKSTART.md, DOCKER_QUICKSTART.md,
install/QUICK_START.md, install/README.md, LabDocumentation/
```

## Appendix B — what I did NOT review in depth

- `LabDocumentation/docs/` rendered MkDocs site (only spot-checked).
- Logo/image assets.
- `package-lock.json` / `requirements-dev.txt` (no security audit of pinned versions performed).
- Ollama modelfiles (`ollama/modelfiles/`).
- The `coverage/` artifact directory (it's a stale artifact from a previous run).
