import os
import random
import string
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

# ~~~~~~~~~ CONSTANTS & CONFIG ~~~~~~~~~
ACCOUNTS_FILE = "accounts.txt"
TRANSACTIONS_FILE = "transactions.txt"
SEP = "|"

BG, CARD, CARD2 = "#0D0F14", "#141720", "#1A1E2A"
ACCENT, ACCENT2, DANGER, WARN, TEXT, TEXT_DIM = "#00FFB2", "#0077FF", "#FF4560", "#FFB830", "#E8EAF0", "#6B7280"
FONT_MONO = ("Cascadia Code", 10)
FONT_BOLD = ("Cascadia Code", 12, "bold")


# ~~~~~~~~~ DATA STRUCTURES & ALGORITHMS ~~~~~~~~~
class TransactionNode:
    """Node in a Doubly Linked List."""
    def __init__(self, ts, txn_type, amount, balance_after):
        self.timestamp = ts
        self.txn_type = txn_type
        self.amount = amount
        self.balance_after = balance_after
        self.prev = None
        self.next = None

class TransactionLedger:
    """Doubly Linked List for transaction logging."""
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, ts, txn_type, amount, balance_after):
        node = TransactionNode(ts, txn_type, amount, balance_after)
        if self.tail:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        else:
            self.head = self.tail = node

    def to_list(self):
        result, cur = [], self.head
        while cur:
            result.append(cur)
            cur = cur.next
        return result

