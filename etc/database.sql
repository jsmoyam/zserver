CREATE TABLE IF NOT EXISTS host(
  id INTEGER NOT NULL PRIMARY KEY,
  hostname TEXT DEFAULT "",
  ip TEXT NOT NULL,
  operating_system TEXT DEFAULT "",
  date_creation INTEGER DEFAULT 0,
  date_modified INTEGER DEFAULT 0,
  agent_available INTEGER DEFAULT 0,
  forest_available INTEGER DEFAULT 0,
  channel_name TEXT DEFAULT "unknown",
  country TEXT DEFAULT "",
  managed_by TEXT DEFAULT "",
  active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS channel(
  name TEXT NOT NULL PRIMARY KEY,
  hunting_type TEXT NOT NULL DEFAULT "yara",
  concurrence_type TEXT NOT NULL DEFAULT "by_times",
  concurrence_time TEXT NOT NULL DEFAULT "1",
  scheduling INTEGER DEFAULT 0,
  priority TEXT NOT NULL DEFAULT "medium",
  force_execution INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS historical_host(
  host_name TEXT NOT NULL,
  channel_name TEXT NOT NULL,
  date_modified INTEGER DEFAULT 0,
  status TEXT NOT NULL -- CHANGE_CHANNEL, REMOVED_HOST, REMOVED_CHANNEL
);

CREATE TABLE IF NOT EXISTS historical_xlsx(
  id INTEGER NOT NULL PRIMARY KEY,
  full_path TEXT NOT NULL,
  date INTEGER DEFAULT 0,
  total_channels INTEGER DEFAULT 0,
  total_hosts INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS session(
  id INTEGER NOT NULL PRIMARY KEY,
  channel_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT "working",
  date_start INTEGER DEFAULT 0,
  date_finish INTEGER DEFAULT 0,
  forest_path TEXT,
  total_evos INTEGER DEFAULT 0,
  current_evos INTEGER DEFAULT 0,
  current_hits INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS session_host(
  id_session INTEGER NOT NULL,
  id_host INTEGER NOT NULL,
  date_start INTEGER DEFAULT 0,
  date_finish INTEGER DEFAULT 0,
  total_evos INTEGER DEFAULT -1,
  current_evos INTEGER DEFAULT 0,
  status TEXT DEFAULT "",
  exit_code TEXT DEFAULT ""
);

CREATE TABLE IF NOT EXISTS session_evo(
  id INTEGER NOT NULL PRIMARY KEY,
  id_session INTEGER DEFAULT -1,
  session_hostname TEXT DEFAULT "",
  id_job TEXT DEFAULT "",
  evo TEXT NOT NULL,
  date_start INTEGER DEFAULT 0,
  date_finish INTEGER DEFAULT 0,
  processing_host TEXT NOT NULL,
  status TEXT DEFAULT "",
  exit_code TEXT DEFAULT ""
);

CREATE TABLE IF NOT EXISTS session_hit(
--   id_session_evo INTEGER DEFAULT -1,
  session_host TEXT DEFAULT "",
  session_evo TEXT DEFAULT "",
  path TEXT NOT NULL,
  date INTEGER DEFAULT 0,
  description TEXT
);

CREATE TABLE IF NOT EXISTS country(
  name TEXT PRIMARY KEY,
  description TEXT,
  forest_host TEXT,
  forest_user TEXT
);

CREATE TABLE IF NOT EXISTS manual_hunting(
  id INTEGER NOT NULL PRIMARY KEY,
  id_host INTEGER,
  hostname TEXT NOT NULL,
  ip TEXT NOT NULL,
  channel_name TEXT NOT NULL,
  country TEXT NOT NULL,
  code TEXT,
  id_session INTEGER
);

CREATE TABLE IF NOT EXISTS processed_host(
	id	INTEGER PRIMARY KEY,
	id_host	INTEGER NOT NULL,
	hunting_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS processed_evo(
	id	INTEGER PRIMARY KEY,
	hostname	TEXT NOT NULL,
	evoname TEXT NOT NULL,
	hunting_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hist_session_host(
  id_session INTEGER NOT NULL,
  id_host INTEGER NOT NULL,
  date_start INTEGER DEFAULT 0,
  date_finish INTEGER DEFAULT 0,
  status TEXT DEFAULT "",
  exit_code TEXT DEFAULT ""
);

CREATE TABLE IF NOT EXISTS hist_session_evo(
  id_session INTEGER DEFAULT -1,
  session_hostname TEXT DEFAULT "",
  id_job TEXT DEFAULT "",
  evo TEXT NOT NULL,
  date_start INTEGER DEFAULT 0,
  date_finish INTEGER DEFAULT 0,
  processing_host TEXT NOT NULL,
  status TEXT DEFAULT "",
  exit_code TEXT DEFAULT ""
);