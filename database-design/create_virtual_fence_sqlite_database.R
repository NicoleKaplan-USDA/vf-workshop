# install the package if not already installed install.packages('RSQLite')

# attach the R package to interface with the SQLite database
library("RSQLite")
library("DBI")

# Connect to SQLite Database ----------------------------------------------

# Create sqlite database in your working directory if it doesn't already exist
database_connection <- DBI::dbConnect(RSQLite::SQLite(),
                                      file.path("database-design", "vf_development_database.db"))

# Create the `active_dates` Table -----------------------------------------

DBI::dbExecute(database_connection,
               "CREATE TABLE active_dates (
      id INTEGER PRIMARY KEY,
      virtual_fence TEXT,
      virtual_herd TEXT,
      vf_date_on TEXT,
      vf_date_off TEXT
      );")

# Create the `animal_parameters` Table ------------------------------------

DBI::dbExecute(database_connection,
               "CREATE TABLE animal_parameters (
      parameter_id INTEGER PRIMARY KEY,
      ear_tag TEXT,
      rfid TEXT,
      other_id REAL,
      date TEXT,
      sex TEXT,
      breed TEXT,
      body_wt_lbs REAL,
      body_condition_score REAL,
      pregnancy_status BOOLEAN,
      lactating BOOLEAN
      );")

# Create the `animals` Table ----------------------------------------------

DBI::dbExecute(database_connection,
               "CREATE TABLE animals (
      animal_id INTEGER PRIMARY KEY,
      ear_tag TEXT,
      rfid TEXT,
      other_id TEXT,
      collar_id TEXT,
      date_collared REAL
      );")

# Create the `collars` Table ----------------------------------------------

DBI::dbExecute(database_connection,
               "CREATE TABLE collars (
      collar_id INTEGER PRIMARY KEY,
      device_eui TEXT,
      last4 TEXT,
      firmware_version TEXT
      );")

# Create the `collar_history` Table ---------------------------------------

DBI::dbExecute(database_connection,
               "CREATE TABLE collar_history (
      collar_id INTEGER PRIMARY KEY,
      animal_id TEXT,
      date_on REAL,
      date_off REAL
      );")

# Create the `landmarks` Table --------------------------------------------

DBI::dbExecute(database_connection,
               "CREATE TABLE landmarks(
      id INTEGER PRIMARY KEY,
      name TEXT,
      landmark_geojson TEXT
      );")

# Create the `messages` Table ---------------------------------------------

DBI::dbExecute(database_connection,
               "CREATE TABLE messages (
      row_id INTEGER PRIMARY KEY,
      uuid TEXT,
      date TEXT,
      collar TEXT,
      messagetype TEXT,
      latitude REAL,
      longitude REAL,
      trackingState TEXT,
      cowHeading TEXT,
      tiltAngle TEXT,
      headingReportingEnabled TEXT,
      headingManagementEnabled TEXT,
      soundDisabled TEXT,
      shockDisabled TEXT,
      soundSuspended TEXT,
      shockSuspended TEXT,
      soundEvent TEXT,
      shockEvent TEXT,
      shockCount INTEGER,
      soundCount INTEGER,
      shockCountAttempts INTEGER,
      soundCountAttempts INTEGER,
      shockCountApplied INTEGER,
      soundCountApplied INTEGER,
      shockCountSuspend INTEGER,
      soundCountSuspend INTEGER,
      shockCountCumulative INTEGER,
      currVoltageMv REAL,
      lastTxVoltageMv REAL,
      lastShockVoltageMv REAL,
      mmuTempDegC REAL,
      mcuTempDegC REAL,
      reliable BOOLEAN,
      more BOOLEAN,
      sequence BOOLEAN,
      accuracy INTEGER,
      collar_id TEXT,
      Duration REAL,
      Time_Zone TEXT,
      latitude_utm REAL,
      Count INTEGER,
      Sum INTEGER,
      Flag INTEGER,
      Count_Flag INTEGER,
      Flag_Collar_Off INTEGER,
      Distance REAL,
      Rate REAL
      );")

# Create the `physical_herds` Table ---------------------------------------

DBI::dbExecute(database_connection,
               "CREATE TABLE physical_herds (
      row_id INTEGER PRIMARY KEY,
      physical_herd TEXT,
      virtual_herd_name TEXT,
      add_date TEXT,
      remove_date TEXT
    );")

# Create the `ranches` Table

DBI::dbExecute(database_connection,
               "CREATE TABLE ranches (
      row_id INTEGER PRIMARY KEY,
      ranch TEXT,
      herd_name TEXT,
      herd_type TEXT
    );")

# Create the `ranch_herds` Table ------------------------------------------

DBI::dbExecute(database_connection,
               "CREATE TABLE ranch_herds (
      ranch_herd_id INTEGER PRIMARY KEY,
      ranch_name TEXT,
      herd_name TEXT,
      herd_type TEXT
    );")

# Create the `virtual-fences` Table ---------------------------------------

DBI::dbExecute(database_connection,
               "CREATE TABLE virtual_fences (
      vf_id INTEGER PRIMARY KEY,
      vf_name TEXT,
      geometry TEXT,
      width_shock_m REAL
      width_sound_m REAL,
      vf_date_on TEXT,
      vf_date_off TEXT,
      vf_geojson TEXT
    );")

# Create the `virtual-herds` Table ----------------------------------------

DBI::dbExecute(database_connection,
               "CREATE TABLE virtual_herds (
      virtual_herd_id INTEGER PRIMARY KEY,
      virtual_herd_name TEXT,
      collar_id TEXT,
      date_added TEXT,
      date_removed TEXT
);")
