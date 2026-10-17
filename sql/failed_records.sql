-- Number of order records that failed one or more DQ checks.
-- Each record is counted once, even if it failed several checks.
SELECT
    'records_failing_dq_checks' AS question,
    'Records that failed one or more checks' AS label,
    COUNT(*) AS value
FROM failed_orders;