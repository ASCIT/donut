DROP TABLE IF EXISTS survey_question_choices;
DROP TABLE IF EXISTS survey_questions;
DROP TABLE IF EXISTS survey_question_types;
DROP TABLE IF EXISTS surveys;

CREATE TABLE surveys (
    survey_id      INT           NOT NULL AUTO_INCREMENT,
    title          VARCHAR(100)  NOT NULL,
    description    TEXT,
    start_time     DATETIME      NOT NULL,
    end_time       DATETIME      NOT NULL,
    access_key     CHAR(64)      NOT NULL, -- hex string
    group_id       INT,                    -- restrict to this group if non-NULL
    auth           BOOLEAN       NOT NULL, -- require authentication (UID and birthday)
    public         BOOLEAN       NOT NULL, -- whether survey should appear in the list of active surveys
    results_shown  BOOLEAN       DEFAULT FALSE, -- whether survey should appear in the list of results
    creator        INT           NOT NULL, -- user id of survey creator

    PRIMARY KEY(survey_id),
    FOREIGN KEY(group_id) REFERENCES groups(group_id) ON DELETE SET NULL,
    FOREIGN KEY(creator) REFERENCES members(user_id) ON DELETE CASCADE
);

CREATE TABLE survey_question_types (
    type_id    INT          NOT NULL AUTO_INCREMENT,
    type_name  VARCHAR(20)  NOT NULL,
    choices    BOOLEAN      NOT NULL, -- whether there is a list of choices associated with this type of question

    PRIMARY KEY(type_id)
);

CREATE TABLE survey_questions (
    question_id  INT           NOT NULL AUTO_INCREMENT,
    survey_id    INT           NOT NULL,
    title        VARCHAR(100)  NOT NULL,
    description  TEXT,
    list_order   INT           NOT NULL, -- position in survey, zero-indexed
    type_id      INT           NOT NULL,

    PRIMARY KEY(question_id),
    FOREIGN KEY(survey_id) REFERENCES surveys(survey_id) ON DELETE CASCADE,
    FOREIGN KEY(type_id) REFERENCES survey_question_types(type_id)
);

CREATE TABLE survey_question_choices (
    choice_id    INT          NOT NULL AUTO_INCREMENT,
    question_id  INT          NOT NULL,
    choice       VARCHAR(50)  NOT NULL,

    PRIMARY KEY(choice_id),
    FOREIGN KEY(question_id) REFERENCES survey_questions(question_id) ON DELETE CASCADE
);

INSERT INTO survey_question_types (type_name, options) VALUES
    ('Dropdown', TRUE),
    ('Checkboxes', TRUE),
    ('Elected position', TRUE),
    ('Short text', FALSE),
    ('Long text', FALSE);