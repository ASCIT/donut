DROP TABLE IF EXISTS planner_courses;
DROP TABLE IF EXISTS planner_placeholders;
DROP TABLE IF EXISTS scheduler_sections;
DROP TABLE IF EXISTS sections;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS instructors;
DROP TABLE IF EXISTS grades_types;

CREATE TABLE courses (
    course_id       INT           NOT NULL AUTO_INCREMENT,
    year            YEAR          NOT NULL, -- e.g. 2018
    term            TINYINT       NOT NULL, -- FA: 1, WI: 2, SP: 3, SU: 4
    department      VARCHAR(30)   NOT NULL, -- e.g. CS
    course_number   VARCHAR(10)   NOT NULL, -- e.g. 124
    name            VARCHAR(150)  NOT NULL, -- e.g. Operating Systems
    description     TEXT, -- Currently unused
    units_lecture   FLOAT         NOT NULL, -- e.g. 3
    units_lab       FLOAT         NOT NULL, -- e.g. 6
    units_homework  FLOAT         NOT NULL, -- e.g. 3
    units           FLOAT         AS (units_lecture + units_lab + units_homework),
    PRIMARY KEY (course_id),
    UNIQUE (year, term, department, course_number)
);

CREATE TABLE instructors (
    instructor_id  INT          NOT NULL AUTO_INCREMENT,
    instructor     VARCHAR(60)  NOT NULL, -- e.g. Pinkston, D
    PRIMARY KEY (instructor_id),
    UNIQUE (instructor)
);

CREATE TABLE grades_types (
    grades_type_id  INT          NOT NULL AUTO_INCREMENT,
    grades_type     VARCHAR(30)  NOT NULL, -- e.g. PASS-FAIL
    PRIMARY KEY (grades_type_id),
    UNIQUE (grades_type)
);

CREATE TABLE sections (
    course_id       INT           NOT NULL,
    section_number  TINYINT       NOT NULL, -- e.g. 1
    instructor_id   INT           NOT NULL,
    grades_type_id  INT           NOT NULL,
    times           VARCHAR(100)  NOT NULL, -- e.g. MWF 13:00 - 13:55
    locations       VARCHAR(100)  NOT NULL, -- e.g. 213 ANB
    PRIMARY KEY (course_id, section_number),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id),
    FOREIGN KEY (grades_type_id) REFERENCES grades_types(grades_type_id)
);

CREATE TABLE planner_courses (
    user_id       INT      NOT NULL,
    course_id     INT      NOT NULL,
    planner_year  TINYINT  NOT NULL, -- Frosh: 1, ..., Senior: 4
    PRIMARY KEY (user_id, course_id, planner_year),
    FOREIGN KEY (user_id) REFERENCES members(user_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON DELETE CASCADE
);

CREATE TABLE planner_placeholders (
    placeholder_id  INT      NOT NULL AUTO_INCREMENT,
    user_id         INT      NOT NULL,
    planner_year    TINYINT  NOT NULL, -- Frosh: 1, ..., Senior: 4
    term            TINYINT  NOT NULL, -- FA: 1, WI: 2, SP: 3
    course_name     TEXT     NOT NULL,
    course_units    FLOAT    NOT NULL,
    PRIMARY KEY (placeholder_id),
    FOREIGN KEY (user_id) REFERENCES members(user_id)
);

CREATE TABLE scheduler_sections (
    user_id         INT      NOT NULL,
    course_id       INT      NOT NULL,
    section_number  TINYINT  NOT NULL,
    notes           TEXT,
    PRIMARY KEY (user_id, course_id, section_number),
    FOREIGN KEY (user_id) REFERENCES members(user_id),
    FOREIGN KEY (course_id, section_number)
        REFERENCES sections(course_id, section_number)
        ON DELETE CASCADE
);
