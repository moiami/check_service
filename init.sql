CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE DATABASE check_db;
\connect check_db;

CREATE TABLE IF NOT EXISTS comment_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id UUID NOT NULL,
    user_id UUID NOT NULL,
    date TIMESTAMPTZ NOT NULL DEFAULT now(),
    report_text TEXT NOT NULL,
    conclusion TEXT NULL
);

CREATE INDEX IF NOT EXISTS ix_comment_reports_comment_id ON comment_reports (comment_id);
CREATE INDEX IF NOT EXISTS ix_comment_reports_user_id ON comment_reports (user_id);

CREATE TABLE IF NOT EXISTS film_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    film_id UUID NOT NULL,
    new_category TEXT NOT NULL,
    review TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_film_reviews_film_id ON film_reviews (film_id);

CREATE TABLE IF NOT EXISTS news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    date TIMESTAMPTZ NOT NULL DEFAULT now(),
    report_text TEXT NOT NULL,
    conclusion TEXT NULL
);

CREATE INDEX IF NOT EXISTS ix_reports_user_id ON reports (user_id);

CREATE TABLE IF NOT EXISTS news_film_reviews (
    news_id UUID NOT NULL REFERENCES news(id) ON DELETE CASCADE,
    film_review_id UUID NOT NULL,
    PRIMARY KEY (news_id, film_review_id)
);

CREATE TABLE IF NOT EXISTS report_comments (
    report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    comment_id UUID NOT NULL,
    PRIMARY KEY (report_id, comment_id)
);

CREATE TABLE IF NOT EXISTS report_related_reports (
    report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    related_report_id UUID NOT NULL,
    PRIMARY KEY (report_id, related_report_id)
);
