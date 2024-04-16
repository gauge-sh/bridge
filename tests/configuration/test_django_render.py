import builtins

import pytest

from bridge.config import BridgeConfig
from bridge.framework.django import DjangoHandler
from bridge.platform import Platform


@pytest.fixture
def render_env(mocker):
    mocker.patch(
        "os.environ",
        {
            "BRIDGE_PLATFORM": "render",
            "DATABASE_URL": "postgres://render:password@renderpg:5432/renderdb",
            "REDIS_URL": "redis://renderredis:6379/0",
            "CELERY_BROKER_URL": "redis://renderredis:6379/0",
            "CELERY_RESULT_BACKEND": "redis://renderredis:6379/0",
            "SECRET_KEY": "fakesecret",
            "WEB_CONCURRENCY": "4",
            "DEBUG": "False",
        },
    )


@pytest.fixture
def django_settings():
    return {
        "ALLOWED_HOSTS": ["localhost"],
        "DATABASES": {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "db.sqlite3",
            }
        },
        "STATIC_URL": "/static/",
        "BASE_DIR": "test",
        "DEBUG": True,
        "SECRET_KEY": "secret",
    }


@pytest.fixture
def django_handler(django_settings):
    bridge_config = BridgeConfig()
    return DjangoHandler(
        project_name="test",
        framework_locals=django_settings,
        bridge_config=bridge_config,
    )


def was_module_imported(import_mock, module_name):
    """Check if the specified module was attempted to be imported."""
    return any(
        call_args[0][0] == module_name for call_args in import_mock.call_args_list
    )


def test_configure_postgres(render_env, django_handler):
    django_handler.configure_postgres(platform=Platform.RENDER)
    assert django_handler.framework_locals["DATABASES"] == {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "renderdb",
            "USER": "render",
            "PASSWORD": "password",
            "HOST": "renderpg",
            "PORT": 5432,
        }
    }


def test_configure_worker(mocker, render_env, django_handler):
    mocked_django_celery_module = mocker.MagicMock()
    mocker.patch.dict(
        "sys.modules", {"bridge.service.django_celery": mocked_django_celery_module}
    )
    original_import = builtins.__import__
    mocked_import = mocker.MagicMock(side_effect=original_import)
    mocker.patch("builtins.__import__", mocked_import)
    django_handler.configure_worker(platform=Platform.RENDER)
    assert was_module_imported(mocked_import, "bridge.service.django_celery")
    assert (
        django_handler.framework_locals["CELERY_BROKER_URL"]
        == "redis://renderredis:6379/0"
    )
    assert (
        django_handler.framework_locals["CELERY_RESULT_BACKEND"]
        == "redis://renderredis:6379/0"
    )


def test_configure_allowed_hosts(render_env, django_handler):
    django_handler.configure_allowed_hosts(platform=Platform.RENDER)
    assert set(django_handler.framework_locals["ALLOWED_HOSTS"]) == {
        ".onrender.com",
        "localhost",
    }


def test_configure_debug(render_env, django_handler):
    django_handler.configure_debug(platform=Platform.RENDER)
    assert django_handler.framework_locals["DEBUG"] is False


def test_configure_secret_key(render_env, django_handler):
    django_handler.configure_secret_key(platform=Platform.RENDER)
    assert django_handler.framework_locals["SECRET_KEY"] == "fakesecret"


def test_configure_staticfiles(django_handler):
    django_handler.configure_staticfiles(platform=Platform.RENDER)
    assert django_handler.framework_locals.get("STATIC_URL") == "/static/"
    assert django_handler.framework_locals.get("STATIC_ROOT") == "test/staticfiles"
    assert (
        django_handler.framework_locals.get("STATICFILES_STORAGE")
        == "whitenoise.storage.CompressedManifestStaticFilesStorage"
    )
    assert (
        "whitenoise.middleware.WhiteNoiseMiddleware"
        in django_handler.framework_locals.get("MIDDLEWARE", [])
    )


def test_configure_services(mocker, django_handler):
    mocked_configure_postgres = mocker.patch.object(
        django_handler, "configure_postgres", new=mocker.MagicMock()
    )
    mocked_configure_worker = mocker.patch.object(
        django_handler, "configure_worker", new=mocker.MagicMock()
    )
    django_handler.configure_services(platform=Platform.RENDER)
    mocked_configure_postgres.assert_called_once_with(platform=Platform.RENDER)
    mocked_configure_worker.assert_called_once_with(platform=Platform.RENDER)
