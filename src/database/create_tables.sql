CREATE SCHEMA students;
CREATE SCHEMA groups;
CREATE SCHEMA payments;
CREATE SCHEMA universities;
CREATE SCHEMA attendances;

create table if not exists universities.universities (
    id bigserial primary key,
    name varchar(255) NOT NULL UNIQUE,
    alias varchar(255) NOT NULL UNIQUE
);

create table if not exists students.students (
    telegram_id bigint primary key,
    name varchar(255) NOT NULL,
    surname varchar(255) NOT NULL,
    birthday smallint,
    birthmonth smallint
);

create table if not exists groups.groups (
    id bigserial primary key,
    headman_id bigint NOT NULL,
    university_id bigint NOT NULL,
    name varchar(255) NOT NULL
);

create table if not exists groups.students_groups (
    student_id bigint NOT NULL,
    group_id bigint NOT NULL
);

create table if not exists attendances.lessons (
    id bigserial primary key,
    group_id bigint NOT NULL,
    name varchar(255) NOT NULL,
    start_time time with time zone NOT NULL
);


create table if not exists attendances.attendances (
    student_id bigint NOT NULL,
    lesson_id bigint NOT NULL,
    visit_status varchar(255) NOT NULL
);
