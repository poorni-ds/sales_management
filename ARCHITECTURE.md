# Sales Intelligence Hub — Architecture & Learning Guide

> Written for someone new to coding. If a term is unfamiliar, check the **Glossary** at the bottom — every technical word used above it is explained there.

---

## 1. What This App Actually Does, In Plain Words

Imagine a company with sales branches in different cities. Every time someone in a branch makes a sale, it gets logged. Customers don't always pay the full amount immediately — they might pay in parts (a "split payment"). This app:

1. Records every sale.
2. Records every payment against that sale, even partial ones.
3. **Automatically** works out how much is still owed — nobody types that number in by hand, the database calculates it.
4. Shows two different admins two different views: a **Super Admin** sees everything, everywhere; a regular **Admin** only sees their own branch.

---

## 2. The Three Layers

Think of the app as three stacked layers, each only talking to the one directly below it:

```
┌─────────────────────────────┐
│   Streamlit UI (frontend)    │  ← what the user clicks and sees
├─────────────────────────────┤
│   Python logic (backend)     │  ← decides who can see what, runs the queries
├─────────────────────────────┤
│   MySQL database             │  ← stores the data, enforces the money math
└─────────────────────────────┘
```

**Why layers matter:** each layer has one job. The database's job is to *never* let the numbers go wrong, no matter what the Python code does. The Python layer's job is to decide *who is allowed to ask for what*. The Streamlit layer's job is just to display things and collect clicks/form input. This separation is why, later, you could swap Streamlit for a different UI without touching the database at all.

---

## 3. The Database Layer — Where the "Truth" Lives

Four tables, and how they connect:

```
branches ──┬─< customer_sales ──< payment_splits
           └─< users
```

(The `<` means "many of these can point to one of those" — e.g. many `customer_sales` rows can belong to one `branches` row.)

- **branches** — the list of cities/offices. Just an ID and a name.
- **customer_sales** — one row per sale. Knows which branch it belongs to (`branch_id`), how much was sold (`gross_sales`), and — critically — it does *not* let anyone manually decide `pending_amount`. That column is **generated**: MySQL computes it itself as `gross_sales - received_amount`, every single time either of those two numbers changes. It's physically impossible for `pending_amount` to be wrong or out of sync, because it isn't really "stored" the normal way — it's recalculated on the fly.
- **users** — who's allowed to log in, and whether they're a Super Admin or an Admin.
- **payment_splits** — one row *per payment*, not per sale. If a customer pays in three installments, that's three rows here, all pointing at the same `sale_id`. This is what makes partial/split payments possible.

### Triggers: code that lives *inside* the database

A **trigger** is a small piece of logic that MySQL runs automatically when something happens — e.g. "whenever a new row is added to `payment_splits`, immediately go update `customer_sales`." This project uses triggers instead of Python code to update `received_amount`, on purpose. Why?

- If the update logic lived only in Python, then *any* future bug, script, or careless direct database edit could accidentally set the wrong `received_amount` and nobody would notice.
- Because it lives in the database as a trigger, it's **impossible to bypass** — even a totally different program connecting to this same database years from now would still get correct, automatically-updated numbers.

This is a core lesson of the project: **push data-integrity rules as close to the data as possible**, rather than trusting every app that touches the data to remember to follow the rules.

---

## 4. The Backend Layer — Python as the Gatekeeper

The Python code has two jobs:

1. **Talk to MySQL** — open a connection, send a query, get results back. This is handled by a small, reusable connection module so the rest of the code never has to worry about connection details.
2. **Enforce who can see what** — this is the important one. Even though the *database* doesn't know or care who's asking, the Python layer checks: "Is this person an Admin? If so, silently add `WHERE branch_id = their_branch` to every query before it's sent." This is called **row-level access control**, and it's done in Python (not just hidden in the UI) so that there's no way to trick the app into showing another branch's data.

### Passwords

Passwords are never stored as plain, readable text — they're **hashed** first (turned into a scrambled, one-way string). When someone logs in, their typed password gets hashed the same way and the two hashes are compared. Nobody — not even someone who steals the database file — can read the original passwords back out. This is standard practice in real-world software, not just a "nice to have" for this project.

---

## 5. The Frontend Layer — Streamlit

Streamlit turns plain Python functions into a web page — no HTML/CSS/JavaScript required. Each "page" (Login, New Sale, Reports, etc.) is just a Python file that:

