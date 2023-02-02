-- !preview conn=database_connection

CREATE TABLE active_dates (
      id INTEGER PRIMARY KEY, --might consider calling this 'animal_id' or 'cow_id'
      virtual_fence TEXT,
      virtual_herd TEXT,
      vf_date_on TEXT, --called 'turn-on' in the template database, but I renamed it here for consistency across tables.
      vf_date_off TEXT
    );
CREATE TABLE animal_parameters (
      parameter_id INTEGER PRIMARY KEY,
      ear_tag TEXT, --TODO what would we use as the foreign key in this table? ear_tags are not always unique. Perhaps 'animal_id'?
      rfid TEXT,
      other_id REAL,
      date TEXT,
      sex TEXT, --need to add to template database
      breed TEXT,
      body_wt_lbs REAL, --called 'body_wt' in the template database but having units might be useful
      body_condition_score REAL, --called 'BSC' in the template database
      pregnancy_status BOOLEAN, --called 'preg_status' in the template database
      lactating BOOLEAN --optional, might be useful
    );
CREATE TABLE animals (
      animal_id INTEGER PRIMARY KEY, --called 'row_id' in the template database
      ear_tag TEXT,
      rfid TEXT,
      other_id TEXT,
      collar_id TEXT, --can change multiple times per year, need to model this with a relationship/join
      date_collared REAL --maybe consider moving this because as cows are frequently re-collared, it may lose its meaning
    );
    CREATE TABLE collars (
      collar_id INTEGER PRIMARY KEY, --this could be an integer as a stand in for DeviceEUI
      device_eui TEXT, --hexadecimal, 16 digits
      last4 TEXT, --useful if you use it join against for quick metadata collection while collaring
      firmware_version TEXT --might be useful to understand changes in data over time
    );
    CREATE TABLE collar_history (
      collar_id INTEGER PRIMARY KEY,
      animal_id TEXT,
      date_on REAL, --date the collar was put on the animal
      date_off REAL --date the collar was taken off the animal (or approximate date it fell off the animal)
    );
    CREATE TABLE landmarks(
      id INTEGER PRIMARY KEY,
      name TEXT,
      landmark_geojson TEXT --store the text file in the database or a path to the file?
      --TODO what else should I include in this table?
    );
    CREATE TABLE messages (
      message_id INTEGER PRIMARY KEY,
      uuid TEXT,
      date TEXT, --consider naming this 'message_date' to differentiate it from the other dates
      collar TEXT, --I could rename this column to be device_eui for consistency across tables
      messagetype TEXT, --this column is not camelCase in the API
      latitude REAL,
      longitude REAL,
      trackingState TEXT,
      cowHeading TEXT, --no longer being passed through the API, consider removing this column from the API
      tiltAngle TEXT, --no longer being passed through the API, consider removing this column from the API
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
      currVoltageMv REAL, --called 'currVoltageMV' in the template database notice the capital V at the end. How I have it spelled is correct to the spelling in the API
      lastTxVoltageMv REAL,
      lastShockVoltageMv REAL,
      mmuTempDegC REAL,
      mcuTempDegC REAL,
      reliable BOOLEAN, --TEXT storage type in the template database. I think it will always be TRUE/FALSE
      more BOOLEAN, --TEXT storage type in the template database. I think it will always be TRUE/FALSE
      sequence BOOLEAN, --TEXT storage type in the template database. I think it will always be TRUE/FALSE
      accuracy INTEGER,
      collar_id TEXT, --not a column name in the API. Would this be a foreign key for the collars table?
      Duration REAL, --not a column name in the API. Not sure what this column represents.
      Time_Zone TEXT, --not a column name in the API. Maybe not a good idea to store it alongside the message data, as it would be replicated millions of times, but store it elsewhere maybe in the `ranches` table
      latitude_utm REAL, --not a column name in the API, but would be useful for calculating metrics as UTM is a planar system compared to Lat/Long which is an angular system. We would need to convert the lat/long column in downstream processing step not in the API code.
      Count INTEGER, --not a column name in the API
      Sum INTEGER, --not a column name in the API
      Flag INTEGER, --not a column name in the API
      Count_Flag INTEGER, --not a column name in the API
      Flag_Collar_Off INTEGER, --not a column name in the API
      Distance REAL, --not a column name in the API
      Rate REAL --not a column name in the API
    );
    CREATE TABLE physical_herds (
      row_id INTEGER PRIMARY KEY, --consider naming this 'herd_id' to differentiate it from the other primary keys
      physical_herd TEXT, --does this represent the name of the physical herd?
      virtual_herd_name TEXT, --each individual can be in multiple virtual herds across time, so maybe we remove this column and store it in virtual herds
      add_date TEXT, --REAL storage type in the template database
      remove_date TEXT --REAL storage type in the template database
    );
    CREATE TABLE ranches ( --called `ranch` in the template database but I think plural is more consistent with the other tables
      row_id INTEGER PRIMARY KEY, --consider naming this 'ranch_id' or something similar
      ranch TEXT, --consider naming this 'ranch_name'
      herd_name TEXT,
      herd_type TEXT --does this represent cow/calf, stocker steer, or breeding bull?
    );
    CREATE TABLE ranch_herds (
      ranch_herd_id INTEGER PRIMARY KEY, --called 'row_id' in the template database
      ranch_name TEXT, --called 'ranch' in the template database
      herd_name TEXT,
      herd_type TEXT --does this represent cow/calf, stocker steer, or breeding bull?
    );
    CREATE TABLE virtual_fences (
      vf_id INTEGER PRIMARY KEY,
      vf_name TEXT,
      geometry TEXT, --maybe store this as a GeoJSON inside the database?
      width_shock_m REAL, --width of shock zone in meters
      width_sound_m REAL, --width of the shock zone in meters
      vf_date_on TEXT, --date virtual fence was enabled
      vf_date_off TEXT, --date virtual fence was disabled
      vf_geojson TEXT --geometry of virtual fence
    );
    CREATE TABLE virtual_herds (
      virtual_herd_id INTEGER PRIMARY KEY,
      virtual_herd_name TEXT,
      collar_id TEXT,
      date_added TEXT,
      date_removed TEXT
);