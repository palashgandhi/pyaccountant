from pyaccountant import pyaccountant


class TestOrchestrator(object):
    def setup(self):
        pyaccountant.app.config["TESTING"] = True
        pyaccountant.app.config["WTF_CSRF_ENABLED"] = False
        pyaccountant.app.config["DEBUG"] = False
        self.app = pyaccountant.app.test_client()

    def teardown(self):
        pass


def test_main_page():
    orchestrator = TestOrchestrator()
    try:
        orchestrator.setup()
        response = orchestrator.app.get("/", follow_redirects=True)
        assert response.status_code == 200
    finally:
        orchestrator.teardown()