1. Checks: "is someone logged in?" (stored in `st.session_state`, which is Streamlit's way of remembering things between clicks — like a temporary notebook that survives as the user clicks around, but is wiped when they close the browser tab).
2. Fetches whatever data it needs by calling backend functions (never writing raw SQL directly in the page file — that's the backend's job).
3. Displays it with `st.dataframe`, `st.form`, `st.metric`, or a chart.

**Why keep SQL out of the page files?** If a query needs fixing, you want one place to fix it (the backend `queries.py`), not to hunt through seven different page files that each wrote their own slightly-different version of "get sales for a branch."

---

## 6. Following One Piece of Data All the Way Through

To really understand the architecture, trace a single action end-to-end:

**"Add a ₹4,000 payment to Sale #12."**

1. **Streamlit (frontend):** Admin fills a form — sale ID, amount, date, method — and clicks Submit.
2. **Python (backend):** the page calls something like `insert_payment(sale_id=12, amount=4000, ...)`, which runs an `INSERT INTO payment_splits ...` through the connection module.
3. **MySQL (database):** the insert succeeds, which **automatically fires the trigger** on `payment_splits`. The trigger recalculates the total paid for Sale #12 and updates `customer_sales.received_amount`.
4. **MySQL (again):** updating `received_amount` causes `pending_amount` to instantly recompute (it's a generated column) and can also fire the *second* trigger that flips `status` from `Open` to `Close` if the balance hits zero.
5. **Python (backend):** the page re-queries the sale and gets back the *already-correct* numbers — it never calculated anything itself.
6. **Streamlit (frontend):** displays the updated `received_amount`, `pending_amount`, and `status` to the user.

Notice: **the Python code never did any subtraction.** All the financial math happened inside the database, automatically, as a side effect of one `INSERT`. That's the whole design philosophy of this project in one example.

---

## 7. How to Read This Codebase as a Beginner

If you're new to a project like this, read it in this order — not top-to-bottom of the file tree, but in the order data actually flows:

1. `db/schema.sql` — read this first. It tells you what the "nouns" of the system are (branches, sales, users, payments) and how they relate.
2. The trigger definitions — read these next, since they explain the *rules* the data must obey.
3. `db/connection.py` and `db/queries.py` — see how Python talks to the tables you just read about.
4. `auth/auth.py` — see how login and role-checking works.
5. `app.py`, then the `pages/` folder in the order a user would actually click through them (Login → Home → New Sale → Add Payment → Reports).

This "data first, then rules, then access, then UI" order matches how the app was actually designed, and it's a good habit for reading *any* unfamiliar codebase — figure out what data exists before worrying about what the buttons do.

---

## 8. Glossary

- **Primary Key (PK):** a column that uniquely identifies each row in a table (like an ID number no two rows share).
- **Foreign Key (FK):** a column in one table that points to a Primary Key in another, linking the two tables together (e.g. `customer_sales.branch_id` points to `branches.branch_id`).
- **Generated Column:** a column whose value MySQL calculates automatically from other columns, rather than something you insert yourself (`pending_amount`).
- **Trigger:** a block of SQL code that runs automatically inside the database whenever a specified event happens (an insert, update, or delete on a specific table).
- **ENUM:** a column type restricted to a fixed list of allowed values (here, `status` can only ever be `'Open'` or `'Close'`).
- **Session state:** a way for a web app to "remember" information (like who's logged in) as a user clicks from page to page, without asking them to log in again on every click.
- **Row-level access control:** restricting *which rows* of a table a user is allowed to see or change, based on who they are (e.g. an Admin only sees their branch's rows) — enforced in code, not just hidden in the UI.
- **Hashing (passwords):** turning a password into a scrambled, irreversible string before storing it, so the real password is never saved anywhere in readable form.
- **Parameterized query:** a way of writing a SQL query with placeholders (`%s`) instead of directly inserting user-typed text into the query string — this is the standard defense against SQL injection attacks.
- **RBAC (Role-Based Access Control):** the general pattern of giving different users different permissions based on their assigned role (here: Super Admin vs Admin).

---

---

## 9. How This Matches Your Actual Code

Everything above describes the real, final project (not a hypothetical plan) — here's the exact mapping:

| Concept above | Real file |
|---|---|
| Database layer | `sql/schema.sql` (reference copy) + `branches.py`, `customer_sales.py`, `users.py`, `payment_split.py` (these four scripts build it for real, in that order) |
| Connection module | `Connector.py` — reads credentials from `.env` instead of hardcoding them |
| Password hashing | `security.py` — `hash_password()` / `verify_password()` |
| Row-level access control | the `if role == "Admin": ... branch_id = ...` checks inside `database_functions.py` and each page |
| Frontend entry point | `login.py` |
| Dashboard pages | `pages/dashboards.py`, `pages/Sales.py`, `pages/create_sales.py`, `pages/Payments.py`, `pages/Analytics.py`, `pages/Query_Explorer.py` |
| "Execute predefined SQL queries" requirement | `pages/Query_Explorer.py` |

### Bugs that existed in the original source, and why they mattered

Worth understanding these even though they're now fixed — they're good examples of easy-to-make mistakes:

1. **A function executing itself instead of its own query** (`database_functions.py`, `get_all_pending_amount`). The line read `cursor.execute(get_all_pending_amount)` — passing the *function object* instead of the *query string* it had just built. Python didn't catch this at "compile time" because it's valid Python to pass a function around like that; it only breaks when MySQL tries to run it as SQL and fails. Lesson: a bug can be syntactically perfect Python and still be wrong — the compiler checks grammar, not intent.

2. **A function call standing in for a condition** (`pages/Payments.py`). The code had `elif get_branchwise_pending_amount():` where it meant `elif role == "Admin":`. This actually *runs* the function to decide true/false, rather than checking who the user is. It happened to work by accident when the result was empty, but would crash the moment an Admin branch had more than one pending sale, because Python refuses to treat a multi-row table as a single True/False value. Lesson: don't put an expensive or side-effecting function call where a role check belongs, even if it "happens" to evaluate correctly right now.

3. **Indentation silently changing which block code belongs to** (`pages/create_sales.py`). A few lines that were meant to run *only* inside an `else:` block (after validation passed) were indented one level too shallow, so they actually ran as part of the *outer* block — meaning they'd execute even when validation failed, referencing variables (`cursor`, `New_sales_query`) that were never created because the `else` branch never ran. In Python, indentation isn't just style — it *is* the grammar. Lesson: when nesting several `if` levels, it's worth double-checking each block's indentation matches where you actually want it to run, especially after copy-pasting code.

These are exactly the kind of bugs that pass a visual read-through (the code "looks" right) but fail the moment a specific path through the logic gets triggered — which is why testing each branch (not just the happy path) matters.
