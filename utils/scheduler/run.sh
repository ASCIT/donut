#!/bin/bash

# Generates the course schedule in courses.bin and courses-with-descriptions.bin
# Creates SQL script to insert into database
# Runs psql using command-line arguments to execute the SQL script
#
# @param
# $1 the name of the schedule file obtained from the registrar
# $2 the username for the database
# $3 the name of the database


rm *.bin
rm *.html
python textParser.py $1
python addDesc.py

export PGUSER=$2
export PGDATABASE=$3

psql -f insert_courses.sql
