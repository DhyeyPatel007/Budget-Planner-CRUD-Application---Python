"""
Budget Planner — human-friendly console CRUD (JSON storage, no external modules)
Save as: budget_json_human_friendly.py
Run with: python budget_json_human_friendly.py

Notes:
- Uses a simple JSON file (budget_data.json) to persist transactions.
- Focused on readability: friendly prompts, helpful messages, and inline comments
- Safe atomic saves (write temp then rename)
- Beginner-friendly code and clear function names
"""

import json
import os
from datetime import datetime
from tempfile import NamedTemporaryFile
from shutil import move

DATA_FILE = "budget_data.json"


def load_store():
    """Load the data file and return a dict with next_id and transactions list.
    If the file doesn't exist or is corrupted, create a fresh store.
    """
    if not os.path.exists(DATA_FILE):
        return {"next_id": 1, "transactions": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        backup = DATA_FILE + ".corrupt"
        try:
            os.replace(DATA_FILE, backup)
        except Exception:
            pass
        print(f"Warning: data file was corrupt and moved to: {backup}")
        return {"next_id": 1, "transactions": []}


def save_store(store):
    """Atomically save the store dict to disk.

    We write to a temporary file and move it into place to reduce chance of data loss.
    """
    tmp = NamedTemporaryFile("w", delete=False, encoding="utf-8", prefix="budget_", suffix=".tmp")
    try:
        json.dump(store, tmp, indent=2, ensure_ascii=False)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp.close()
        move(tmp.name, DATA_FILE)
    except Exception:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass
        raise


# ----------------------- Input helpers -----------------------

def ask_date(prompt="Date (YYYY-MM-DD) [today]: "):
    s = input(prompt).strip()
    if not s:
        return datetime.today().strftime("%Y-%m-%d")
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        print("That's not a valid date. Please use YYYY-MM-DD.")
        return ask_date(prompt)


def ask_float(prompt="Amount: "):
    s = input(prompt).strip()
    try:
        return float(s)
    except ValueError:
        print("Please enter a number like 1200 or 45.50.")
        return ask_float(prompt)


def ask_choice(prompt, choices, default=None):
    """Ask the user to choose a value from `choices` (case-insensitive).
    If default provided and user presses Enter, default is returned.
    """
    choice = input(prompt).strip().lower()
    if choice == "" and default is not None:
        return default
    if choice in choices:
        return choice
    print(f"Please enter one of: {', '.join(choices)}")
    return ask_choice(prompt, choices, default)


# ----------------------- CRUD operations -----------------------

def add_transaction(store):
    print("\nAdd a new transaction — type 'income' or 'expense'.")
    ttype = ask_choice("Type (income/expense) [expense]: ", ("income", "expense"), default="expense")
    amt = ask_float("Amount: ")
    if amt <= 0:
        print("Amount must be greater than zero.")
        return
    # store expenses as negative numbers (so net sums are easier)
    if ttype == "expense":
        amt = -abs(amt)
    else:
        amt = abs(amt)
    category = input("Category (e.g. Food, Salary) [Misc]: ").strip() or "Misc"
    date = ask_date()
    notes = input("Notes (optional): ").strip() or None

    now = datetime.now().isoformat()
    tid = store["next_id"]
    tx = {
        "id": tid,
        "type": ttype,
        "amount": amt,
        "category": category,
        "date": date,
        "notes": notes,
        "created_at": now,
        "updated_at": None,
    }
    store["transactions"].append(tx)
    store["next_id"] += 1
    save_store(store)
    print(f"Saved — transaction id: {tid}")


def list_transactions(store, limit=None):
    txs = sorted(store["transactions"], key=lambda r: (r["date"], r["id"]), reverse=True)
    if limit:
        txs = txs[:limit]
    if not txs:
        print("\nNo transactions yet — add your first one!")
        return
    print("\nRecent transactions:")
    for r in txs:
        amt = r["amount"]
        sign = "+" if amt > 0 else "-"
        notes = r.get("notes") or ""
        print(f"ID:{r['id']} | {r['date']} | {r['category']} | {r['type']} | {sign}{abs(amt):.2f} | {notes}")


def view_transaction(store):
    tid = input("Enter transaction id to view: ").strip()
    try:
        tid = int(tid)
    except ValueError:
        print("ID must be a number.")
        return
    tx = next((x for x in store["transactions"] if x["id"] == tid), None)
    if not tx:
        print("Transaction not found.")
        return
    print("\nTransaction details:")
    for k, v in tx.items():
        print(f"{k}: {v}")


def update_transaction(store):
    tid = input("Enter transaction id to update: ").strip()
    try:
        tid = int(tid)
    except ValueError:
        print("ID must be an integer.")
        return
    idx = next((i for i, x in enumerate(store["transactions"]) if x["id"] == tid), None)
    if idx is None:
        print("Transaction not found.")
        return
    tx = store["transactions"][idx]
    print("Leave blank to keep the current value.")
    print(f"Current type: {tx['type']}")
    new_type = input("New type (income/expense): ").strip().lower()
    if new_type not in ("", "income", "expense"):
        print("Invalid type. Keeping current.")
        new_type = ""

    print(f"Current amount: {tx['amount']}")
    amt_in = input("New amount: ").strip()
    if amt_in:
        try:
            amt_val = float(amt_in)
            if amt_val <= 0:
                print("Amount must be > 0. Keeping old amount.")
                amt_val = None
        except ValueError:
            print("Invalid number. Keeping old amount.")
            amt_val = None
    else:
        amt_val = None

    category = input(f"New category [{tx['category']}]: ").strip()
    date = input(f"New date [{tx['date']}] (YYYY-MM-DD): ").strip()
    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Keeping old date.")
            date = ""
    notes = input(f"New notes [{tx.get('notes') or ''}]: ").strip()

    final_type = tx["type"] if not new_type else new_type
    final_amount = tx["amount"]
    if amt_val is not None:
        final_amount = -abs(amt_val) if final_type == "expense" else abs(amt_val)
    if new_type and amt_val is None:
        # user changed type but not amount: flip sign
        if tx["type"] != new_type:
            final_amount = -tx["amount"]

    final_category = tx["category"] if not category else category
    final_date = tx["date"] if not date else date
    final_notes = tx.get("notes") if not notes else notes
    tx.update(
        {
            "type": final_type,
            "amount": final_amount,
            "category": final_category,
            "date": final_date,
            "notes": final_notes,
            "updated_at": datetime.now().isoformat(),
        }
    )
    save_store(store)
    print("Transaction updated.")


def delete_transaction(store):
    tid = input("Enter transaction id to delete: ").strip()
    try:
        tid = int(tid)
    except ValueError:
        print("ID must be an integer.")
        return
    before = len(store["transactions"])
    store["transactions"] = [x for x in store["transactions"] if x["id"] != tid]
    after = len(store["transactions"])
    if before == after:
        print("No transaction found with that id.")
    else:
        save_store(store)
        print("Deleted.")


# ----------------------- Reports -----------------------

def monthly_summary(store):
    from collections import defaultdict

    agg = defaultdict(float)
    for t in store["transactions"]:
        ym = t["date"][0:7]
        agg[ym] += t["amount"]
    if not agg:
        print("\nNo transactions to summarize.")
        return
    print("\nMonthly summary (YYYY-MM -> Net):")
    for ym in sorted(agg.keys(), reverse=True):
        print(f"{ym} -> {agg[ym]:.2f}")


def category_breakdown(store):
    from collections import defaultdict

    agg = defaultdict(float)
    for t in store["transactions"]:
        agg[t["category"]] += t["amount"]
    if not agg:
        print("\nNo transactions.")
        return
    print("\nCategory totals:")
    for cat, total in sorted(agg.items(), key=lambda kv: abs(kv[1]), reverse=True):
        print(f"{cat}: {total:.2f}")


def reset_store(store):
    ok = input("Type YES to permanently delete all data: ").strip()
    if ok == "YES":
        store["transactions"].clear()
        store["next_id"] = 1
        save_store(store)
        print("All data removed.")
    else:
        print("Cancelled.")


# ----------------------- Main menu -----------------------

def main_menu():
    store = load_store()
    menu = """
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
Choose: """
    try:
        while True:
            choice = input(menu).strip()
            if choice == "1":
                add_transaction(store)
            elif choice == "2":
                list_transactions(store)
            elif choice == "3":
                view_transaction(store)
            elif choice == "4":
                update_transaction(store)
            elif choice == "5":
                delete_transaction(store)
            elif choice == "6":
                monthly_summary(store)
            elif choice == "7":
                category_breakdown(store)
            elif choice == "8":
                list_transactions(store, limit=5)
            elif choice == "9":
                reset_store(store)
            elif choice == "0":
                print("Goodbye — data saved.")
                break
            else:
                print("Please choose a number from 0 to 9.")
    except KeyboardInterrupt:
        print("\nInterrupted — exiting.")
    finally:
        try:
            save_store(store)
        except Exception:
            pass


if __name__ == "__main__":
    main_menu()