def merge_sort(nodes):
    """Sorts nodes by newest timestamp first."""
    if len(nodes) <= 1:
        return nodes
    mid = len(nodes) // 2
    left = merge_sort(nodes[:mid])
    right = merge_sort(nodes[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i].timestamp >= right[j].timestamp:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ~~~~~~~~~ BANK SYSTEM CORE ~~~~~~~~~
class BankSystem:
    def __init__(self):
        self.accounts = {}      # acc_num -> {name, pin, balance, status}
        self.ledgers = {}       # acc_num -> TransactionLedger
        self.load_data()

    def load_data(self):
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        num, name, pin, bal, status = line.strip().split(SEP)
                        self.accounts[num] = {"name": name, "pin": pin, "balance": float(bal), "status": status}
        else:
            self.accounts = {
                "1000000001": {"name": "Juan dela Cruz", "pin": "1234", "balance": 15000.0, "status": "VERIFIED"},
                "1000000002": {"name": "Maria Santos", "pin": "4321", "balance": 8500.5, "status": "VERIFIED"}
            }
            self.save_all_accounts()

        if os.path.exists(TRANSACTIONS_FILE):
            with open(TRANSACTIONS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        num, t_type, amt, bal_after, ts = line.strip().split(SEP)
                        if num not in self.ledgers:
                            self.ledgers[num] = TransactionLedger()
                        self.ledgers[num].append(ts, t_type, float(amt), float(bal_after))

    def save_all_accounts(self):
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            f.write("# account_number|name|pin|balance|status\n")
            for num, data in self.accounts.items():
                f.write(f"{num}{SEP}{data['name']}{SEP}{data['pin']}{SEP}{data['balance']:.2f}{SEP}{data['status']}\n")

    def log_transaction(self, account_number, txn_type, amount, balance_after):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if account_number not in self.ledgers:
            self.ledgers[account_number] = TransactionLedger()
        
        # Append to Doubly Linked List
        self.ledgers[account_number].append(ts, txn_type, amount, balance_after)
        
        # Save to TRANSACTIONS_FILE
        with open(TRANSACTIONS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{account_number}{SEP}{txn_type}{SEP}{amount:.2f}{SEP}{balance_after:.2f}{SEP}{ts}\n")

    def register_user(self, name, pin, deposit):
        while True:
            num = "1" + "".join(random.choices(string.digits, k=9))
            if num not in self.accounts: break
            
        self.accounts[num] = {"name": name, "pin": pin, "balance": deposit, "status": "PENDING_VERIFICATION"}
        self.save_all_accounts()
        if deposit > 0:
            self.log_transaction(num, "DEPOSIT", deposit, deposit)
        return num


# ~~~~~~~~~ GUI INTERFACE ~~~~~~~~~
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.bank = BankSystem()
        self.current_user = None

        self.title("ATM Simulation")
        self.geometry("910x520")
        self.configure(bg=BG)

        self.left_frame = tk.Frame(self, bg=CARD, width=320, highlightthickness=1, highlightbackground=CARD2)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.left_frame.pack_propagate(False)

        self.right_frame = tk.Frame(self, bg=BG)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.build_auth_panel()
        self.show_welcome_dashboard()

    def make_label(self, parent, text, font=FONT_MONO, fg=TEXT, bg=CARD, **kwargs):
        return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kwargs)

    def make_entry(self, parent, show=None):
        return tk.Entry(parent, show=show, bg=CARD2, fg=ACCENT, insertbackground=ACCENT, font=FONT_MONO, relief="flat", highlightthickness=1, highlightbackground=CARD2)

    def make_btn(self, parent, text, cmd, bg=ACCENT, fg=BG):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, activebackground=ACCENT2, font=FONT_BOLD, relief="flat", cursor="hand2")

    def build_auth_panel(self):
        for widget in self.left_frame.winfo_children(): widget.destroy()
        self.make_label(self.left_frame, "🏦 TrustMyWalletBro", font=FONT_BOLD, fg=ACCENT).pack(pady=(20, 5))
        self.make_label(self.left_frame, "An Atomic Transaction Hub", font=FONT_MONO, fg=TEXT_DIM).pack(pady=(0, 20))

        if not self.current_user:
            self.make_label(self.left_frame, "Account Number").pack(anchor="w", padx=20)
            self.acc_entry = self.make_entry(self.left_frame); self.acc_entry.pack(fill="x", padx=20, pady=5)
            self.make_label(self.left_frame, "PIN Code").pack(anchor="w", padx=20)
            self.pin_entry = self.make_entry(self.left_frame, show="*"); self.pin_entry.pack(fill="x", padx=20, pady=5)
            self.make_btn(self.left_frame, "LOGIN ►", self.handle_login).pack(fill="x", padx=20, pady=15)
            tk.Frame(self.left_frame, bg=CARD2, height=1).pack(fill="x", padx=20, pady=15)
            self.make_btn(self.left_frame, "CREATE NEW ACCOUNT", self.build_register_panel, bg=CARD2, fg=TEXT).pack(fill="x", padx=20)
        else:
            data = self.bank.accounts[self.current_user]
            self.make_label(self.left_frame, f"User: {data['name']}", font=FONT_BOLD).pack(pady=10)
            self.make_label(self.left_frame, f"Acc No: {self.current_user}", fg=ACCENT2).pack()
            self.make_label(self.left_frame, f"Status: {data['status']}", fg=WARN if data['status'] == "PENDING_VERIFICATION" else ACCENT).pack(pady=5)
            if data['status'] == "PENDING_VERIFICATION":
                self.make_label(self.left_frame, "Account needs \nin-person verification. \nVisit us \nat our nearest branch!", fg=WARN).pack(pady=2)
            self.make_btn(self.left_frame, "🚪 EXIT", self.handle_logout, bg=DANGER, fg=TEXT).pack(side="bottom", fill="x", padx=20, pady=20)

    def build_register_panel(self):
        for widget in self.left_frame.winfo_children(): widget.destroy()
        self.make_label(self.left_frame, "✍️ REGISTER ACCOUNT", font=FONT_BOLD, fg=ACCENT2).pack(pady=15)
        self.make_label(self.left_frame, "Full Name").pack(anchor="w", padx=20)
        r_name = self.make_entry(self.left_frame); r_name.pack(fill="x", padx=20, pady=4)
        self.make_label(self.left_frame, "PIN (4 Digits)").pack(anchor="w", padx=20)
        r_pin = self.make_entry(self.left_frame, show="*"); r_pin.pack(fill="x", padx=20, pady=4)
        self.make_label(self.left_frame, "Initial Deposit (₱)").pack(anchor="w", padx=20)
        r_dep = self.make_entry(self.left_frame); r_dep.pack(fill="x", padx=20, pady=4)

        def submit():
            name, pin, dep = r_name.get().strip(), r_pin.get().strip(), r_dep.get().strip()
            if not name or len(pin) != 4 or not pin.isdigit():
                return messagebox.showerror("Error", "Provide a valid Name and 4-digit PIN.")
            try:
                amt = float(dep) if dep else 0.0
                if amt < 0: raise ValueError
            except ValueError:
                return messagebox.showerror("Error", "Invalid deposit amount.")
            num = self.bank.register_user(name, pin, amt)
            messagebox.showinfo("Success", f"Account created!\nAccount Number: {num}\nStatus: PENDING_VERIFICATION.")
            self.build_auth_panel()

        self.make_btn(self.left_frame, "SUBMIT INFO", submit).pack(fill="x", padx=20, pady=10)
        self.make_btn(self.left_frame, "◀ BACK TO LOGIN", self.build_auth_panel, bg=CARD2, fg=TEXT).pack(fill="x", padx=20)

    def show_welcome_dashboard(self):
        for widget in self.right_frame.winfo_children(): widget.destroy()
        welcome_box = tk.Frame(self.right_frame, bg=CARD, highlightthickness=1, highlightbackground=CARD2)
        welcome_box.place(relx=0.5, rely=0.5, anchor="center", width=400, height=200)
        self.make_label(welcome_box, "ATM Algorithmic Terminal", font=FONT_BOLD, bg=CARD).pack(pady=30)
        self.make_label(welcome_box, "Please authenticate on the left column panel.", fg=TEXT_DIM, bg=CARD).pack()

    def refresh_user_dashboard(self):
        for widget in self.right_frame.winfo_children(): widget.destroy()
        user_data = self.bank.accounts[self.current_user]
        
        b_card = tk.Frame(self.right_frame, bg=CARD, highlightthickness=1, highlightbackground=CARD2)
        b_card.pack(fill="x", pady=(0, 15))
        self.make_label(b_card, "AVAILABLE BALANCE", font=FONT_MONO, fg=TEXT_DIM, bg=CARD).pack(anchor="w", padx=15, pady=(10, 0))
        self.bal_label = self.make_label(b_card, f"₱{user_data['balance']:,.2f}", font=("Cascadia Code", 28, "bold"), fg=ACCENT, bg=CARD)
        self.bal_label.pack(anchor="w", padx=15, pady=(0, 10))

        act_strip = tk.Frame(self.right_frame, bg=BG)
        act_strip.pack(fill="x", pady=5)
        self.make_label(act_strip, "Amount: ", bg=BG).pack(side="left")
        val_entry = self.make_entry(act_strip); val_entry.pack(side="left", padx=5, ipady=3)

        def trigger_mutation(txn_type):
            try:
                val = float(val_entry.get().strip())
                if val <= 0: raise ValueError
            except ValueError:
                return messagebox.showerror("Failed", "Please input a positive value.")

            if txn_type == "WITHDRAW" and val > user_data["balance"]:
                return messagebox.showerror("Declined", "Insufficient liquidity.")

            user_data["balance"] += val if txn_type == "DEPOSIT" else -val
            self.bank.save_all_accounts()
            self.bank.log_transaction(self.current_user, txn_type, val, user_data["balance"])
            
            val_entry.delete(0, tk.END)
            self.bal_label.config(text=f"₱{user_data['balance']:,.2f}")
            build_history_tree()

        self.make_btn(act_strip, "➕ DEPOSIT", lambda: trigger_mutation("DEPOSIT")).pack(side="left", padx=5)
        self.make_btn(act_strip, "➖ WITHDRAW", lambda: trigger_mutation("WITHDRAW"), bg=ACCENT2, fg=TEXT).pack(side="left", padx=5)

        tree_frame = tk.Frame(self.right_frame, bg=CARD)
        tree_frame.pack(fill="both", expand=True, pady=(10, 0))

        cols = ("Timestamp", "Transaction", "ΔValue", "Running Balance")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)
        tree.pack(side="left", fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, rowheight=24, font=FONT_MONO)
        style.configure("Treeview.Heading", background=CARD2, foreground=ACCENT, font=FONT_MONO)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=110, anchor="center")

        def build_history_tree():
            for i in tree.get_children(): tree.delete(i)
            
            # 1. Fetch data from the Doubly Linked List if it exists
            ledger = self.bank.ledgers.get(self.current_user, TransactionLedger())
            raw_nodes_list = ledger.to_list()
            
            # 2. Run Merge Sort function (newest timestamp first)
            sorted_nodes = merge_sort(raw_nodes_list)
            
            # 3. Populate Treeview
            for node in sorted_nodes:
                sign = "+" if node.txn_type == "DEPOSIT" else "-"
                tree.insert("", "end", values=(
                    node.timestamp, 
                    node.txn_type, 
                    f"{sign}₱{node.amount:,.2f}", 
                    f"₱{node.balance_after:,.2f}"
                ))

        build_history_tree()

    def handle_login(self):
        acc, pin = self.acc_entry.get().strip(), self.pin_entry.get().strip()
        if acc in self.bank.accounts and self.bank.accounts[acc]["pin"] == pin:
            self.current_user = acc
            self.build_auth_panel()
            self.refresh_user_dashboard()
        else:
            messagebox.showerror("Auth Failure", "Invalid credentials.")

    def handle_logout(self):
        self.current_user = None
        self.build_auth_panel()
        self.show_welcome_dashboard()

if __name__ == "__main__":
    App().mainloop()
