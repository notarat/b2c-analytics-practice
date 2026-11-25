"""
Практика pandas на данных «как в банке» (B2C).
Сначала создай базу: python generate_db.py, потом: python pandas_solutions.py
Сначала попробуй решить сам в pandas_tasks.py, потом сверяйся здесь.
"""
import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DB = HERE / "b2c.db"
con = sqlite3.connect(DB)

# ---------- P1. Загрузить таблицы из SQLite в DataFrame ----------
tx = pd.read_sql("SELECT * FROM transactions", con, parse_dates=["txn_date"])
cl = pd.read_sql("SELECT * FROM clients", con, parse_dates=["reg_date"])
of = pd.read_sql("SELECT * FROM offers", con, parse_dates=["shown_date"])
print("P1:", tx.shape, cl.shape, of.shape)          # (31693, 6) (2000, 7) (8069, 6)
print(tx.head(), "\n")

# ---------- P2. Сумма, число операций и средний чек по категориям ----------
p2 = (tx.groupby("category")["amount"]
        .agg(total="sum", n="count", avg="mean")
        .sort_values("total", ascending=False)
        .round(0))
print("P2:\n", p2, "\n")

# ---------- P3. Средний чек: сегмент × пол (merge + pivot_table) ----------
m = tx.merge(cl[["client_id", "segment", "gender"]], on="client_id", how="left")
p3 = m.pivot_table(index="segment", columns="gender", values="amount",
                   aggfunc="mean").round(0)
print("P3:\n", p3, "\n")

# ---------- P4. График трат по месяцам ----------
monthly = tx.groupby(tx["txn_date"].dt.to_period("M"))["amount"].sum() / 1e6
ax = monthly.plot(marker="o", figsize=(8, 4), title="Траты клиентов по месяцам, млн ₽")
ax.set_xlabel(""); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(HERE / "monthly_spend.png", dpi=120)
print("P4: график сохранён в monthly_spend.png\n")

# ---------- P5. Автоматизация отчёта: одна функция — один месяц ----------
def make_report(month: str) -> dict:
    """month в формате 'YYYY-MM', например '2026-08'."""
    t = tx[tx["txn_date"].dt.strftime("%Y-%m") == month]
    o = of[of["shown_date"].dt.strftime("%Y-%m") == month]
    return {
        "Месяц": month,
        "Траты, ₽": round(t["amount"].sum()),
        "Активных клиентов": t["client_id"].nunique(),
        "Средний чек, ₽": round(t["amount"].mean(), 2),
        "Топ-3 категории": t.groupby("category")["amount"].sum().nlargest(3).index.tolist(),
        "CTR предложений, %": round(o["clicked"].mean() * 100, 1),
    }

report = pd.DataFrame([make_report(f"2026-{mm:02d}") for mm in range(1, 11)])
print("P5:\n", report.to_string(index=False))
report.to_excel(HERE / "monthly_report.xlsx", index=False)   # готовый файл для руководителя
print("\nОтчёт сохранён в monthly_report.xlsx")
