"""Exercise the actual dashboard against the locally built sample marts."""

import os

import pytest
from streamlit.testing.v1 import AppTest

from taxi_pipeline.config import ROOT


def test_dashboard_payment_filter_and_metrics():
    if not os.getenv("POSTGRES_TEST_URL"):
        pytest.skip("Build the sample marts and set POSTGRES_TEST_URL for dashboard verification")
    app = AppTest.from_file(str(ROOT / "dashboards/streamlit/app.py"), default_timeout=30).run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "8"
    assert app.metric[1].value == "2.12 miles"
    assert app.metric[2].value == "$5.29"
    app.sidebar.selectbox[0].select("Cash").run()
    assert not app.exception
    assert app.metric[0].value == "3"
    app.sidebar.selectbox[0].select("Credit card").run()
    assert app.metric[0].value == "5"
