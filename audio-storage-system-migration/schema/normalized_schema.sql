-- Normalized schema (Oracle-style)
CREATE TABLE Departments (
  dept_id NUMBER PRIMARY KEY,
  dept_name VARCHAR2(100) UNIQUE NOT NULL
);

CREATE TABLE RecordingTypes (
  type_id NUMBER PRIMARY KEY,
  type_name VARCHAR2(150) UNIQUE NOT NULL
);

CREATE TABLE StorageTiers (
  tier_id NUMBER PRIMARY KEY,
  tier_name VARCHAR2(50) UNIQUE NOT NULL
);

CREATE TABLE AudioFiles (
  file_id NUMBER PRIMARY KEY,
  record_id NUMBER UNIQUE NOT NULL,
  file_name VARCHAR2(200) NOT NULL,
  dept_id NUMBER NOT NULL,
  type_id NUMBER NOT NULL,
  tier_id NUMBER NOT NULL,
  duration_sec NUMBER NOT NULL,
  sample_rate_hz NUMBER NOT NULL,
  channels NUMBER NOT NULL,
  file_size_mb NUMBER(10,2) NOT NULL,
  created_date DATE NOT NULL,
  created_by VARCHAR2(50) NOT NULL,
  storage_cost_usd_month NUMBER(10,4),
  CONSTRAINT fk_dept FOREIGN KEY (dept_id) REFERENCES Departments(dept_id),
  CONSTRAINT fk_type FOREIGN KEY (type_id) REFERENCES RecordingTypes(type_id),
  CONSTRAINT fk_tier FOREIGN KEY (tier_id) REFERENCES StorageTiers(tier_id)
);
