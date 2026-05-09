"""
Smoke-test для Check Service.
Запуск: python test_api.py
Требует: pip install httpx
"""

import httpx
import json
import uuid

BASE = "http://localhost:8002"
OK = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"

def check(label: str, condition: bool, detail: str = ""):
    status = OK if condition else FAIL
    print(f"  {status} {label}" + (f"  →  {detail}" if detail else ""))
    return condition

def section(title: str):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)

errors = []

with httpx.Client(base_url=BASE, timeout=10) as c:

    # ── Health ────────────────────────────────────────
    section("Health")
    r = c.get("/api/v1/health")
    check("GET /health/ → 200", r.status_code == 200, r.text)

    # ── Reports ───────────────────────────────────────
    section("Reports")

    user_id = str(uuid.uuid4())
    comment_id_1 = str(uuid.uuid4())
    comment_id_2 = str(uuid.uuid4())
    old_report_id = str(uuid.uuid4())

    # Create (вызов сервисного слоя напрямую через отдельный запрос — симулируем через прямой вызов)
    # Так как Create не пробрасывается в API, создаём через internal endpoint если есть,
    # иначе просто проверяем GET на пустой список
    r = c.get("/api/v1/reports/")
    check("GET /reports/ → 200", r.status_code == 200, str(r.json()))

    # Попытка GET несуществующего → 404
    fake_id = str(uuid.uuid4())
    r = c.get(f"/api/v1/reports/{fake_id}")
    check("GET /reports/{fake_id} → 404", r.status_code == 404, str(r.status_code))

    # PATCH несуществующего → 500 (нет записи, ожидаемо)
    r = c.patch("/api/v1/reports/", json={"id": fake_id, "conclusion": "blocking"})
    check("PATCH /reports/ несуществующий → не 200", r.status_code != 200, str(r.status_code))

    # DELETE несуществующего → 200 (DELETE идемпотентен, просто ничего не делает)
    r = c.request("DELETE", "/api/v1/reports/", content=json.dumps({"id": fake_id}), headers={"Content-Type": "application/json"})
    check("DELETE /reports/ несуществующий → 200", r.status_code == 200, str(r.status_code))

    # ── Comment Reports ───────────────────────────────
    section("Comment Reports")

    r = c.get("/api/v1/comment-reports/")
    check("GET /comment-reports/ → 200", r.status_code == 200, str(r.json()))

    r = c.get(f"/api/v1/comment-reports/{fake_id}")
    check("GET /comment-reports/{fake_id} → 404", r.status_code == 404, str(r.status_code))

    r = c.patch("/api/v1/comment-reports/", json={"id": fake_id, "conclusion": "everything_is_fine"})
    check("PATCH /comment-reports/ несуществующий → не 200", r.status_code != 200, str(r.status_code))

    r = c.request("DELETE", "/api/v1/comment-reports/", content=json.dumps({"id": fake_id}), headers={"Content-Type": "application/json"})
    check("DELETE /comment-reports/ несуществующий → 200", r.status_code == 200, str(r.status_code))

    # ── News ──────────────────────────────────────────
    section("News")

    r = c.get("/api/v1/news/")
    check("GET /news/ → 200", r.status_code == 200, str(r.json()))

    r = c.get(f"/api/v1/news/{fake_id}")
    check("GET /news/{fake_id} → 404", r.status_code == 404, str(r.status_code))

    # PATCH с film_review_ids на несуществующую news → не 200
    r = c.patch("/api/v1/news/", json={"id": fake_id, "film_review_ids": []})
    check("PATCH /news/ несуществующий → не 200", r.status_code != 200, str(r.status_code))

    r = c.request("DELETE", "/api/v1/news/", content=json.dumps({"id": fake_id}), headers={"Content-Type": "application/json"})
    check("DELETE /news/ несуществующий → 200", r.status_code == 200, str(r.status_code))

    # ── Film Reviews ──────────────────────────────────
    section("Film Reviews")

    r = c.get("/api/v1/film-reviews/")
    check("GET /film-reviews/ → 200", r.status_code == 200, str(r.json()))

    r = c.get(f"/api/v1/film-reviews/{fake_id}")
    check("GET /film-reviews/{fake_id} → 404", r.status_code == 404, str(r.status_code))

    r = c.patch("/api/v1/film-reviews/", json={
        "id": fake_id,
        "new_category": "drama",
        "review": "great film"
    })
    check("PATCH /film-reviews/ несуществующий → не 200", r.status_code != 200, str(r.status_code))

    r = c.request("DELETE", "/api/v1/film-reviews/", content=json.dumps({"id": fake_id}), headers={"Content-Type": "application/json"})
    check("DELETE /film-reviews/ несуществующий → 200", r.status_code == 200, str(r.status_code))

    # ── Проверка Create через сервисный слой ──────────
    section("Сервисный слой (Create) — симуляция вызова Арсения")
    print("  Создание записей через прямой вызов Python (не API):")

    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))

    try:
        import asyncio
        from src.services.report_service import create_report
        from src.services.comment_report_service import create_comment_report
        from src.services.news_service import create_news
        from src.services.film_review_service import create_film_review
        from src.domain.models.report import ReportCreateDto
        from src.domain.models.comment_report import CommentReportCreateDto
        from src.domain.models.news import NewsCreateDto
        from src.domain.models.film_review import FilmReviewCreateDto

        async def run_creates():
            film_id = uuid.uuid4()
            comment_id = uuid.uuid4()
            user_id = uuid.uuid4()

            # create film_review
            fr_result = await create_film_review(FilmReviewCreateDto(
                film_id=film_id,
                comment_id=comment_id,
                new_category="thriller",
                review="Отличный триллер с неожиданной концовкой."
            ))
            print(f"  {OK} create_film_review → {fr_result}")

            # get its id for news
            all_fr = await asyncio.get_event_loop().run_in_executor(None, lambda: c.get("/api/v1/film-reviews/").json())
            fr_id = uuid.UUID(all_fr[0]["id"]) if all_fr else uuid.uuid4()

            # create news
            news_result = await create_news(NewsCreateDto(film_review_ids=[fr_id]))
            print(f"  {OK} create_news → {news_result}")

            # create comment_report
            cr_result = await create_comment_report(CommentReportCreateDto(
                comment_id=comment_id,
                user_id=user_id,
                report_text="LLM сгенерировал: комментарий содержит оскорбления и нарушает правила сообщества."
            ))
            print(f"  {OK} create_comment_report → {cr_result}")

            # create report
            r_result = await create_report(ReportCreateDto(
                user_id=user_id,
                report_text="Сводный отчёт по пользователю: несколько нарушений за последние 30 дней.",
                comment_ids=[comment_id],
                related_report_ids=[]
            ))
            print(f"  {OK} create_report → {r_result}")

        asyncio.run(run_creates())

        # Теперь проверяем что всё появилось в базе через API
        section("Проверка что записи появились в базе")
        r = c.get("/api/v1/film-reviews/")
        data = r.json()
        check("film_reviews не пустой", len(data) > 0, f"{len(data)} записей")

        r = c.get("/api/v1/news/")
        data = r.json()
        check("news не пустой", len(data) > 0, f"{len(data)} записей")

        r = c.get("/api/v1/comment-reports/")
        data = r.json()
        check("comment_reports не пустой", len(data) > 0, f"{len(data)} записей")

        r = c.get("/api/v1/reports/")
        data = r.json()
        check("reports не пустой", len(data) > 0, f"{len(data)} записей")

        # PATCH существующих записей
        section("PATCH существующих записей")

        fr_id = c.get("/api/v1/film-reviews/").json()[0]["id"]
        r = c.patch("/api/v1/film-reviews/", json={"id": fr_id, "new_category": "drama", "review": "Обновлённое ревью."})
        check("PATCH /film-reviews/ существующий → 200", r.status_code == 200, str(r.json()))

        cr_id = c.get("/api/v1/comment-reports/").json()[0]["id"]
        r = c.patch("/api/v1/comment-reports/", json={"id": cr_id, "conclusion": "blocking"})
        check("PATCH /comment-reports/ → conclusion=blocking", r.status_code == 200, str(r.json()))

        rep_id = c.get("/api/v1/reports/").json()[0]["id"]
        r = c.patch("/api/v1/reports/", json={"id": rep_id, "conclusion": "everything_is_fine"})
        check("PATCH /reports/ → conclusion=everything_is_fine", r.status_code == 200, str(r.json()))

        news_id = c.get("/api/v1/news/").json()[0]["id"]
        r = c.patch("/api/v1/news/", json={"id": news_id, "film_review_ids": []})
        check("PATCH /news/ → очистить film_review_ids", r.status_code == 200, str(r.json()))

        # DELETE существующих записей
        section("DELETE существующих записей")

        r = c.request("DELETE", "/api/v1/film-reviews/", content=json.dumps({"id": fr_id}), headers={"Content-Type": "application/json"})
        check("DELETE /film-reviews/ → 200", r.status_code == 200)
        r = c.get(f"/api/v1/film-reviews/{fr_id}")
        check("GET удалённого film_review → 404", r.status_code == 404)

        r = c.request("DELETE", "/api/v1/comment-reports/", content=json.dumps({"id": cr_id}), headers={"Content-Type": "application/json"})
        check("DELETE /comment-reports/ → 200", r.status_code == 200)
        r = c.get(f"/api/v1/comment-reports/{cr_id}")
        check("GET удалённого comment_report → 404", r.status_code == 404)

        r = c.request("DELETE", "/api/v1/reports/", content=json.dumps({"id": rep_id}), headers={"Content-Type": "application/json"})
        check("DELETE /reports/ → 200", r.status_code == 200)
        r = c.get(f"/api/v1/reports/{rep_id}")
        check("GET удалённого report → 404", r.status_code == 404)

        r = c.request("DELETE", "/api/v1/news/", content=json.dumps({"id": news_id}), headers={"Content-Type": "application/json"})
        check("DELETE /news/ → 200", r.status_code == 200)
        r = c.get(f"/api/v1/news/{news_id}")
        check("GET удалённой news → 404", r.status_code == 404)

    except ImportError as e:
        print(f"  ⚠ Сервисный слой недоступен локально (нормально если запускаешь вне проекта): {e}")
        print("  → Запусти скрипт из корня проекта: python test_api.py")

print(f"\n{'='*50}")
print("  Готово!")
print('='*50)