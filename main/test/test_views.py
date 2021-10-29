from django.test.client import RequestFactory

from main.views import healthcheck


def test_healthcheck():
    factory = RequestFactory()
    request = factory.get("/healthcheck")
    return_response = healthcheck(request)
    assert return_response.status_code, 200
