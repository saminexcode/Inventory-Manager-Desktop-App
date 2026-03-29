"""
======================================================
  INVENTORY MANAGEMENT SYSTEM
  Built by: Sami Ullah Alimi | @saminexcode
  Tech: Python + Tkinter + SQLite (MySQL-ready)
======================================================
  FEATURES:
  - Add / Edit / Delete products
  - Search & filter inventory
  - Sales tracking
  - Low stock alerts
  - Reports & statistics
  - MySQL-ready (just swap sqlite3 for mysql.connector)
======================================================
  HOW TO RUN:
  python project4_inventory.py
  
  Requirements: Python 3.x (Tkinter included)
  For MySQL: pip install mysql-connector-python
======================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
from datetime import datetime
import random

# ─── DATABASE SETUP ────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            quantity INTEGER DEFAULT 0,
            price REAL DEFAULT 0.0,
            supplier TEXT,
            min_stock INTEGER DEFAULT 5,
            added_date TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            product_name TEXT,
            quantity INTEGER,
            total_price REAL,
            sale_date TEXT
        )
    """)
    # Insert sample data if empty
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        samples = [
            ("Laptop Dell XPS", "Electronics", 15, 85000, "Dell Inc.", 3),
            ("Mouse Wireless", "Electronics", 42, 1200, "Logitech", 10),
            ("Keyboard USB", "Electronics", 38, 800, "HP", 10),
            ("A4 Paper Ream", "Stationery", 120, 250, "CamPaper", 20),
            ("Monitor 24inch", "Electronics", 8, 45000, "Samsung", 2),
            ("USB Hub 4-Port", "Electronics", 25, 600, "Anker", 5),
            ("Notebook", "Stationery", 5, 80, "Local", 15),  # Low stock!
            ("Printer Ink Black", "Consumable", 30, 900, "HP", 8),
            ("HDMI Cable 2m", "Accessories", 45, 400, "Generic", 10),
            ("Chair Office", "Furniture", 3, 15000, "LocalMart", 2),  # Low stock!
        ]
        for s in samples:
            c.execute(
                "INSERT INTO products (name, category, quantity, price, supplier, min_stock, added_date) VALUES (?,?,?,?,?,?,?)",
                (*s, datetime.now().strftime("%Y-%m-%d"))
            )
    conn.commit()
    conn.close()

# ─── COLORS & STYLE ────────────────────────────────────────
BG      = "#0f0f17"
SIDEBAR = "#161620"
CARD    = "#1e1e2a"
BORDER  = "#2a2a38"
ACCENT  = "#00d4aa"
ACCENT2 = "#7c6fff"
DANGER  = "#e85d4a"
WARN    = "#f5a623"
TEXT    = "#e8e8f0"
MUTED   = "#888899"
WHITE   = "#ffffff"
SUCCESS = "#2ecc71"

