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
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context options."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-US",
    }
