"""Test suite for user interactions with the UI. It is designed to run both
inside and outside of pytest to make future development easier.
"""

import random
import time

import pytest
import requests
from playwright.sync_api import Page, expect, sync_playwright

DEFAULT_TIMEOUT = 60_000  # time in ms

expect.set_options(timeout=DEFAULT_TIMEOUT)


@pytest.fixture
def test_config():
    return {"base_url": "http://localhost:8000"}


def _login_sequence(page, screenshot=False):
    """Conda-store ui login sequence. From the default UI interface, click log
    in and go through the log in UI on the following page. The UI will be
    returned back to the default UI.

    Parameters
    ----------
    page: playwright.Page
        page object for the current test being run
    screenshot: bool
        [Optional] Flag to trigger screenshot collection, set to True to
        grab screenshots
    """
    # Log in sequence
    # Click Login
    page.locator("text=Log in").click()

    if screenshot:
        page.screenshot(path="test-results/conda-store-login_screen.png")

    # Fill in the Username field
    page.locator('[placeholder="Username"]').fill("username")

    # Fill in the Password field
    page.locator('[placeholder="Password"]').fill("password")

    with page.expect_navigation():
        page.locator('button:has-text("Sign In")').click()

    if screenshot:
        page.screenshot(path="test-results/conda-store-authenticated.png")


def _create_new_environment(page, screenshot=False):
    """Workflow to create a new environment in the UI. The env will be
    in the "username" workspace and will have a semi-random number to
    ensure that the env is indeed new since if the environment already
    exists we get a different UI. This allows this test to be run multiple
    times without needing to empty the database.

    Note: this environment takes about a minute to create
    WARNING: Changes to this method will require reflective changes on
    `_existing_environment_interactions` since it uses this env.

    Parameters
    ----------
    page: playwright.Page
        page object for the current test being run
    screenshot: bool
        [Optional] Flag to trigger screenshot collection, set to True to
        grab screenshots
    """
    # ensure new filename in case this test is run multiple times
    new_env_name = f"test_env_{random.randint(0, 100000)}"
    # set timeout for building the environment
    time_to_build_env = 5 * 60 * 1000  # 5 minutes in milliseconds

    # Create the new environment
    # click the + to create a new env
    page.get_by_label("Create a new environment in the username namespace").click()
    if screenshot:
        page.screenshot(path="test-results/conda-store-new-env.png")
    # fill in the env name
    page.get_by_label("Environment name").fill(new_env_name)
    # fill in the description
    page.get_by_placeholder("Enter here the description of your environment").fill(
        "description"
    )
    # click the + to add a package
    page.get_by_role("button", name="+ Add Package").click()
    # add a package to the ui
    page.get_by_label("Enter package").fill("rich")
    page.get_by_role("option", name="rich", exact=True).click()
    # open up the channels accordion card
    page.get_by_role("button", name="Channels").click()
    # click the + to add a channel
    page.get_by_role("button", name="+ Add Channel").click()
    # fill in conda-forge as the new channel name
    page.get_by_label("Enter channel").fill("conda-forge")
    # press enter to submit the channel to the list
    page.get_by_label("Enter channel").press("Enter")
    # click create to start building the env
    page.get_by_role("button", name="Create", exact=True).click()

    # Interact with the environment shortly after creation
    # click to open the Active environment dropdown menu
    page.get_by_text(" - Active", exact=False).click()
    # click on the Active environment on the dropdown menu item (which is currently building)
    page.get_by_role("option", name=" - Active", exact=False).click()
    # ensure that the environment is building
    expect(page.get_by_test_id("build-status")).to_contain_text("Building", )
    # wait until the status is `Completed`
    completed = page.get_by_text("Completed", exact=False)
    completed.wait_for(state="attached", timeout=time_to_build_env)
    expect(completed).to_be_visible()

    return new_env_name


