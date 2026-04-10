# plugins/finance_tools.py — Finance, Budget, Investment & Currency Tools

import os, json, math, random
from datetime import datetime, timedelta, date
from database import _c


# ══ DB INIT ═══════════════════════════════════════════════════════════════════
def _init():
    with _c() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS budget(id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT, limit_amount REAL, month TEXT);
        CREATE TABLE IF NOT EXISTS investments(id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT, shares REAL, buy_price REAL, buy_date TEXT,
            note TEXT, created TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS bills(id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, amount REAL, due_day INTEGER, recurring INTEGER DEFAULT 1,
            paid INTEGER DEFAULT 0, created TEXT DEFAULT(datetime('now')));
        CREATE TABLE IF NOT EXISTS savings_goals(id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, target REAL, current REAL DEFAULT 0,
            deadline TEXT, created TEXT DEFAULT(datetime('now')));
        """)
_init()


# ══ CURRENCY CONVERTER ════════════════════════════════════════════════════════
def currency_convert(amount, from_cur, to_cur):
    try:
        import requests
        r = requests.get(
            f"https://api.exchangerate-api.com/v4/latest/{from_cur.upper()}",
            timeout=10
        ).json()
        rate = r["rates"].get(to_cur.upper())
        if not rate:
            return f"Unknown currency: {to_cur}"
        result = float(amount) * rate
        return f"💱 {amount} {from_cur.upper()} = {result:.2f} {to_cur.upper()}"
    except Exception as e:
        return f"Currency error: {e}"

def currency_list():
    MAJOR = {
        "INR":"Indian Rupee","USD":"US Dollar","EUR":"Euro","GBP":"British Pound",
        "JPY":"Japanese Yen","AUD":"Australian Dollar","CAD":"Canadian Dollar",
        "CHF":"Swiss Franc","CNY":"Chinese Yuan","SGD":"Singapore Dollar",
        "AED":"UAE Dirham","SAR":"Saudi Riyal","BDT":"Bangladeshi Taka",
    }
    lines = [f"  {code}: {name}" for code,name in MAJOR.items()]
    return "Major Currencies:\n" + "\n".join(lines)


# ══ LOAN & EMI CALCULATORS ════════════════════════════════════════════════════
def emi_calculator(principal, annual_rate, years):
    P = float(principal)
    r = float(annual_rate) / 100 / 12
    n = int(years) * 12
    if r == 0:
        emi = P / n
    else:
        emi = P * r * (1+r)**n / ((1+r)**n - 1)
    total = emi * n
    interest = total - P
    return (f"💳 EMI Calculator:\n"
            f"  Principal    : ₹{P:,.2f}\n"
            f"  Monthly EMI  : ₹{emi:,.2f}\n"
            f"  Total Payment: ₹{total:,.2f}\n"
            f"  Total Interest: ₹{interest:,.2f}\n"
            f"  Duration     : {n} months ({years} years)")

def loan_amortization(principal, annual_rate, years, show_months=6):
    P = float(principal); r = float(annual_rate)/100/12; n = int(years)*12
    if r == 0: emi = P/n
    else: emi = P * r*(1+r)**n / ((1+r)**n - 1)
    balance = P
    lines = [f"  {'Month':>5}  {'EMI':>12}  {'Principal':>12}  {'Interest':>12}  {'Balance':>14}"]
    lines.append("  " + "-"*65)
    for month in range(1, min(n+1, show_months+1)):
        interest_part  = balance * r
        principal_part = emi - interest_part
        balance       -= principal_part
        lines.append(f"  {month:>5}  ₹{emi:>11,.2f}  ₹{principal_part:>11,.2f}  "
                     f"₹{interest_part:>11,.2f}  ₹{max(balance,0):>13,.2f}")
    return f"📊 Loan Amortization (first {show_months} months):\n" + "\n".join(lines)

def simple_interest(principal, rate, years):
    P,R,T = float(principal), float(rate), float(years)
    SI = P * R * T / 100
    return (f"Simple Interest:\n"
            f"  Principal: ₹{P:,.2f}\n"
            f"  SI       : ₹{SI:,.2f}\n"
            f"  Total    : ₹{P+SI:,.2f}")

def compound_interest(principal, rate, years, n=12):
    P,r,t,n = float(principal), float(rate)/100, float(years), int(n)
    A = P * (1 + r/n)**(n*t)
    CI = A - P
    return (f"Compound Interest (compounded {n}x/year):\n"
            f"  Principal: ₹{P:,.2f}\n"
            f"  CI       : ₹{CI:,.2f}\n"
            f"  Total    : ₹{A:,.2f}")


# ══ INVESTMENT TOOLS ══════════════════════════════════════════════════════════
def sip_calculator(monthly, rate, years):
    r = float(rate)/100/12; n = int(years)*12; m = float(monthly)
    if r == 0:
        fv = m * n
    else:
        fv = m * ((1+r)**n - 1) / r * (1+r)
    invested = m * n
    returns  = fv - invested
    return (f"📈 SIP Calculator:\n"
            f"  Monthly SIP : ₹{m:,.2f}\n"
            f"  Duration    : {years} years ({n} months)\n"
            f"  Invested    : ₹{invested:,.2f}\n"
            f"  Returns     : ₹{returns:,.2f}\n"
            f"  Final Value : ₹{fv:,.2f}\n"
            f"  XIRR (approx): {rate}% p.a.")

def ppf_calculator(annual, years=15, rate=7.1):
    total = 0; year_data = []
    for y in range(1, int(years)+1):
        total = (total + float(annual)) * (1 + float(rate)/100)
        year_data.append((y, total))
    return (f"🏦 PPF Calculator ({years} years @ {rate}%):\n"
            f"  Annual deposit : ₹{annual:,.2f}\n"
            f"  Total invested : ₹{float(annual)*years:,.2f}\n"
            f"  Maturity value : ₹{total:,.2f}\n"
            f"  Wealth gained  : ₹{total - float(annual)*years:,.2f}")

def fd_calculator(principal, rate, years, compound="quarterly"):
    P = float(principal); r = float(rate)/100; t = float(years)
    n_map = {"monthly":12,"quarterly":4,"half-yearly":2,"yearly":1}
    n = n_map.get(compound.lower(), 4)
    A = P * (1 + r/n)**(n*t)
    return (f"🏦 FD Calculator ({compound}):\n"
            f"  Principal : ₹{P:,.2f}\n"
            f"  Rate      : {rate}% p.a.\n"
            f"  Duration  : {years} years\n"
            f"  Maturity  : ₹{A:,.2f}\n"
            f"  Interest  : ₹{A-P:,.2f}")

def roi_calculator(invested, returns):
    roi = (float(returns) - float(invested)) / float(invested) * 100
    return (f"📊 ROI:\n"
            f"  Invested : ₹{float(invested):,.2f}\n"
            f"  Returns  : ₹{float(returns):,.2f}\n"
            f"  ROI      : {roi:+.2f}%\n"
            f"  Status   : {'Profit 📈' if roi>0 else 'Loss 📉'}")

def breakeven_calculator(fixed_cost, variable_cost, selling_price):
    FC = float(fixed_cost); VC = float(variable_cost); SP = float(selling_price)
    if SP <= VC: return "Selling price must be greater than variable cost."
    units = FC / (SP - VC)
    revenue = units * SP
    return (f"📊 Break-Even Analysis:\n"
            f"  Fixed Cost    : ₹{FC:,.2f}\n"
            f"  Variable Cost : ₹{VC:,.2f}/unit\n"
            f"  Selling Price : ₹{SP:,.2f}/unit\n"
            f"  Break-Even    : {units:.0f} units\n"
            f"  Revenue needed: ₹{revenue:,.2f}")

def inflation_calculator(amount, rate, years):
    future = float(amount) * (1 + float(rate)/100)**float(years)
    lost   = future - float(amount)
    return (f"📉 Inflation Impact:\n"
            f"  Today's value : ₹{float(amount):,.2f}\n"
            f"  After {years} years @ {rate}% inflation:\n"
            f"  Future cost   : ₹{future:,.2f}\n"
            f"  Purchasing power lost: ₹{lost:,.2f}")

def retirement_calculator(current_age, retirement_age, monthly_expense, inflation=6.0, return_rate=12.0):
    years_to_retire  = int(retirement_age) - int(current_age)
    years_in_retire  = 25  # assumed post-retirement life
    monthly_expense_at_retire = float(monthly_expense) * (1 + float(inflation)/100)**years_to_retire
    annual_needed    = monthly_expense_at_retire * 12
    corpus_needed    = annual_needed / (float(return_rate)/100 - float(inflation)/100) * (
                       1 - (1 + float(inflation)/100)**(-years_in_retire) / (1 + float(return_rate)/100)**(-years_in_retire))
    monthly_sip      = corpus_needed * (float(return_rate)/100/12) / ((1 + float(return_rate)/100/12)**(years_to_retire*12) - 1)
    return (f"🎯 Retirement Planner:\n"
            f"  Current age      : {current_age}\n"
            f"  Retirement age   : {retirement_age}\n"
            f"  Years to save    : {years_to_retire}\n"
            f"  Monthly expense now: ₹{float(monthly_expense):,.2f}\n"
            f"  At retirement    : ₹{monthly_expense_at_retire:,.2f}/month\n"
            f"  Corpus needed    : ₹{corpus_needed:,.2f}\n"
            f"  Monthly SIP now  : ₹{monthly_sip:,.2f}")


# ══ BUDGET MANAGER ════════════════════════════════════════════════════════════
def set_budget(category, amount):
    month = datetime.now().strftime("%Y-%m")
    with _c() as c:
        c.execute("INSERT OR REPLACE INTO budget(category,limit_amount,month) VALUES(?,?,?)",
                  (category.lower(), float(amount), month))
    return f"💰 Budget set: {category} = ₹{float(amount):,.2f}/month"

def show_budget():
    month = datetime.now().strftime("%Y-%m")
    with _c() as c:
        budgets = c.execute("SELECT * FROM budget WHERE month=?", (month,)).fetchall()
        expenses= c.execute(
            "SELECT category, SUM(amount) as total FROM expenses "
            "WHERE strftime('%Y-%m',timestamp)=? GROUP BY category", (month,)
        ).fetchall()
    if not budgets: return "No budget set for this month. Use 'set budget food 5000'."
    spent_map = {r["category"]: r["total"] for r in expenses}
    lines = []
    for b in budgets:
        cat   = b["category"]; limit = b["limit_amount"]
        spent = spent_map.get(cat, 0)
        pct   = spent/limit*100 if limit>0 else 0
        bar   = "█"*int(min(pct,100)/5) + "░"*(20-int(min(pct,100)/5))
        status= "⚠️ OVER!" if pct>100 else "✅"
        lines.append(f"  {cat:<20} [{bar}] ₹{spent:.0f}/₹{limit:.0f} ({pct:.0f}%) {status}")
    return f"💰 Budget — {month}:\n" + "\n".join(lines)


# ══ BILL TRACKER ══════════════════════════════════════════════════════════════
def add_bill(name, amount, due_day):
    with _c() as c:
        c.execute("INSERT INTO bills(name,amount,due_day) VALUES(?,?,?)",
                  (name, float(amount), int(due_day)))
    return f"📅 Bill added: {name} ₹{float(amount):,.2f} due on day {due_day}"

def show_bills():
    with _c() as c:
        rows = c.execute("SELECT * FROM bills WHERE recurring=1 ORDER BY due_day").fetchall()
    if not rows: return "No bills tracked."
    today = datetime.now().day
    lines = []
    for r in rows:
        days_left = r["due_day"] - today
        status = f"DUE IN {days_left}d" if days_left > 0 else "⚠️ OVERDUE"
        lines.append(f"  {'✅' if r['paid'] else '📅'} {r['name']:<25} ₹{r['amount']:>8,.2f}  Day {r['due_day']:>2}  {status}")
    total = sum(r["amount"] for r in rows)
    return f"📅 Monthly Bills (Total: ₹{total:,.2f}):\n" + "\n".join(lines)

def mark_bill_paid(name):
    with _c() as c:
        c.execute("UPDATE bills SET paid=1 WHERE LOWER(name)=?", (name.lower(),))
    return f"✅ Bill marked paid: {name}"


# ══ SAVINGS GOALS ════════════════════════════════════════════════════════════
def add_savings_goal(name, target, deadline=""):
    with _c() as c:
        c.execute("INSERT INTO savings_goals(name,target,deadline) VALUES(?,?,?)",
                  (name, float(target), deadline))
    return f"🎯 Savings goal: {name} = ₹{float(target):,.2f}"

def update_savings(name, amount):
    with _c() as c:
        c.execute("UPDATE savings_goals SET current=current+? WHERE LOWER(name)=?",
                  (float(amount), name.lower()))
    return f"💰 Added ₹{float(amount):,.2f} to '{name}'"

def show_savings_goals():
    with _c() as c:
        rows = c.execute("SELECT * FROM savings_goals ORDER BY id").fetchall()
    if not rows: return "No savings goals."
    lines = []
    for r in rows:
        pct = r["current"]/r["target"]*100 if r["target"]>0 else 0
        bar = "█"*int(min(pct,100)/5) + "░"*(20-int(min(pct,100)/5))
        lines.append(f"  {r['name']:<25} [{bar}] ₹{r['current']:,.0f}/₹{r['target']:,.0f} ({pct:.0f}%)")
    return "🎯 Savings Goals:\n" + "\n".join(lines)


# ══ PORTFOLIO TRACKER ════════════════════════════════════════════════════════
def add_investment(symbol, shares, buy_price, note=""):
    with _c() as c:
        c.execute("INSERT INTO investments(symbol,shares,buy_price,buy_date,note) VALUES(?,?,?,?,?)",
                  (symbol.upper(), float(shares), float(buy_price), date.today().isoformat(), note))
    cost = float(shares)*float(buy_price)
    return f"📈 Investment added: {shares}x {symbol.upper()} @ ₹{float(buy_price):,.2f} (Cost: ₹{cost:,.2f})"

def show_portfolio():
    with _c() as c:
        rows = c.execute("SELECT * FROM investments ORDER BY symbol").fetchall()
    if not rows: return "Portfolio is empty."
    total_cost = sum(r["shares"]*r["buy_price"] for r in rows)
    lines = [f"  {'Symbol':<10} {'Shares':>8}  {'Buy Price':>12}  {'Cost':>14}"]
    lines.append("  " + "-"*55)
    for r in rows:
        cost = r["shares"] * r["buy_price"]
        lines.append(f"  {r['symbol']:<10} {r['shares']:>8.2f}  ₹{r['buy_price']:>11,.2f}  ₹{cost:>13,.2f}")
    lines.append("  " + "-"*55)
    lines.append(f"  {'TOTAL':<10} {'':>8}  {'':>12}  ₹{total_cost:>13,.2f}")
    return "📊 Portfolio:\n" + "\n".join(lines)


# ══ TAX CALCULATOR (India) ════════════════════════════════════════════════════
def income_tax_india(income, regime="new"):
    income = float(income)
    if regime.lower() == "new":
        slabs = [(300000,0),(300000,5),(300000,10),(300000,15),(300000,20),(float('inf'),30)]
    else:
        slabs = [(250000,0),(250000,5),(500000,20),(float('inf'),30)]
    tax = 0; remaining = income; lines = []
    for slab, rate in slabs:
        taxable = min(remaining, slab)
        slab_tax = taxable * rate / 100
        if taxable > 0:
            lines.append(f"  ₹{taxable:>12,.0f} @ {rate}% = ₹{slab_tax:>10,.2f}")
        tax += slab_tax; remaining -= taxable
        if remaining <= 0: break
    cess = tax * 0.04
    return (f"🧾 Income Tax ({regime} regime) for ₹{income:,.0f}:\n" +
            "\n".join(lines) +
            f"\n  Base tax : ₹{tax:,.2f}\n"
            f"  Cess (4%): ₹{cess:,.2f}\n"
            f"  Total tax: ₹{tax+cess:,.2f}\n"
            f"  Effective rate: {(tax+cess)/income*100:.1f}%")

def gst_calculator(amount, rate, type_="inclusive"):
    amount = float(amount); rate = float(rate)
    if type_.lower() == "inclusive":
        base = amount * 100 / (100 + rate)
        gst  = amount - base
        return f"GST ({rate}% inclusive):\n  Base: ₹{base:.2f}  GST: ₹{gst:.2f}  Total: ₹{amount:.2f}"
    else:
        gst   = amount * rate / 100
        total = amount + gst
        return f"GST ({rate}% exclusive):\n  Base: ₹{amount:.2f}  GST: ₹{gst:.2f}  Total: ₹{total:.2f}"
