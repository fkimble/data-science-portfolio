-- Senior analyst reconciliation checks for the Access-to-Oracle migration.

-- 1. Source-to-target row reconciliation.
SELECT COUNT(*) AS migrated_audio_files
FROM AudioFiles;

-- 2. Primary-key uniqueness guardrail.
SELECT record_id, COUNT(*) AS duplicate_count
FROM AudioFiles
GROUP BY record_id
HAVING COUNT(*) > 1;

-- 3. Department-level storage and cost exposure.
SELECT
  d.dept_name,
  COUNT(*) AS records,
  ROUND(SUM(a.file_size_mb) / 1024, 2) AS storage_gb,
  ROUND(SUM(a.storage_cost_usd_month), 4) AS monthly_cost
FROM AudioFiles a
JOIN Departments d ON a.dept_id = d.dept_id
GROUP BY d.dept_name
ORDER BY monthly_cost DESC;

-- 4. Cost optimization queue: large standard-tier files.
SELECT
  a.record_id,
  a.file_name,
  d.dept_name,
  a.file_size_mb,
  a.storage_cost_usd_month
FROM AudioFiles a
JOIN Departments d ON a.dept_id = d.dept_id
JOIN StorageTiers s ON a.tier_id = s.tier_id
WHERE s.tier_name = 'Standard'
  AND a.file_size_mb >= 100
ORDER BY a.storage_cost_usd_month DESC;
