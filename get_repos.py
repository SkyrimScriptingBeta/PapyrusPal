import pprint
import requests
import json
import time
import random
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Any
import os
from urllib.parse import urlencode

# Load environment variables from .env file
load_dotenv(find_dotenv())

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if GITHUB_TOKEN is None:
    raise ValueError(
        "GITHUB_TOKEN environment variable not set. Please set it in your .env file."
    )

BASE_URL: str = "https://api.github.com/search/repositories"
QUERY: str = "language:papyrus+skyrim+in:name,description"
PER_PAGE: int = 100
MAX_RETRIES: int = 5
HEADERS: Dict[str, str] = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
}


def fetch_with_backoff(base_url: str, page: int) -> Dict[str, Any]:
    attempt: int = 0

    # Build raw query manually
    q: str = "language:papyrus+skyrim+in:name,description"
    other_params: Dict[str, Any] = {
        "per_page": PER_PAGE,
        "page": page,
        "sort": "stars",
        "order": "desc",
    }
    query_string: str = f"q={q}&{urlencode(other_params)}"
    full_url: str = f"{base_url}?{query_string}"

    print(f">>> Fetching: {full_url}")

    while attempt < MAX_RETRIES:
        response = requests.get(full_url, headers=HEADERS)
        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            json_data = response.json()
            pprint.pprint(json_data)
            return json_data

        try:
            print("Response JSON:", response.json())
        except Exception:
            print("Failed to decode JSON response")

        if response.status_code == 403:
            print("Rate limit or abuse detection triggered. Backing off...")
        else:
            print(f"Unexpected status code: {response.status_code}. Retrying...")

        sleep_time: float = (2**attempt) + random.uniform(0, 1)
        time.sleep(sleep_time)
        attempt += 1

    raise Exception(f"Failed after {MAX_RETRIES} retries")


def fetch_all_repos() -> List[Dict[str, Any]]:
    all_repos: List[Dict[str, str | None | Dict[str, str]]] = []
    page: int = 1

    while True:
        print(f"Fetching page {page}...")
        data: Dict[str, Any] = fetch_with_backoff(BASE_URL, page)
        items = data.get("items", [])
        if not items:
            break

        for repo in items:
            all_repos.append(
                {
                    "html_url": repo["html_url"],
                    "description": repo.get("description", ""),
                    "license": repo.get("license") or None,
                }
            )

        if len(items) < PER_PAGE:
            break

        page += 1

    return all_repos


def save_to_json(data: List[Dict[str, str]], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    repos = fetch_all_repos()
    save_to_json(repos, "skyrim_papyrus_repos.json")
    print(f"Saved {len(repos)} repos to skyrim_papyrus_repos.json")
