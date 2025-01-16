from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "../../db.sqlite3",
    }
}

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.mysql",
#         "NAME": "sawdaa$default",
#         "USER": "sawdaa",
#         "PASSWORD": "<pass>sawda</pass>",
#         "HOST": "sawdaa.mysql.pythonanywhere-services.com",
#         "PORT": "3306",
#         "OPTIONS": {
#             "charset": "utf8mb4",  # Use utf8mb4 for full emoji support
#             "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",  # Important for data consistency
#         },
#     }
# }
