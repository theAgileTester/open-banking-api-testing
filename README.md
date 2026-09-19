# Open Banking API Testing Project

A self-directed QA portfolio project testing the TrueLayer Open Banking sandbox API — covering manual API testing, Python test automation, negative/edge case testing, and SQL-based test result logging.

## Scope

This project tests the **TrueLayer Data API** (sandbox/mock environment) — a UK Open Banking API that lets an authorised app read a user's bank account data (accounts, balances, transactions) after the user grants consent via an OAuth2 flow.

**In scope:**
- The full OAuth2 authorization code flow (auth link → mock bank consent → code → token exchange)
- Reading Accounts, Balance, and Transactions data
- Happy-path and negative/error-case testing of the above
- Automating the happy-path tests in Python
- Logging test results to a local SQL database

**Out of scope:**
- TrueLayer's Payments API (initiating a payment, IBAN/amount validation) — not covered here, as this project used only the read-only Data API. Noted as a possible extension.
- Automating the OAuth consent step itself (see "Findings" below for why).

## Tech Stack

| Purpose | Tool |
|---|---|
| API under test | [TrueLayer Sandbox](https://docs.truelayer.com/) (mock bank, UK Open Banking / PSD2) |
| Manual/exploratory testing | Postman |
| Automation | Python (`requests`), Jupyter Notebook |
| Test result logging | SQLite (via Python's `sqlite3`) |

## Project Structure

```
.
├── README.md
├── day10_python_automation_tests.ipynb   # Automated happy-path tests + SQL logging
├── test_results.db                       # SQLite database of logged test results
└── postman/
    └── TrueLayer_Open_Banking_Sandbox.postman_collection.json
```

*(Export your Postman collection into a `postman/` folder before pushing — see Setup below.)*

## Setup — How to Run This Yourself

### 1. TrueLayer sandbox account
- Sign up at [console.truelayer.com](https://console.truelayer.com) (free)
- Create a Sandbox application → note your `client_id` and `client_secret`
- Add a redirect URI, e.g. `https://console.truelayer.com/redirect-page`

### 2. Postman
- Import `postman/TrueLayer_Open_Banking_Sandbox.postman_collection.json`
- Create an environment with variables: `client_id`, `client_secret`, `redirect_uri`, `access_token`
- Fill in your own `client_id` / `client_secret` / `redirect_uri`

### 3. Get an access token (manual step — see Findings)
- Open this URL in an **Incognito/Private browser window** (important — see Findings):
```
https://auth.truelayer-sandbox.com/?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=accounts%20balance%20transactions%20offline_access&providers=uk-cs-mock&enable_mock=true
```
- Log in to the mock bank with username `john`, password `doe`
- Copy the authorization code shown on the "Authentication process complete" page
- Immediately paste it into TC01 (token exchange request) in Postman and send — codes expire within minutes and are single-use

### 4. Python / Jupyter
```bash
pip install requests jupyter pandas
jupyter notebook
```
- Open `day10_python_automation_tests.ipynb`
- Paste the fresh `access_token` from step 3 into the notebook
- Run all cells top to bottom

## How to Run the Tests

- **Postman:** open the collection, run folders `01 - Auth Flow`, `02 - Data API (Happy Path)`, `03 - Negative Tests` in order (or use the Collection Runner)
- **Python:** run all cells in `day10_python_automation_tests.ipynb` top to bottom; each cell prints its response and either "✅ Test passed" or an `AssertionError`
- **Test results:** logged automatically into `test_results.db`; view with:
```python
import pandas as pd, sqlite3
conn = sqlite3.connect("test_results.db")
pd.read_sql_query("SELECT * FROM test_results", conn)
```

## Test Coverage

| Test Case | Description | Expected | Type |
|---|---|---|---|
| TC01 | Exchange auth code for access token | 200 | Happy path |
| TC02 | Get Accounts | 200 | Happy path |
| TC03 | Get Account Balance | 200 | Happy path |
| TC04 | Get Account Transactions | 200 | Happy path |
| TC05 | Get Accounts with invalid token | 401 | Negative |
| TC06 | Get Balance with missing auth header | 401 | Negative |
| TC07 | Get Transactions with invalid account_id | 404 | Negative |
| TC08 | Token exchange with expired/reused code | 400 (`invalid_grant`) | Negative |
| TC09 | Token exchange with wrong client_secret | 400 (`invalid_client`) | Negative |

## Findings

**1. OAuth codes are single-use and expire within minutes.**
Early testing repeatedly failed with `invalid_grant` even when the request body looked correct. Root cause, found by inspecting the raw request in Postman's Console, was a stray double newline appended to the `code` field on paste (a Postman text-field quirk) — combined with the code simply going stale during the debugging process itself. Fix: copy the code with Cmd+A/Cmd+C directly from the browser and paste immediately, without an intermediate step (e.g. pasting into a chat or notes app first).

**2. Browser session caching caused a further `invalid_grant`, unrelated to the above.**
Even with a clean code, one run kept failing. Using an Incognito/Private window (guaranteeing a fresh session) resolved it — the regular browser window appeared to be reusing a stale mock-bank session.

**3. `GET /accounts/{id}/transactions` with an invalid `account_id` returns `401`, not `404` — but only when the access token is also invalid/expired.**
With a *valid* token, an invalid `account_id` correctly returns `404`. This was only discovered by isolating the two variables (token validity vs. account_id validity) after an initial false result.

**4. The auth/consent step (TC01) cannot be fully automated with `requests` alone.**
The mock bank's login and consent screens require a real browser session with user interaction. This is a standard constraint in Open Banking / OAuth2 testing — full end-to-end automation of the consent step would require a browser-automation tool (e.g. Selenium) or a cached/service-account token, which is a natural next step beyond this project's current scope.

## Possible Next Steps

- Automate the OAuth consent step with Selenium, removing the last manual step from the suite
- Port the 5 negative test cases (TC05–TC09) from Postman into the Python notebook for full automation parity
- Extend into the TrueLayer Payments API to cover payment-specific negative cases (invalid IBAN, negative amount)
- Add a CI step (e.g. GitHub Actions) to run the Python suite on a schedule