# ─── MAIN APP ──────────────────────────────────────────────
class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Manager Pro — @saminexcode")
        self.geometry("1200x720")
        self.minsize(1000, 600)
        self.configure(bg=BG)
        init_db()
        self.current_page = tk.StringVar(value="dashboard")
        self.build_ui()
        self.show_page("dashboard")

    def build_ui(self):
        # ── Sidebar ──
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(self.sidebar, bg=SIDEBAR, pady=20)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="📦", font=("Segoe UI", 24), bg=SIDEBAR, fg=ACCENT).pack()
        tk.Label(logo_frame, text="InvenPro", font=("Segoe UI", 14, "bold"), bg=SIDEBAR, fg=WHITE).pack()
        tk.Label(logo_frame, text="@saminexcode", font=("Segoe UI", 8), bg=SIDEBAR, fg=MUTED).pack()

        # Divider
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=15)

        # Nav buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "🏠", "Dashboard"),
            ("products",  "📋", "Products"),
            ("add",       "➕", "Add Product"),
            ("sales",     "💰", "Sales"),
        ]
        nav_frame = tk.Frame(self.sidebar, bg=SIDEBAR, pady=10)
        nav_frame.pack(fill="x")
        for key, icon, label in nav_items:
            btn = tk.Button(
                nav_frame, text=f"  {icon}  {label}",
                font=("Segoe UI", 10), bg=SIDEBAR, fg=MUTED,
                activebackground=CARD, activeforeground=ACCENT,
                bd=0, padx=20, pady=12, anchor="w", cursor="hand2",
                command=lambda k=key: self.show_page(k)
            )
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        # User info at bottom
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=15, side="bottom", pady=10)
        user_frame = tk.Frame(self.sidebar, bg=SIDEBAR, pady=10)
        user_frame.pack(side="bottom", fill="x")
        tk.Label(user_frame, text="👤 Sami Ullah", font=("Segoe UI", 9, "bold"), bg=SIDEBAR, fg=TEXT).pack()
        tk.Label(user_frame, text="Admin", font=("Segoe UI", 8), bg=SIDEBAR, fg=MUTED).pack()

        # ── Main area ──
        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

        # Top bar
        topbar = tk.Frame(self.main, bg=CARD, height=55)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        self.page_title_lbl = tk.Label(topbar, text="Dashboard", font=("Segoe UI", 14, "bold"), bg=CARD, fg=WHITE, padx=20)
        self.page_title_lbl.pack(side="left", pady=10)
        tk.Label(topbar, text=datetime.now().strftime("📅 %A, %d %B %Y"), font=("Segoe UI", 9), bg=CARD, fg=MUTED, padx=20).pack(side="right", pady=10)

        # Content area
        self.content = tk.Frame(self.main, bg=BG)
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def set_active_nav(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.config(bg=CARD, fg=ACCENT)
            else:
                btn.config(bg=SIDEBAR, fg=MUTED)

    def show_page(self, key):
        self.set_active_nav(key)
        titles = {"dashboard":"Dashboard","products":"Products","add":"Add Product","sales":"Sales"}
        self.page_title_lbl.config(text=titles.get(key,""))
        self.clear_content()
        if key == "dashboard": self.page_dashboard()
        elif key == "products": self.page_products()
        elif key == "add": self.page_add()
        elif key == "sales": self.page_sales()

    # ── DASHBOARD ──────────────────────────────────────────
    def page_dashboard(self):
        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()
        total_products = c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        total_stock    = c.execute("SELECT SUM(quantity) FROM products").fetchone()[0] or 0
        total_value    = c.execute("SELECT SUM(quantity * price) FROM products").fetchone()[0] or 0
        low_stock      = c.execute("SELECT COUNT(*) FROM products WHERE quantity <= min_stock").fetchone()[0]
        total_sales    = c.execute("SELECT SUM(total_price) FROM sales").fetchone()[0] or 0
        conn.close()

        # Stat cards
        stats_row = tk.Frame(self.content, bg=BG)
        stats_row.pack(fill="x", pady=(0,15))
        stats = [
            ("📦", "Total Products",  str(total_products),  ACCENT),
            ("📊", "Total Items",     f"{total_stock:,}",    ACCENT2),
            ("💵", "Stock Value",     f"₹{total_value:,.0f}",SUCCESS),
            ("⚠️", "Low Stock",       str(low_stock),       DANGER if low_stock > 0 else MUTED),
        ]
        for icon, label, val, color in stats:
            card = tk.Frame(stats_row, bg=CARD, padx=18, pady=15)
            card.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(card, text=icon, font=("Segoe UI", 18), bg=CARD, fg=color).pack(anchor="w")
            tk.Label(card, text=val, font=("Segoe UI", 20, "bold"), bg=CARD, fg=WHITE).pack(anchor="w")
            tk.Label(card, text=label, font=("Segoe UI", 9), bg=CARD, fg=MUTED).pack(anchor="w")

        # Low stock alert
        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()
        low_items = c.execute("SELECT name, quantity, min_stock FROM products WHERE quantity <= min_stock").fetchall()
        conn.close()

        if low_items:
            alert = tk.Frame(self.content, bg="#2a1a1a", pady=10, padx=15)
            alert.pack(fill="x", pady=(0,15))
            tk.Label(alert, text=f"⚠️  Low Stock Alert — {len(low_items)} item(s) need restocking", font=("Segoe UI", 10, "bold"), bg="#2a1a1a", fg=WARN).pack(anchor="w")
            for item in low_items:
                tk.Label(alert, text=f"     • {item[0]}: {item[1]} units left (min: {item[2]})", font=("Segoe UI", 9), bg="#2a1a1a", fg=MUTED).pack(anchor="w")

        # Recent products table
        tk.Label(self.content, text="Recent Products", font=("Segoe UI", 11, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(0,8))
        self._build_table(self.content, limit=6)

    # ── PRODUCTS ───────────────────────────────────────────
    def page_products(self):
        # Search row
        top = tk.Frame(self.content, bg=BG)
        top.pack(fill="x", pady=(0,12))
        tk.Label(top, text="Search:", font=("Segoe UI", 10), bg=BG, fg=MUTED).pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(top, textvariable=self.search_var, font=("Segoe UI", 10), bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat", bd=5, width=30)
        search_entry.pack(side="left", padx=8)
        search_entry.bind("<KeyRelease>", lambda e: self._refresh_products())
        tk.Button(top, text="➕ Add New", font=("Segoe UI", 9, "bold"), bg=ACCENT, fg="#0a0a0f", relief="flat", padx=12, pady=5, cursor="hand2", command=lambda: self.show_page("add")).pack(side="right")

        # Table
        self.prod_table_frame = tk.Frame(self.content, bg=BG)
        self.prod_table_frame.pack(fill="both", expand=True)
        self._refresh_products()

    def _refresh_products(self):
        for w in self.prod_table_frame.winfo_children():
            w.destroy()
        search = getattr(self, 'search_var', tk.StringVar()).get().lower()
        self._build_table(self.prod_table_frame, search=search, editable=True)

    def _build_table(self, parent, limit=None, search="", editable=False):
        cols = ("ID","Product Name","Category","Qty","Price (₹)","Supplier","Status")
        tree_frame = tk.Frame(parent, bg=BG)
        tree_frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, rowheight=32, font=("Segoe UI", 9))
        style.configure("Custom.Treeview.Heading", background=SIDEBAR, foreground=MUTED, font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Custom.Treeview", background=[("selected", ACCENT2)])

        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", style="Custom.Treeview")
        widths = [50, 200, 120, 60, 100, 140, 80]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center" if col not in ("Product Name","Supplier") else "w")

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()
        query = "SELECT id,name,category,quantity,price,supplier,min_stock FROM products"
        if search:
            query += f" WHERE lower(name) LIKE '%{search}%' OR lower(category) LIKE '%{search}%'"
        if limit:
            query += f" LIMIT {limit}"
        rows = c.execute(query).fetchall()
        conn.close()

        for r in rows:
            status = "🔴 Low" if r[3] <= r[6] else "🟢 OK"
            vals = (r[0], r[1], r[2] or "-", r[3], f"{r[4]:,.0f}", r[5] or "-", status)
            tree.insert("", "end", values=vals)

        if editable:
            action_frame = tk.Frame(parent, bg=BG, pady=8)
            action_frame.pack(fill="x")
            def delete_selected():
                sel = tree.selection()
                if not sel:
                    messagebox.showwarning("Select", "Please select a product to delete.")
                    return
                pid = tree.item(sel[0])["values"][0]
                if messagebox.askyesno("Delete", f"Delete product ID {pid}?"):
                    conn = sqlite3.connect("inventory.db")
                    conn.cursor().execute("DELETE FROM products WHERE id=?", (pid,))
                    conn.commit(); conn.close()
                    self._refresh_products()
            tk.Button(action_frame, text="🗑 Delete Selected", font=("Segoe UI", 9), bg="#2a1515", fg=DANGER, relief="flat", padx=12, pady=6, cursor="hand2", command=delete_selected).pack(side="right")

    # ── ADD PRODUCT ────────────────────────────────────────
    def page_add(self):
        wrap = tk.Frame(self.content, bg=CARD, padx=30, pady=25)
        wrap.pack(fill="both", expand=False, padx=0, pady=0, ipadx=10, ipady=10)
        tk.Label(wrap, text="Add New Product", font=("Segoe UI", 13, "bold"), bg=CARD, fg=WHITE).pack(anchor="w", pady=(0,18))

        fields = [("Product Name *", "name"), ("Category", "category"), ("Quantity *", "qty"), ("Price (₹) *", "price"), ("Supplier", "supplier"), ("Min. Stock Alert", "min_stock")]
        self.form_vars = {}
        for label, key in fields:
            row = tk.Frame(wrap, bg=CARD)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=("Segoe UI", 9), bg=CARD, fg=MUTED, width=18, anchor="w").pack(side="left")
            var = tk.StringVar()
            self.form_vars[key] = var
            e = tk.Entry(row, textvariable=var, font=("Segoe UI", 10), bg=BG, fg=TEXT, insertbackground=TEXT, relief="flat", bd=6, width=32)
            e.pack(side="left")

        tk.Frame(wrap, bg=BORDER, height=1).pack(fill="x", pady=15)
        def save():
            name = self.form_vars["name"].get().strip()
            qty  = self.form_vars["qty"].get().strip()
            price= self.form_vars["price"].get().strip()
            if not name or not qty or not price:
                messagebox.showerror("Error", "Name, Quantity, and Price are required.")
                return
            try: qty = int(qty); price = float(price)
            except: messagebox.showerror("Error", "Quantity must be integer, Price must be a number."); return
            conn = sqlite3.connect("inventory.db")
            conn.cursor().execute(
                "INSERT INTO products (name,category,quantity,price,supplier,min_stock,added_date) VALUES (?,?,?,?,?,?,?)",
                (name, self.form_vars["category"].get(), qty, price, self.form_vars["supplier"].get(),
                 int(self.form_vars["min_stock"].get() or 5), datetime.now().strftime("%Y-%m-%d"))
            )
            conn.commit(); conn.close()
            messagebox.showinfo("Success", f"✅ '{name}' added to inventory!")
            self.show_page("products")

        tk.Button(wrap, text="💾 Save Product", font=("Segoe UI", 10, "bold"), bg=ACCENT, fg="#0a0a0f", relief="flat", padx=20, pady=8, cursor="hand2", command=save).pack(anchor="w")

    # ── SALES ──────────────────────────────────────────────
    def page_sales(self):
        top = tk.Frame(self.content, bg=BG)
        top.pack(fill="x", pady=(0,12))

        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()
        products = c.execute("SELECT id, name, price, quantity FROM products ORDER BY name").fetchall()
        conn.close()

        tk.Label(top, text="Record a Sale", font=("Segoe UI", 11, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(0,10))
        form = tk.Frame(self.content, bg=CARD, padx=20, pady=15)
        form.pack(fill="x", pady=(0,15))

        tk.Label(form, text="Product:", font=("Segoe UI", 9), bg=CARD, fg=MUTED).pack(side="left")
        prod_var = tk.StringVar()
        prod_names = [f"{p[0]} — {p[1]} (₹{p[2]:,.0f})" for p in products]
        combo = ttk.Combobox(form, textvariable=prod_var, values=prod_names, font=("Segoe UI", 9), state="readonly", width=35)
        combo.pack(side="left", padx=8)
        tk.Label(form, text="Qty:", font=("Segoe UI", 9), bg=CARD, fg=MUTED).pack(side="left")
        qty_var = tk.StringVar(value="1")
        tk.Entry(form, textvariable=qty_var, font=("Segoe UI", 9), bg=BG, fg=TEXT, insertbackground=TEXT, relief="flat", bd=5, width=6).pack(side="left", padx=4)

        def record_sale():
            if not prod_var.get():
                messagebox.showwarning("Select", "Please select a product.")
                return
            pid = int(prod_var.get().split("—")[0].strip())
            try: qty = int(qty_var.get())
            except: messagebox.showerror("Error", "Enter a valid quantity."); return
            conn = sqlite3.connect("inventory.db")
            c = conn.cursor()
            row = c.execute("SELECT name, price, quantity FROM products WHERE id=?", (pid,)).fetchone()
            if row[2] < qty:
                messagebox.showerror("Out of Stock", f"Only {row[2]} units available.")
                conn.close(); return
            total = row[1] * qty
            c.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (qty, pid))
            c.execute("INSERT INTO sales (product_id, product_name, quantity, total_price, sale_date) VALUES (?,?,?,?,?)", (pid, row[0], qty, total, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit(); conn.close()
            messagebox.showinfo("Sale Recorded", f"✅ Sold {qty}x {row[0]} — Total: ₹{total:,.0f}")
            self.page_sales()

        tk.Button(form, text="✅ Record Sale", font=("Segoe UI", 9, "bold"), bg=SUCCESS, fg="#0a0a0f", relief="flat", padx=12, pady=5, cursor="hand2", command=record_sale).pack(side="left", padx=8)

        # Sales history
        tk.Label(self.content, text="Sales History", font=("Segoe UI", 11, "bold"), bg=BG, fg=TEXT).pack(anchor="w", pady=(0,8))
        cols = ("ID","Product","Qty Sold","Total (₹)","Date")
        style = ttk.Style(); style.theme_use("clam")
        style.configure("Custom.Treeview", background=CARD, foreground=TEXT, fieldbackground=CARD, rowheight=30, font=("Segoe UI", 9))
        style.configure("Custom.Treeview.Heading", background=SIDEBAR, foreground=MUTED, font=("Segoe UI", 9, "bold"), relief="flat")

        frame2 = tk.Frame(self.content, bg=BG)
        frame2.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame2, columns=cols, show="headings", style="Custom.Treeview")
        for col, w in zip(cols, [50,250,80,120,160]):
            tree.heading(col, text=col); tree.column(col, width=w, anchor="center")
        sb2 = ttk.Scrollbar(frame2, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb2.set)
        tree.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")

        conn = sqlite3.connect("inventory.db")
        rows = conn.cursor().execute("SELECT id, product_name, quantity, total_price, sale_date FROM sales ORDER BY id DESC LIMIT 30").fetchall()
        conn.close()
        for r in rows:
            tree.insert("", "end", values=(r[0], r[1], r[2], f"{r[3]:,.0f}", r[4]))

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
