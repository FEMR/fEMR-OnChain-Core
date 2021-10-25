from django.test.client import RequestFactory

from main.views import healthcheck


def test_healthcheck():
    factory = RequestFactory()
    request = factory.get('/healthcheck')
    response = healthcheck(request)
    assert response.status_code, 200
