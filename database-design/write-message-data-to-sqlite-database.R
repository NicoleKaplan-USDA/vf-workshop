# install the SQLite R package if not already installed
# install.packages("RSQLite")

# attach the R package to interface with the SQLite database
library("RSQLite")
library("DBI")
library("dplyr")

# Connect to SQLite Database ----------------------------------------------

# Create sqlite database in your working directory if it doesn't already exist
database_connection <- DBI::dbConnect(RSQLite::SQLite(),
                                        file.path("database-design", "vf_development_database.db"))

# Read Empty Tables in SQLite Database ------------------------------------

# You can see which tables are in the database by running the following
DBI::dbListTables(database_connection)

# Read in Message Data ----------------------------------------------------

# load message data (downloaded from the API)
message_data <- readr::read_csv(file.path("database-design", "example-data.csv"))

# Rename 'index' column to 'row_id' ---------------------------------------

# data from the API uses the 'index' column to number the rows
# 'index' is a reserved keyword in SQLite and we need to change it

message_data <- dplyr::rename(message_data, row_id = index)

# Write Message Data to Database ------------------------------------------

DBI::dbWriteTable(database_connection, "messages", message_data, append = TRUE)

# Close the Database Connection -------------------------------------------

DBI::dbDisconnect(database_connection)
