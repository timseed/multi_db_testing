# Multi Db Tests

I would like to ensure my ORM/Schema will work with different engines.

By changing the class initializer and inheriting from the base (SQLITE :MEMORY:), we can demonstrate the ability to test 3 databases, using 2 Database schema languages (Sqlite, mysql).

Please note - none of the SQL is RDBMS specific, so you would expect it to work on both. 

This greatly simplifies and de-risks the RDBMS testing for moving a project forward. 


## Problem areas

As each database test assumes an empty database. 
