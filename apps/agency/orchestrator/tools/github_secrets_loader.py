"""
GitHub Secrets Loader for Claude Code Sessions
================================================

Attempts to fetch GitHub Secrets via GitHub API and inject them into environment.

This bridges the gap between GitHub Secrets (CI/CD) and Claude Code sessions (development).
"""

import os
import subprocess

import requests


def get_github_token() -> str | None:
    """Get GitHub token from available sources"""

    # Try environment variable
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        return token

    # Try gh CLI
    try:
        result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return None


def fetch_repository_secrets(owner: str, repo: str, token: str) -> dict[str, str]:
    """
    Fetch repository secrets via GitHub API.

    Note: The API returns secret NAMES only, not values (for security).
    Values are only available in GitHub Actions runners.

    Returns dict of secret names (values will be None).
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()

        data = resp.json()
        secrets = {}

        for secret in data.get("secrets", []):
            # API only returns names, not values
            secrets[secret["name"]] = None

        return secrets

    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch secrets: {e}")


def load_secrets_from_github(owner: str = "kimeisele", repo: str = "vibe-agency") -> bool:
    """
    Attempt to load GitHub Secrets into environment.

    Returns True if successful, False otherwise.

    NOTE: GitHub API does NOT expose secret VALUES (security feature).
    This can only verify secrets EXIST, not load their values.
    """
    token = get_github_token()
    if not token:
        print("⚠️  No GitHub token available (try: gh auth login)")
        return False

    try:
        secrets = fetch_repository_secrets(owner, repo, token)
        print(f"✅ Found {len(secrets)} secrets in GitHub:")
        for name in secrets:
            print(f"   - {name}")

        print()
        print("⚠️  LIMITATION: GitHub API does NOT expose secret values")
        print("   Secret values are ONLY available in GitHub Actions runners")
        print("   This function can verify secrets exist, but cannot load them")
        print()

        return False  # Cannot actually load values

    except Exception as e:
        print(f"❌ Failed to fetch secrets: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("GitHub Secrets Loader")
    print("=" * 70)
    print()

    load_secrets_from_github()

    print("CONCLUSION:")
    print("  GitHub Secrets API is read-only for security.")
    print("  Values are only decrypted in GitHub Actions runners.")
    print()
    print("SOLUTION:")
    print("  1. Use .claude/settings.local.json for local development")
    print("  2. Use GitHub Actions workflows for CI/CD (secrets work there)")
    print("  3. Use Claude Code WebSearch as fallback (no secrets needed)")
