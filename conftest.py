import pytest


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch options.
    
    Set headless=True for CI/CD pipelines.
    slow_mo adds a delay (ms) between actions for better readability.
    """
    return {
        **browser_type_launch_args,
        "headless": False,
        "slow_mo": 600,
        "args": ["--start-maximized"],
        "executable_path": "/usr/bin/google-chrome-stable",
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context options."""
    return {
        **browser_context_args,
        "no_viewport": True,
        "locale": "en-US",
    }
