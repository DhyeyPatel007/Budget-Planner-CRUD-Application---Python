Simple Budget Planner (JSON) — Console CRUD

A beginner-friendly, console-based budget planner that stores transactions in a JSON file.
No external Python modules required — works with the Python standard library only.

Features

Create / Read / Update / Delete (CRUD) transactions

Store transactions in a human-readable JSON file (budget_data.json)

Monthly summary (YYYY-MM) and category breakdown reports

Safe, atomic saves (write to temporary file then rename)

Friendly prompts and validation (dates, amounts)

Lightweight — great for learning, prototyping, or personal use

Files

budget_json_human_friendly.py (or budget_data.json if you saved it under another name) — main script

budget_data.json — automatically created when you add your first transaction

Requirements

Python 3.6+ (uses datetime.isoformat() and f-strings)

No third-party packages

Quick start

Clone or download this repository.

(Optional) Create and activate a virtual environment.

Run the script:

python budget_json_human_friendly.py


Follow the on-screen menu to add, list, view, update, or delete transactions.

Usage / Menu

When you run the script you'll see a menu:

==== Simple Budget Planner ====
1) Add transaction
2) List transactions
3) View by id
4) Update transaction
5) Delete transaction
6) Monthly summary
7) Category breakdown
8) Show latest 5
9) Reset (delete all) — DANGEROUS
0) Exit
Choose:


Add transaction — enter type (income or expense), amount, category, date (YYYY-MM-DD, defaults to today), notes (optional).

List transactions — shows recent transactions in descending date order.

View by id — print full details of a specific transaction.

Update transaction — change one or more fields (leave blank to keep current).

Delete transaction — remove a transaction by id.

Monthly summary — shows net total per month (YYYY-MM -> Net).

Category breakdown — shows totals per category.

Show latest 5 — quick view of the five most recent transactions.

Reset — deletes all data (requires typing YES to confirm).

Data format

budget_data.json structure:

{
  "next_id": 4,
  "transactions": [
    {
      "id": 1,
      "type": "expense",
      "amount": -250.0,
      "category": "Food",
      "date": "2025-11-24",
      "notes": "Lunch",
      "created_at": "2025-11-24T20:00:00",
      "updated_at": null
    },
    {
      "id": 2,
      "type": "income",
      "amount": 1500.0,
      "category": "Salary",
      "date": "2025-11-01",
      "notes": null,
      "created_at": "2025-11-01T09:00:00",
      "updated_at": null
    }
  ]
}


next_id is used to generate unique integer IDs for transactions.

Expense amounts are stored as negative numbers so net sums are straightforward.

Implementation notes / decisions

Uses JSON to avoid SQL boilerplate and reduce similarity with common SQL tutorials.

Atomic save: writes to a temporary file and renames it to reduce corruption risk.

Basic input validation: checks date format and numeric amounts.

Not designed for concurrent multi-user access — for heavy usage, migrate to a real DB.

Extending the project (ideas)

Add CSV export / import.

Add simple password protection or encryption for the JSON file.

Add search and filter options (date range, category, text search in notes).

Add a small web or GUI frontend (Flask, Tkinter, etc.).

Add unit tests for core functions.

Troubleshooting

Corrupt JSON file: The script moves a corrupt file to budget_data.json.corrupt and starts fresh.

Permission errors when saving: Ensure you have write permission in the working directory.

Wrong date format: Use YYYY-MM-DD (e.g., 2025-11-24) or press Enter for today.

License

This project is released under the MIT License — copy, modify, and use it freely.

Contributing

Contributions are welcome! Open an issue or PR with improvements, bug fixes, or feature ideas.

Author

Created for learning and small personal projects.
If you want a version that uses CSV, shelve, or a small SQLite backend (with migration helpers), I can provide it.
