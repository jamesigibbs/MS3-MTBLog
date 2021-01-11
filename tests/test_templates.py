import pytest
from .utils import template_exists


def test_home_template():
    assert template_exists(
        "home"
    ), "The `home.html` template does not exist in the `templates` folder."


def test_register_template():
    assert template_exists(
        "register"
    ), "The `register.html` template does not exist in the `templates` folder."


def test_login_template():
    assert template_exists(
        "login"
    ), "The `login.html` template does not exist in the `templates` folder."


def test_prelog_template():
    assert template_exists(
        "prelog-base"
    ), '''The `prelog-base.html`
            template does not exist in the `templates` folder.'''


def test_postlog_template():
    assert template_exists(
        "postlog-base"
    ), ''''The `postlog-base.html`
            template does not exist in the `templates` folder.'''


def test_logs_template():
    assert template_exists(
        "logs"
    ), "The `logs.html` template does not exist in the `templates` folder."


def test_add_log_template():
    assert template_exists(
        "add_log"
    ), "The `add_log.html` template does not exist in the `templates` folder."


def test_edit_log_template():
    assert template_exists(
        "edit_log"
    ), "The `edit_log.html` template does not exist in the `templates` folder."


def test_admin_template():
    assert template_exists(
        "admin"
    ), "The `admin.html` template does not exist in the `templates` folder."
