import os
import time
import requests
import pandas as pd

API = "https://api.github.com/search/repositories"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "student-project-scraper"
}

token = os.getenv("GITHUB_TOKEN")
if token:
    HEADERS["Authorization"] = f"Bearer {token}"

def request_json(url, params, max_tries=6):
    """Запрос с ретраями и backoff на случай 403 rate limit/временных сбоев."""
    for attempt in range(1, max_tries + 1):
        r = requests.get(url, headers=HEADERS, params=params, timeout=(10, 30))

        # Если упёрлись в лимит — подождём до reset
        if r.status_code == 403 and "X-RateLimit-Remaining" in r.headers:
            remaining = int(r.headers.get("X-RateLimit-Remaining", "0"))
            if remaining == 0:
                reset = int(r.headers.get("X-RateLimit-Reset", "0"))
                sleep_for = max(5, reset - int(time.time()) + 5)
                print(f"Rate limit. Sleep {sleep_for}s...")
                time.sleep(sleep_for)
                continue

        # Иногда GitHub может вернуть 502/503
        if r.status_code in (500, 502, 503, 504):
            time.sleep(1.5 * attempt)
            continue

        r.raise_for_status()
        return r.json()

    raise RuntimeError("Не удалось получить ответ от GitHub API после нескольких попыток.")

def fetch_1000_repos(query: str) -> list[dict]:
    """
    GitHub Search API возвращает максимум 1000 результатов (10 страниц по 100).
    """
    repos = []
    for page in range(1, 11):  # 10 * 100 = 1000
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
            "page": page,
        }
        data = request_json(API, params)
        items = data.get("items", [])
        if not items:
            break

        for it in items:
            license_info = it.get("license") or {}
            owner_info = it.get("owner") or {}

            repos.append({
                # текстовые
                "full_name": it.get("full_name", ""),
                "description": (it.get("description") or ""),

                # категориальные
                "language": it.get("language") or "Unknown",
                "license": license_info.get("spdx_id") or "None",
                "owner_type": owner_info.get("type") or "Unknown",

                # числовые (>=5)
                "stars": int(it.get("stargazers_count") or 0),
                "forks": int(it.get("forks_count") or 0),
                "open_issues": int(it.get("open_issues_count") or 0),
                "watchers": int(it.get("watchers_count") or 0),
                "size_kb": int(it.get("size") or 0),

                # доп. полезные
                "has_issues": int(bool(it.get("has_issues"))),
                "is_fork": int(bool(it.get("fork"))),
                "archived": int(bool(it.get("archived"))),
                "repo_url": it.get("html_url", ""),
            })

        print(f"page {page}: collected {len(repos)}")
        time.sleep(0.2)

    return repos

def main():
    # Запрос специально сделан так, чтобы результатов было >>1000
    # Тогда GitHub отдаст топ-1000 по звёздам.
    query = "stars:>50"

    repos = fetch_1000_repos(query)
    df = pd.DataFrame(repos)

    # На всякий случай уберём дубли
    df = df.drop_duplicates(subset=["full_name"]).reset_index(drop=True)

    df.to_csv("github_repos_1000.csv", index=False, encoding="utf-8-sig")
    print("Saved:", df.shape, "-> github_repos_1000.csv")
    print(df.head())

if __name__ == "__main__":
    main()


