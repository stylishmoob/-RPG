import os


def _with_connect_timeout(database_url):
    if "connect_timeout=" in database_url:
        return database_url

    separator = "&" if "?" in database_url else "?"
    return f"{database_url}{separator}connect_timeout=1"


os.environ["DATABASE_URL"] = _with_connect_timeout(
    os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/rpg",
    )
)