def _existing_environment_interactions(
    page, env_name, time_to_build_env=5 * 60 * 1000, screenshot=False
):
    """test interactions with existing environments.
    During this test, the test will be rebuilt twice.

    Note: This test assumes the environment being tested is the one from
    `_create_new_environment`. Changes to that method will require changes
    here as well (expected existing packages, etc).

    Parameters
    ----------
    page: playwright.Page
        page object for the current test being run
    env_name: str
        Name of existing environment to interact with - must already exist!
    time_to_build_env: float
        [Optional] Time to wait for an updated environment to rebuild in ms
    screenshot: bool
        [Optional] Flag to trigger screenshot collection, set to True to
        grab screenshots

    """
    env_link = page.get_by_role("link", name=env_name)
    edit_button = page.get_by_role("button", name="Edit")

    # edit existing environment through the YAML editor
    env_link.click()
    edit_button.click()
    page.get_by_label("YAML").check()
    if screenshot:
        page.screenshot(path="test-results/conda-store-yaml-editor.png")

    # set the YAML editor to a particular environment specification
    yaml_editor = page.get_by_test_id("yaml-editor").get_by_role("textbox")
    # note: I'm not sure this is necessary but I deliberately chose to match
    # text near the end of the editor to prevent the possibility of Playwright
    # acting on the editor before it has finished rendering its initial value
    yaml_editor.filter(has_text=r"variables: {}").clear()
    yaml_editor.fill(
        "channels:\n  - conda-forge\ndependencies:\n  - rich\n  - python\n  - pip:\n      - nothing\n  - ipykernel\n\n"
    )

    page.get_by_role("button", name="Save").click()
    edit_button.wait_for(state="attached")

    # wait until the status is `Completed`
    completed = page.get_by_text("Completed", exact=False)
    completed.wait_for(state="attached", timeout=time_to_build_env)

    # ensure the namespace is expanded
    try:
        expect(env_link).to_be_visible()
    except Exception:
        # click to expand the `username` name space (but not click the +)
        page.get_by_role(
            "button", name="username Create a new environment in the username namespace"
        ).click()

    # edit existing environment
    env_link.click()
    edit_button.click()
    # page.get_by_placeholder("Enter here the description of your environment").click()
    # change the description
    page.get_by_placeholder("Enter here the description of your environment").fill(
        "new description"
    )
    # change the vesion spec of an existing package
    page.get_by_role("row", name="rich").get_by_role("button").first.click()
    page.get_by_role("option", name="12.5.1").click()
    # Note: purposefully not testing version constraint since there is inconsistent behavior here

    # add a new package
    page.get_by_role("button", name="+ Add Package").click()
    page.get_by_label("Enter package").fill("click")
    page.get_by_role("option", name="click", exact=True).click()
    # Note: purposefully not testing version constraint since there is inconsistent behavior here

    # delete a package
    page.get_by_role("row", name="rich", exact=False).get_by_test_id(
        "RemovePackageTest"
    ).click()

    # promote a package installed as dependency to specified package
    page.get_by_test_id("PromoteIcon").first.click()

    # delete conda-forge channel
    page.get_by_test_id("DeleteIcon").click()
    # add conda-forge channel
    page.get_by_role("button", name="+ Add Channel").click()
    page.get_by_label("Enter channel").fill("conda-forge")
    page.get_by_label("Enter channel").press("Enter")
    # click save to start the new env build
    page.get_by_role("button", name="Save").click()
    edit_button.wait_for(state="attached")

    # wait until the status is `Completed`
    completed = page.get_by_text("Completed", exact=False)
    completed.wait_for(state="attached", timeout=time_to_build_env)

    # Edit -> Cancel editing
    edit_button.click()
    page.get_by_role("button", name="Cancel").click()

    # Edit -> Delete environment
    edit_button.click()
    page.get_by_text("Delete environment").click()
    page.get_by_role("button", name="Delete").click()

    expect(env_link).not_to_be_visible()


def test_integration(page: Page, test_config, screenshot):
    """Basic integration test.

    When this test runs in CI, we launch the webpack server as a detached
    service at the same time that this test is run. For this reason, we
    have a try/except here to allow the webpack server to finish deploying
    before the test begins.

    Parameters
    ----------
    page: playwright.Page
        page object for the current test being run
    test_config:
        Fixture containing the configuration env vars
    screenshot: bool
        Fixture flag to trigger screenshot collection, set to True to
        grab screenshots
    """
    # wait for server to spin up if necessary
    server_running = False
    retry_wait_time = 2  # seconds
    max_wait_time = 4 * 60  # 4 minutes
    elapsed_wait_time = 0
    # loop until server is running or max_wait_time is reached
    while not server_running and elapsed_wait_time < max_wait_time:
        try:
            requests.head(
                test_config["base_url"], allow_redirects=True
            ).status_code != 200
            server_running = True
        except requests.exceptions.ConnectionError:
            elapsed_wait_time += retry_wait_time
            time.sleep(retry_wait_time)

    # Go to http://localhost:{server_port}
    page.goto(
        test_config["base_url"], wait_until="domcontentloaded", timeout=4 * 60 * 1000
    )

    page.screenshot(path="test-results/conda-store-unauthenticated.png")
    if screenshot:
        page.screenshot(path="test-results/conda-store-unauthenticated.png")

    # Log in to conda-store
    _login_sequence(page, screenshot=screenshot)

    # create a new environment
    env_name = _create_new_environment(page, screenshot=screenshot)

    # interact with an existing environment
    _existing_environment_interactions(page, env_name, screenshot=screenshot)


if __name__ == "__main__":
    """This sequence runs through the basic UI test outside of pytest to allow
    for more control during development. It is not intended to be used in CI.
    """

    config = {
        "base_url": "http://localhost:8000",
    }
    screenshot = False

    # ########################################################################
    # Start playwright and setup
    playwright = sync_playwright().start()
    # Use playwright.chromium, playwright.firefox or playwright.webkit
    # Pass headless=False to launch() to see the browser UI
    # slow_mo adds milliseconds to each playwright command so humans can follow along
    browser = playwright.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()

    # Go to http://localhost:{server_port}
    page.goto(config["base_url"], wait_until="domcontentloaded")

    # Log in to conda-store
    _login_sequence(page)

    # create a new environment
    env_name = _create_new_environment(page, screenshot=screenshot)

    # interact with an existing environment
    _existing_environment_interactions(page, env_name, screenshot=screenshot)

    browser.close()
    playwright.stop()
