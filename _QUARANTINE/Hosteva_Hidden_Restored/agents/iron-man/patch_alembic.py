import re

with open("alembic/env.py", "r") as f:
    content = f.read()

new_content = """import os
from app.core.config import settings

# Override sqlalchemy.url with dynamic config
config.set_main_option("sqlalchemy.url", settings.sqlalchemy_database_url)

"""

if "from app.core.config import settings" not in content:
    content = content.replace("config = context.config", "config = context.config\n" + new_content)
    with open("alembic/env.py", "w") as f:
        f.write(content)
