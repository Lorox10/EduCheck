import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from db import db_healthcheck, init_db


load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    init_db()

    @app.get("/health")
    def health() -> tuple[dict, int]:
        db_status = db_healthcheck()
        status_code = 200 if db_status == "ok" else 503
        return {"status": "ok", "db": db_status}, status_code

    return app


if __name__ == "__main__":
    app = create_app()
    env = os.getenv("APP_ENV", "development").lower()
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=env == "development")
