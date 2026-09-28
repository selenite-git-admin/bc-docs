BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;
-- W9 path A vs B feasibility (umbrella, 2026-09-28): read-only on Odoo v3_lc5, company 1 (Kaveri). SELECT only.
-- At each date P: the lc5 numerator (receivable-line balance) vs invoice-grain readings of ar_balance.
\echo '== F1 per as-of date P (company currency)'
WITH d(p) AS (VALUES (date '2024-03-31'), (date '2025-03-31'), (date '2025-09-30'), (date '2026-03-31'), (date '2026-08-31')),
rl AS (  -- receivable-control lines, posted, company 1
  SELECT l.id, l.move_id, l.date, l.balance, m.move_type, l.full_reconcile_id
    FROM account_move_line l JOIN account_account a ON a.id = l.account_id JOIN account_move m ON m.id = l.move_id
   WHERE l.company_id = 1 AND l.parent_state = 'posted' AND a.account_type = 'asset_receivable'),
inv AS (SELECT * FROM rl WHERE move_type IN ('out_invoice','out_refund')),
fr AS (  -- a fully reconciled line's clearing date = the latest partial touching its full reconcile
  SELECT l.full_reconcile_id, max(p.max_date) AS cleared_at
    FROM account_partial_reconcile p JOIN account_move_line l ON l.id IN (p.debit_move_id, p.credit_move_id)
   WHERE l.full_reconcile_id IS NOT NULL GROUP BY 1),
applied AS (  -- signed reconciled amount on each receivable line, by partial date
  SELECT x.line_id, x.max_date, sum(x.amt) AS amt FROM (
    SELECT p.debit_move_id AS line_id, p.max_date, p.amount AS amt FROM account_partial_reconcile p
    UNION ALL SELECT p.credit_move_id, p.max_date, -p.amount FROM account_partial_reconcile p) x GROUP BY 1,2)
SELECT d.p AS as_of,
  (SELECT sum(balance) FROM rl WHERE date <= d.p) AS b_line_balance_lc5,
  (SELECT sum(i.balance) FROM inv i LEFT JOIN fr ON fr.full_reconcile_id = i.full_reconcile_id
    WHERE i.date <= d.p AND (fr.cleared_at IS NULL OR fr.cleared_at > d.p)) AS a_face_open_signed,
  (SELECT sum(m.amount_total) FROM inv i JOIN account_move m ON m.id = i.move_id LEFT JOIN fr ON fr.full_reconcile_id = i.full_reconcile_id
    WHERE i.date <= d.p AND (fr.cleared_at IS NULL OR fr.cleared_at > d.p)) AS a_as_declared_unsigned,
  (SELECT sum(i.balance - coalesce((SELECT sum(ap.amt) FROM applied ap WHERE ap.line_id = i.id AND ap.max_date <= d.p), 0))
     FROM inv i WHERE i.date <= d.p) AS a_residual_invoice_lines,
  (SELECT sum(r.balance - coalesce((SELECT sum(ap.amt) FROM applied ap WHERE ap.line_id = r.id AND ap.max_date <= d.p), 0))
     FROM rl r WHERE r.date <= d.p AND r.move_type NOT IN ('out_invoice','out_refund')) AS non_invoice_residual,
  (SELECT count(*) FROM rl r WHERE r.date <= d.p AND r.move_type NOT IN ('out_invoice','out_refund')) AS non_invoice_lines
FROM d ORDER BY 1;
\echo '== F2 billing in FY2026-27 P03..P05 (2026-06-01..2026-08-31): as declared (unsigned amount_total, refunds added) vs net of credit notes (signed)'
SELECT sum(amount_total) FILTER (WHERE move_type IN ('out_invoice','out_refund')) AS gross_invoiced_as_declared_unsigned,
       sum(amount_total_signed) FILTER (WHERE move_type IN ('out_invoice','out_refund')) AS net_of_credit_notes_signed,
       count(*) FILTER (WHERE move_type = 'out_refund') AS refunds
  FROM account_move WHERE company_id = 1 AND state = 'posted' AND date BETWEEN date '2026-06-01' AND date '2026-08-31';
\echo '== F3 non-invoice receivable lines by journal and sign (what invoice grain cannot see), all posted'
SELECT j.code AS journal, m.move_type, count(*) AS lines, sum(l.balance) AS balance
  FROM account_move_line l JOIN account_account a ON a.id = l.account_id JOIN account_move m ON m.id = l.move_id JOIN account_journal j ON j.id = m.journal_id
 WHERE l.company_id = 1 AND l.parent_state = 'posted' AND a.account_type = 'asset_receivable' AND m.move_type NOT IN ('out_invoice','out_refund')
 GROUP BY 1,2 ORDER BY 1,2;
\echo '== F4 invoice header facts ar_balance as declared needs: invoice_date present, a header clearing date (none in Odoo), partial payments'
SELECT count(*) AS posted_docs, count(invoice_date) AS with_invoice_date,
       count(*) FILTER (WHERE payment_state = 'partial') AS partially_paid, count(*) FILTER (WHERE payment_state IN ('paid','in_payment')) AS paid
  FROM account_move WHERE company_id = 1 AND state = 'posted' AND move_type IN ('out_invoice','out_refund');
COMMIT;
