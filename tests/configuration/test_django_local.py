import builtins

import pytest

from bridge.config import BridgeConfig
from bridge.framework.django import DjangoHandler
from bridge.platform import Platform


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


def test_configure_postgres(django_handler):
    django_handler.configure_postgres(platform=Platform.LOCAL)
    assert django_handler.framework_locals["DATABASES"] == {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "localhost",
            "PORT": 5432,
        }
    }


def test_configure_worker(mocker, django_handler):
    mocked_django_celery_module = mocker.MagicMock()
    mocker.patch.dict(
        "sys.modules", {"bridge.service.django_celery": mocked_django_celery_module}
    )
    original_import = builtins.__import__
    mocked_import = mocker.MagicMock(side_effect=original_import)
    mocker.patch("builtins.__import__", mocked_import)
    django_handler.configure_worker(platform=Platform.LOCAL)
    assert was_module_imported(mocked_import, "bridge.service.django_celery")
    assert (
        django_handler.framework_locals["CELERY_BROKER_URL"]
        == "redis://localhost:6379/0"
    )
    assert (
        django_handler.framework_locals["CELERY_RESULT_BACKEND"]
        == "redis://localhost:6379/0"
    )


def test_configure_allowed_hosts(django_handler):
    previous_allowed_hosts = django_handler.framework_locals["ALLOWED_HOSTS"].copy()
    django_handler.configure_allowed_hosts(platform=Platform.LOCAL)
    assert django_handler.framework_locals["ALLOWED_HOSTS"] == previous_allowed_hosts


def test_configure_debug(django_handler):
    previous_debug = django_handler.framework_locals["DEBUG"]
    django_handler.configure_debug(platform=Platform.LOCAL)
    assert django_handler.framework_locals["DEBUG"] == previous_debug


def test_configure_secret_key(mocker, django_handler):
    previous_secret_key = django_handler.framework_locals["SECRET_KEY"]
    django_handler.configure_secret_key(platform=Platform.LOCAL)
    assert django_handler.framework_locals["SECRET_KEY"] == previous_secret_key


def test_configure_staticfiles(django_handler):
    previous_static_url = django_handler.framework_locals.get("STATIC_URL")
    previous_static_root = django_handler.framework_locals.get("STATIC_ROOT")
    previous_staticfiles_dirs = django_handler.framework_locals.get("STATICFILES_DIRS")
    previous_staticfiles_storage = django_handler.framework_locals.get(
        "STATICFILES_STORAGE"
    )
    django_handler.configure_staticfiles(platform=Platform.LOCAL)
    assert django_handler.framework_locals.get("STATIC_URL") == previous_static_url
    assert django_handler.framework_locals.get("STATIC_ROOT") == previous_static_root
    assert (
        django_handler.framework_locals.get("STATICFILES_DIRS")
        == previous_staticfiles_dirs
    )
    assert (
        django_handler.framework_locals.get("STATICFILES_STORAGE")
        == previous_staticfiles_storage
    )


def test_configure_services(mocker, django_handler):
    mocked_configure_postgres = mocker.patch.object(
        django_handler, "configure_postgres", new=mocker.MagicMock()
    )
    mocked_configure_worker = mocker.patch.object(
        django_handler, "configure_worker", new=mocker.MagicMock()
    )
    django_handler.configure_services(platform=Platform.LOCAL)
    mocked_configure_postgres.assert_called_once_with(platform=Platform.LOCAL)
    mocked_configure_worker.assert_called_once_with(platform=Platform.LOCAL)
