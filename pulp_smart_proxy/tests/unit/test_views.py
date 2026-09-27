from types import SimpleNamespace

import django
from django.test import RequestFactory

django.setup()


def features_v2_settings(monkeypatch, capabilities, container_registry_api_url=None):
    from pulp_smart_proxy.app import views

    plugins = [SimpleNamespace(label=capability) for capability in capabilities]
    monkeypatch.setattr(views, "pulp_plugin_configs", lambda: plugins)
    monkeypatch.setattr(
        views,
        "settings",
        SimpleNamespace(
            CONTENT_ORIGIN="https://content.example.test/",
            CONTENT_PATH_PREFIX="/pulp/content/",
            SMART_PROXY_AUTH_METHODS=[],
            SMART_PROXY_AUTH_PASSWORD="password",
            SMART_PROXY_AUTH_USERNAME="admin",
            SMART_PROXY_MIRROR=False,
            SMART_PROXY_PULP_URL="https://pulp.example.test/",
            SMART_PROXY_RHSM_URL=None,
            SMART_PROXY_CONTAINER_REGISTRY_API_URL=container_registry_api_url,
        ),
    )

    request = RequestFactory().get("/pulp/api/v3/smart_proxy/v2/features")
    return views.FeaturesV2View().get(request).data["pulpcore"]["settings"]


def test_container_registry_api_url_defaults_to_pulp_url(monkeypatch):
    settings = features_v2_settings(monkeypatch, ["core", "container"])

    assert settings["container_registry_api_url"] == settings["pulp_url"]


def test_container_registry_api_url_can_be_overridden(monkeypatch):
    settings = features_v2_settings(
        monkeypatch,
        ["core", "container"],
        container_registry_api_url="https://registry.example.test/",
    )

    assert settings["container_registry_api_url"] == "https://registry.example.test/"


def test_container_registry_api_url_is_null_without_container(monkeypatch):
    settings = features_v2_settings(monkeypatch, ["core"])

    assert settings["container_registry_api_url"] is None
