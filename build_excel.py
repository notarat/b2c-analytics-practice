"""
Сборка тренировочного Excel-файла practice.xlsx из базы b2c.db.

Что делает:
  1. читает три таблицы из b2c.db в pandas;
  2. заранее считает правильные ответы к заданиям (для самопроверки);
  3. записывает лист «Задания» и три листа с данными через pd.ExcelWriter;
  4. через openpyxl красит заголовки, закрепляет первую строку, ставит фильтры,
     ширину столбцов и формат дат/чисел.

Запуск: python build_excel.py  (сначала python generate_db.py)
Нужны библиотеки: pip install pandas openpyxl
"""
import sqlite3
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
HERE = Path(__file__).resolve().parent
con = sqlite3.connect(HERE / "b2c.db")
tx = pd.read_sql("SELECT * FROM transactions", con, parse_dates=["txn_date"])
cl = pd.read_sql("SELECT * FROM clients", con, parse_dates=["reg_date"])
of = pd.read_sql("SELECT * FROM offers", con, parse_dates=["shown_date"])
# expected answers
m = tx.merge(cl[["client_id", "segment"]], on="client_id")
e3 = m.groupby("segment")["amount"].mean().round(2).sort_values(ascending=False)
e4 = tx[(tx.category == "Рестораны") & (tx.txn_date.dt.month == 7)]["amount"].sum().round(2)
e6 = int((tx.amount > 50000).sum())
aug = tx[tx.txn_date.dt.month == 8].groupby("channel")["amount"].sum().round(0)
ans = {"e3": e3.to_dict(), "e4": float(e4), "e6": e6, "aug": aug.to_dict()}

print(ans)
tasks = [
 ("1", "Сводная таблица: сумма трат по категориям", "Лист «Транзакции» → Вставка → Сводная таблица. Строки: category, Значения: Сумма по amount. Отсортируй по убыванию.", "Маркетплейсы — 21 365 836 ₽"),
 ("2", "Сводная по месяцам и каналам", "Строки: txn_date (правой кнопкой → Группировать → Месяцы), Столбцы: channel, Значения: Сумма по amount.", "Пик — август: 12 784 092 ₽ всего"),
 ("3", "ВПР / ПРОСМОТРX: подтянуть сегмент клиента", "В лист «Транзакции» добавь столбец G «segment»: =ПРОСМОТРX(B2;Клиенты!A:A;Клиенты!E:E) или =ВПР(B2;Клиенты!A:E;5;0). Потом сводная: Строки — segment, Значения — Среднее по amount.", "; ".join(f"{k}: {v:,.2f} ₽".replace(",", " ").replace(".", ",") for k, v in e3.items())),
 ("4", "СУММЕСЛИМН: траты на рестораны в июле", "Формула: =СУММЕСЛИМН(E:E;D:D;\"Рестораны\";C:C;\">=01.07.2026\";C:C;\"<=31.07.2026\"). E — amount, D — category, C — txn_date. Проверь себя сводной с фильтром.", f"{e4:,.2f} ₽".replace(",", " ").replace(".", ",")),
 ("5", "CTR предложений", "Лист «Предложения» → сводная: Строки — offer, Значения — Количество по show_id и Сумма по clicked. Рядом формула CTR = клики / показы, формат «процент».", "Лидер: Кешбэк на маркетплейсах — 16,3%; хуже всех Кредитная карта — 5,2%"),
 ("6", "СЧЁТЕСЛИ + условное форматирование", "Посчитай операции дороже 50 000 ₽: =СЧЁТЕСЛИ(E:E;\">50000\"). Выдели их цветом: Главная → Условное форматирование → Правила выделения ячеек → Больше.", f"{e6} операций"),
 ("7", "График", "По сводной из задания 2: Вставка → Сводная диаграмма → График. Найди, когда траты максимальны, и предположи почему.", "Рост летом (июль–август): сезон путешествий"),
]
with pd.ExcelWriter(HERE / "practice.xlsx", engine="openpyxl") as xw:
    pd.DataFrame(tasks, columns=["№", "Задание", "Как сделать", "Ответ для самопроверки"]).to_excel(xw, sheet_name="Задания", index=False)
    tx.to_excel(xw, sheet_name="Транзакции", index=False)
    cl.to_excel(xw, sheet_name="Клиенты", index=False)
    of.to_excel(xw, sheet_name="Предложения", index=False)
wb = load_workbook(HERE / "practice.xlsx")
head = PatternFill("solid", fgColor="0B7A57")
for ws in wb.worksheets:
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = head; c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"
    if ws.title != "Задания":
        ws.auto_filter.ref = ws.dimensions
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = max(12, min(28, len(str(col[0].value)) + 6))
        for row in ws.iter_rows(min_row=2):
            for c in row:
                if hasattr(c.value, "year"): c.number_format = "DD.MM.YYYY"
                elif isinstance(c.value, float): c.number_format = "#,##0.00"
ws = wb["Задания"]
for col, w in zip("ABCD", [5, 34, 70, 44]): ws.column_dimensions[col].width = w
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
wb.save(HERE / "practice.xlsx")
print("saved")
