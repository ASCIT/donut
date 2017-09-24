--------------------------
-- course_scheduler.sql --
--------------------------
--
-- Database schema definition for Donut undergraduate course scheduler,
-- adapted from work by Kevin Chen (kchen2@) and Bryant Lin (bjlin@) as
-- part of the Bagel team of summer 2012.
--
-- Revisions:
--   v1.0   2013-09-21   mqian@caltech.edu (Mike Qian)
--   v1.1   2014-09-21   rbachal@caltech.edu (Rahul Bachal)

DROP TABLE IF EXISTS scheduler.course_sections;
DROP TABLE IF EXISTS scheduler.courses;
DROP TABLE IF EXISTS scheduler.schedules;

DROP SCHEMA IF EXISTS scheduler;
CREATE SCHEMA scheduler;
-- Schema permissions
GRANT ALL ON SCHEMA scheduler TO pgsql;
GRANT USAGE ON SCHEMA scheduler TO view, ascit, devel;

/*
 * Information about courses
 */
CREATE TABLE scheduler.courses (
    course_id   SERIAL         PRIMARY KEY,
    department  VARCHAR(30)     NOT NULL,
    course_no   VARCHAR(10)     NOT NULL,
    name        VARCHAR(150)    NOT NULL,
    description TEXT,
    units       VARCHAR(10)     NOT NULL,
    UNIQUE (department, course_no)
);

GRANT ALL ON scheduler.courses TO pgsql;
GRANT SELECT ON scheduler.courses TO view;
GRANT INSERT,UPDATE,DELETE,SELECT ON scheduler.courses TO ascit,devel;

GRANT ALL ON scheduler.courses_course_id_seq to pgsql;
GRANT SELECT, UPDATE ON scheduler.courses_course_id_seq TO view, ascit, devel;

/*
 * Information about course sections
 */
CREATE TABLE scheduler.course_sections (
    section_id  SERIAL          PRIMARY KEY,
    course_id   INTEGER         NOT NULL REFERENCES scheduler.courses(course_id),
    section_no  VARCHAR(3)      NOT NULL,
    instructor  VARCHAR(60),
    times       VARCHAR(100),
    locations   VARCHAR(100),
    grades      VARCHAR(25),
    UNIQUE (course_id, section_no)
);

GRANT ALL ON scheduler.course_sections TO pgsql;
GRANT SELECT ON scheduler.course_sections TO view;
GRANT INSERT,UPDATE,DELETE,SELECT ON scheduler.course_sections TO ascit,devel;

GRANT ALL ON scheduler.course_sections_section_id_seq to pgsql;
GRANT SELECT, UPDATE ON scheduler.course_sections_section_id_seq TO view,ascit,devel;

/*
 * Schedules saved by logged-in students
 */
CREATE TABLE scheduler.schedules (
    inum        INTEGER   PRIMARY KEY REFERENCES public.inums(inum),
    courses     TEXT            NOT NULL
);

GRANT ALL ON scheduler.schedules TO pgsql;
GRANT SELECT ON scheduler.schedules TO view;
GRANT INSERT,UPDATE,DELETE,SELECT ON scheduler.schedules TO ascit,devel;

--
-- end of course_scheduler.sql
--
