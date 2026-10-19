from infrastructure.persistence.database import ENGINE_KWARGS, sessionmanager


def test_engine_hides_query_parameters_from_logs():
    assert ENGINE_KWARGS["hide_parameters"] is True
    assert sessionmanager._engine.sync_engine.hide_parameters is True
