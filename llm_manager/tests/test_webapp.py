"""Web route tests for /tuning and the consolidated directory admin portal."""

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TEST_DB = REPO / "test_local_config.db"


def _patch_modules(engine, SessionLocal):
    from llm_manager import (
        database as db_mod,
        config_store as cs_mod,
        tuning_store as ts_mod,
    )

    db_mod.engine = engine
    db_mod.SessionLocal = SessionLocal
    cs_mod.SessionLocal = SessionLocal
    ts_mod.engine = engine
    ts_mod.SessionLocal = SessionLocal
    return db_mod, cs_mod, ts_mod


@pytest.fixture()
def app():
    if TEST_DB.exists():
        TEST_DB.unlink()

    from llm_manager import database as db_mod
    from llm_manager.webapp import create_app
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine2 = create_engine(
        f"sqlite:///{TEST_DB}", connect_args={"check_same_thread": False}
    )
    SessionLocal2 = sessionmaker(bind=engine2, autoflush=False, expire_on_commit=False)

    original_engine = db_mod.engine
    original_session = db_mod.SessionLocal
    _patch_modules(engine2, SessionLocal2)

    try:
        from llm_manager.database import init_db

        init_db()
        app = create_app()
        app.config["TESTING"] = True
        yield app
    finally:
        from llm_manager import (
            database as db_mod_r,
            config_store as cs_mod_r,
            tuning_store as ts_mod_r,
        )

        db_mod_r.engine = original_engine
        db_mod_r.SessionLocal = original_session
        cs_mod_r.SessionLocal = original_session
        ts_mod_r.engine = original_engine
        ts_mod_r.SessionLocal = original_session
        if TEST_DB.exists():
            TEST_DB.unlink()


def _t(string):
    return string


def test_tuning_page_renders(app):
    client = app.test_client()
    resp = client.get("/tuning")
    assert resp.status_code == 200
    assert "Model tuning profiles" in resp.get_data(as_text=True)


def test_tuning_save_and_list(app):
    client = app.test_client()
    payload = {
        "model_key": "codellama-7b-instruct",
        "model_name": "CodeLlama-7B-Instruct",
        "quantization": "Q5_K_M",
        "n_gpu_layers": "all",
        "ctx_size": "52105",
        "temp": "0.7",
        "top_k": "40",
        "top_p": "0.9",
        "n_predict": "512",
        "n_threads": "4",
        "path": "",
    }
    resp = client.post("/tuning", data=payload)
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True

    html = client.get("/tuning").get_data(as_text=True)
    assert "CodeLlama-7B-Instruct" in html
    assert 'value="Q5_K_M"' in html
    assert 'value="52105"' in html


def test_tuning_requires_model_key(app):
    client = app.test_client()
    resp = client.post(
        "/tuning",
        data={
            "model_name": "X",
            "quantization": "Q4_K_M",
            "n_gpu_layers": "all",
            "ctx_size": "0",
            "temp": "0.7",
            "top_k": "40",
            "top_p": "0.9",
            "n_predict": "512",
            "n_threads": "4",
            "path": "",
        },
    )
    assert resp.status_code == 400
    assert resp.get_json()["ok"] is False


def test_dirs_add_and_delete(app):
    client = app.test_client()
    resp = client.post("/dirs", data={"action": "add", "path": "/tmp/models-new"})
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True

    html = client.get("/admin").get_data(as_text=True)
    assert "/tmp/models-new" in html

    resp = client.post("/dirs", data={"action": "delete", "path": "/tmp/models-new"})
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True

    html = client.get("/admin").get_data(as_text=True)
    assert "/tmp/models-new" not in html


def test_dirs_add_rejects_empty(app):
    client = app.test_client()
    resp = client.post("/dirs", data={"action": "add", "path": "  "})
    assert resp.status_code == 400
    assert resp.get_json()["ok"] is False


def test_admin_page_renders_and_lists_dirs(app):
    client = app.test_client()
    # Add a directory so the portal can render it.
    client.post("/dirs", data={"action": "add", "path": "/tmp/admin-test-dir"})

    resp = client.get("/admin")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Admin — Model directories" in html
    assert "Configured directories" in html
    assert 'action="/dirs"' in html
    assert "data-path" in html
    # The added directory appears in the table.
    assert "/tmp/admin-test-dir" in html
    # Each configured directory has a remove form.
    assert html.count('<form method="post" action="/dirs"') >= 1
    # Model counts are presented next to each directory row.
    assert "Models" in html
