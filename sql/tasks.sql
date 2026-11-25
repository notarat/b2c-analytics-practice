-- Практика SQL на учебной базе b2c.db (SQLite).
-- Открой b2c.db в DBeaver / DataGrip / DB Browser и выполняй запросы по одному.
-- Сначала попробуй написать запрос сам, потом сверься с решением ниже.

-- 1. Сколько клиентов в каждом сегменте? Отсортируй по убыванию.
--    Тема: GROUP BY, COUNT
--    Ответ (строк: 3): Массовый | 1379 / Массовый высокодоходный | 452 / Премиум | 169
SELECT segment, COUNT(*) AS clients
FROM clients
GROUP BY segment
ORDER BY clients DESC;

-- 2. Топ-5 категорий по общей сумме трат.
--    Тема: SUM, ORDER BY, LIMIT
--    Ответ (строк: 5): Маркетплейсы | 21365836 / Супермаркеты | 20528246 / Путешествия | 16758474 …
SELECT category, ROUND(SUM(amount)) AS total
FROM transactions
GROUP BY category
ORDER BY total DESC
LIMIT 5;

-- 3. Число операций и средний чек по каждому каналу оплаты.
--    Тема: AVG, ROUND
--    Ответ (строк: 3): Карта | 22199 | 3128.9 / СБП | 6320 | 3151.63 / Онлайн | 3174 | 3173.99
SELECT channel, COUNT(*) AS operations, ROUND(AVG(amount), 2) AS avg_check
FROM transactions
GROUP BY channel
ORDER BY operations DESC;

-- 4. Сумма трат по месяцам 2026 года.
--    Тема: даты: strftime
--    Ответ (строк: 10): 2026-01 | 8735235 / 2026-02 | 8126529 / 2026-03 | 9802676 …
SELECT strftime('%Y-%m', txn_date) AS month, ROUND(SUM(amount)) AS total
FROM transactions
GROUP BY month
ORDER BY month;

-- 5. Сколько клиентов потратили за период больше 300 000 ₽?
--    Тема: HAVING
--    Ответ (строк: 1): 11
SELECT COUNT(*) AS big_spenders
FROM (
  SELECT client_id
  FROM transactions
  GROUP BY client_id
  HAVING SUM(amount) > 300000
);

-- 6. Траты на одного активного клиента по сегментам.
--    Тема: JOIN, COUNT(DISTINCT)
--    Ответ (строк: 3): Премиум | 164 | 177150 / Массовый высокодоходный | 438 | 77753 / Массовый | 1353 | 26861
SELECT c.segment,
       COUNT(DISTINCT t.client_id) AS active_clients,
       ROUND(SUM(t.amount) / COUNT(DISTINCT t.client_id)) AS spend_per_client
FROM transactions t
JOIN clients c ON c.client_id = t.client_id
GROUP BY c.segment
ORDER BY spend_per_client DESC;

-- 7. Сколько клиентов не сделали ни одной операции?
--    Тема: LEFT JOIN … IS NULL
--    Ответ (строк: 1): 45
SELECT COUNT(*) AS inactive
FROM clients c
LEFT JOIN transactions t ON t.client_id = c.client_id
WHERE t.client_id IS NULL;

-- 8. CTR каждого предложения: доля кликов от показов, в процентах.
--    Тема: SUM / COUNT, 100.0
--    Ответ (строк: 6): Кешбэк на маркетплейсах | 1341 | 219 | 16.3 / Кешбэк на такси | 1342 | 204 | 15.2 / Кешбэк в ресторанах | 1288 | 187 | 14.5 …
SELECT offer,
       COUNT(*) AS shows,
       SUM(clicked) AS clicks,
       ROUND(100.0 * SUM(clicked) / COUNT(*), 1) AS ctr_pct
FROM offers
GROUP BY offer
ORDER BY ctr_pct DESC;

-- 9. Отличается ли CTR у клиентов со СберПраймом и без него?
--    Тема: JOIN двух таблиц, AVG по 0/1
--    Ответ (строк: 2): 0 | 5786 | 10.8 / 1 | 2283 | 13.8
SELECT c.has_sberprime,
       COUNT(*) AS shows,
       ROUND(100.0 * AVG(o.clicked), 1) AS ctr_pct
FROM offers o
JOIN clients c ON c.client_id = o.client_id
GROUP BY c.has_sberprime;

-- 10. Две самые крупные по сумме трат категории в каждом сегменте.
--    Тема: оконная функция RANK
--    Ответ (строк: 6): Массовый | Маркетплейсы | 7722482 | 1 / Массовый | Супермаркеты | 7513397 | 2 / Массовый высокодоходный | Маркетплейсы | 7291009 | 1 …
WITH s AS (
  SELECT c.segment, t.category, SUM(t.amount) AS total
  FROM transactions t
  JOIN clients c ON c.client_id = t.client_id
  GROUP BY c.segment, t.category
)
SELECT segment, category, ROUND(total) AS total, rnk
FROM (
  SELECT *, RANK() OVER (PARTITION BY segment ORDER BY total DESC) AS rnk
  FROM s
)
WHERE rnk <= 2
ORDER BY segment, rnk;

-- 11. Траты по месяцам с накопленным итогом с начала года.
--    Тема: SUM() OVER
--    Ответ (строк: 10): 2026-01 | 8735235 | 8735235 / 2026-02 | 8126529 | 16861765 / 2026-03 | 9802676 | 26664441 …
WITH m AS (SELECT strftime('%Y-%m', txn_date) AS month, SUM(amount) AS total FROM transactions GROUP BY month)
SELECT month, ROUND(total) AS total,
       ROUND(SUM(total) OVER (ORDER BY month)) AS cumulative
FROM m;

-- 12. Изменение трат месяц к месяцу в процентах.
--    Тема: LAG
--    Ответ (строк: 10): 2026-01 | 8735235 | — / 2026-02 | 8126529 | -7 / 2026-03 | 9802676 | 20.6 …
WITH m AS (SELECT strftime('%Y-%m', txn_date) AS month, SUM(amount) AS total FROM transactions GROUP BY month)
SELECT month, ROUND(total) AS total,
       ROUND(100.0 * (total - LAG(total) OVER (ORDER BY month))
             / LAG(total) OVER (ORDER BY month), 1) AS mom_pct
FROM m;

