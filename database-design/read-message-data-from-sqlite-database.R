# remove all objects from the R environment
rm(list = ls())

# connect to the SQLite database
database_connection <- DBI::dbConnect(RSQLite::SQLite(), 
                                      "vf_development_database.db")

# read in data from the messages table
message_data <- DBI::dbReadTable(database_connection, "messages")

# print the first 5 rows of data from the 'messages' table
head(message_data)

# or View the data in a new tab
View(message_data)
