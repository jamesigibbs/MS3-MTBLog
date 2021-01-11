import pytest
from .utils import template_exists


def test_login_template():
    assert template_exists(
        "login"
    ), "The `login.html` template does not exist in the `templates` folder."
# write for each template


