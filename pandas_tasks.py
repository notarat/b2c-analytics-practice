"""
Практика pandas на данных «как в банке» (B2C). 5 задач, ~1 час.
Сначала создай базу: python generate_db.py. Решай по очереди, после каждой сверяйся с ответом в комментарии.
Застрял больше 10 минут — подсмотри в pandas_solutions.py.

Таблицы в b2c.db:
  clients       client_id, gender, age, city, segment, has_sberprime, reg_date
  transactions  txn_id, client_id, txn_date, category, amount, channel
  offers        show_id, client_id, shown_date, offer, clicked, converted
"""
import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DB = HERE / "b2c.db"
con = sqlite3.connect(DB)

# P1. Загрузи три таблицы в DataFrame-ы tx, cl, of через pd.read_sql.
#     Даты сразу сделай датами: parse_dates=["txn_date"] и т.п.
#     Проверка: tx.shape == (31693, 6), cl.shape == (2000, 7), of.shape == (8069, 6)


# P2. По каждой категории посчитай сумму трат, число операций и средний чек.
#     Отсортируй по сумме по убыванию.
#     Подсказка: groupby("category")["amount"].agg(total="sum", n="count", avg="mean")
#     Проверка: первая строка — Маркетплейсы, 21 365 836 ₽, 4940 операций


# P3. Средний чек в разрезе «сегмент × пол».
#     Сначала merge транзакций с клиентами по client_id, потом pivot_table.
#     Проверка: Премиум/Ж ≈ 6871, Премиум/М ≈ 6238, Массовый/Ж ≈ 1992


# P4. Нарисуй график трат по месяцам (млн ₽) и сохрани в png.
#     Подсказка: tx["txn_date"].dt.to_period("M"), потом .plot(marker="o")
#     Проверка: пик — август 2026 (12,8 млн), провал — февраль (8,1 млн)


# P5. Автоматизация отчёта. Напиши функцию make_report(month), month = "2026-08",
#     которая возвращает словарь: траты за месяц, число активных клиентов,
#     средний чек, топ-3 категории, CTR предложений (% кликов от показов).
#     Прогони её по всем месяцам 2026-01…2026-10, собери DataFrame и сохрани в Excel.
#     Проверка для 2026-08: 12 784 092 ₽, 1601 клиент, чек 3802.53,
#     топ-3: Путешествия, Маркетплейсы, Супермаркеты; CTR 11.6 %
