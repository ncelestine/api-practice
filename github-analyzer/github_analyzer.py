import os
import time

import requests

# GitHub User Repository Analyzer
# This script connects to the GitHub API, grabs a user's repos,
# and shows rankings and summary statistics.


GITHUB_API_URL = "https://api.github.com/users/{username}/repos"
HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}

# Optional: a personal access token raises the rate limit from 60 to 5,000 requests per hour.
# It is read from an environment variable so it is never stored in the code.
if os.environ.get("GITHUB_TOKEN"):
    HEADERS["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"


def fetch_repos(username):
    """
    This function calls the GitHub API with retry logic.
    It will retry up to 3 times if there is a temporary failure.
    """
    url = GITHUB_API_URL.format(username=username)

    for attempt in range(1, 4):   # try up to 3 times
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)

            # Success
            if response.status_code == 200:
                return response.json()

            # Rate limit or forbidden
            elif response.status_code == 403:
                print("GitHub API rate limit reached or access denied.")
                return None

            # Other client/server errors
            else:
                print(f"GitHub API returned status {response.status_code}")
                print(f"Attempt {attempt} failed.")

        except Exception as e:
            print(f"Error on attempt {attempt}: {e}")

        if attempt < 3:
            print("Retrying in 1 second...")
            time.sleep(1)

    print("Failed to retrieve data after 3 attempts.")
    return None



def analyze_repos(repos):
    """
    This function analyzes the list of repositories and calculates:
    - total number of repos
    - total stars
    - average stars
    - repositories grouped by language
    """
    total_repos = len(repos)
    total_stars = 0
    language_counts = {}

    for repo in repos:
        lang = repo["language"] if repo["language"] else "Unknown"

        if lang not in language_counts:
            language_counts[lang] = 0
        language_counts[lang] += 1

        total_stars += repo.get("stargazers_count", 0)

    avg_stars = total_stars / total_repos if total_repos > 0 else 0

    return {
        "total_repos": total_repos,
        "total_stars": total_stars,
        "avg_stars": avg_stars,
        "language_counts": language_counts
    }



def get_rankings(repos):
    """
    Finds:
    - Top 3 most-starred repositories
    - Top 5 most recently updated repositories
    """

    most_starred = sorted(
        repos,
        key=lambda r: r.get("stargazers_count", 0),
        reverse=True
    )[:3]

    most_recent = sorted(
        repos,
        key=lambda r: r.get("updated_at", ""),
        reverse=True
    )[:5]

    return most_starred, most_recent



def main():
    """
    Main function for running the analyzer.
    """
    print("\n===============================================")
    print("   GITHUB REPO ANALYZER")
    print("===============================================")

    username = input("Enter a GitHub username: ").strip()

    if not username:
        print("You must enter a username.")
        return

    repos = fetch_repos(username)

    if repos is None:
        print("Could not fetch repositories.")
        return

    if len(repos) == 0:
        print("This user has no public repositories.")
        return

    print(f"\nFound {len(repos)} public repositories:\n")
    for repo in repos:
        print("-", repo["name"])

    # Ranking (top starred + most recently updated)
    most_starred, most_recent = get_rankings(repos)

    print("\n" + "="*50)
    print("TOP 3 MOST-STARRED REPOSITORIES")
    print("="*50)
    for repo in most_starred:
        print(f"  • {repo['name']}  —  {repo.get('stargazers_count', 0)} stars")

    print("\n" + "="*50)
    print("TOP 5 MOST RECENTLY UPDATED REPOSITORIES")
    print("="*50)
    for repo in most_recent:
        print(f"  • {repo['name']}  —  updated at {repo['updated_at']}")

    # Summary statistics
    stats = analyze_repos(repos)

    print("\n" + "="*50)
    print("SUMMARY STATISTICS")
    print("="*50)
    print("Total Repositories:", stats["total_repos"])
    print("Total Stars:", stats["total_stars"])
    print("Average Stars per Repo:", round(stats["avg_stars"], 2))

    print("\nRepositories by Language:")
    for lang, count in stats["language_counts"].items():
        print(f"  • {lang}: {count}")


if __name__ == "__main__":
    main()
