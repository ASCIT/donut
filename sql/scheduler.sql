DROP TABLE IF EXISTS scheduler_courses;
DROP TABLE IF EXISTS scheduler_course_sections;

CREATE TABLE scheduler_courses (
    course_id           INT             NOT NULL AUTO_INCREMENT,
    department          VARCHAR(30)     NOT NULL,
    course_no           VARCHAR(10)     NOT NULL,
    name                VARCHAR(150)    NOT NULL,
    description         TEXT            NOT NULL,
    units               VARCHAR(10)     NOT NULL,
    PRIMARY KEY (course_id),
    UNIQUE KEY (department, course_no)
);

CREATE TABLE scheduler_course_sections (
    section_id          INT             NOT NULL AUTO_INCREMENT,
    course_id           INT             NOT NULL,
    section_no          VARCHAR(3)      NOT NULL,
    instructor          VARCHAR(60),
    times               VARCHAR(100),
    locations           VARCHAR(100),
    grades              vARCHAR(25),
    PRIMARY KEY (section_id),
    UNIQUE KEY (course_id, section_no),
    FOREIGN KEY (course_id) REFERENCES scheduler_courses(course_id)
);
