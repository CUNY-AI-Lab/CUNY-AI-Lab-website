"""Browser contract tests for the signed request-access intake routes.

Both modes use the verified CUNY session identity. Class applications retain
their class-specific fields at `/request-access/class-api`.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from playwright.sync_api import Page, Route, expect, sync_playwright


BASE_URL = os.environ.get("CAIL_TEST_BASE", "http://127.0.0.1:4321")
IDENTITY_URL = "https://tools.ailab.gc.cuny.edu/request-access/identity"
SIGN_IN_URL = "https://tools.ailab.gc.cuny.edu/request-access/sign-in"
INDIVIDUAL_INTAKE_URL = "https://tools.ailab.gc.cuny.edu/request-access/api"
CLASS_INTAKE_URL = "https://tools.ailab.gc.cuny.edu/request-access/class-api"

# Model the external widget lifecycle, including a reset that invalidates the token.
# Tests deliver the next completion explicitly, rather than assuming immediate refresh.
TURNSTILE_SCRIPT = """
window.turnstile = {
  render(container, options) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'cf-turnstile-response';
    container.append(input);
    window.testTurnstile = {
      solve(token) { input.value = token; options.callback(token); },
      notify(name) { input.value = ''; options[name](); },
      clear() { input.value = ''; }
    };
    return 'test-widget';
  },
  reset() { window.testTurnstile.clear(); }
};
"""


def cors_headers() -> dict[str, str]:
    return {
        "access-control-allow-origin": BASE_URL,
        "access-control-allow-credentials": "true",
        "access-control-allow-methods": "GET,POST,OPTIONS",
        "access-control-allow-headers": "content-type",
        "cache-control": "no-store",
        "vary": "Origin",
    }


def assert_equal(actual: Any, expected: Any) -> None:
    assert actual == expected, f"expected {expected!r}, got {actual!r}"


def mock_turnstile(page: Page) -> None:
    page.route(
        "https://challenges.cloudflare.com/**",
        lambda route: route.fulfill(status=200, content_type="application/javascript", body=TURNSTILE_SCRIPT),
    )


def add_turnstile_token(page: Page, value: str = "test-turnstile-token") -> None:
    page.wait_for_function("window.testTurnstile !== undefined")
    page.evaluate("token => window.testTurnstile.solve(token)", value)


def add_test_cookie(page: Page) -> None:
    page.context.add_cookies(
        [
            {
                "name": "cail_test_session",
                "value": "present",
                "domain": "tools.ailab.gc.cuny.edu",
                "path": "/",
                "secure": True,
                "sameSite": "None",
            }
        ]
    )


def mock_identity(page: Page, email: str | None = "alex.rivera@cuny.edu") -> list[dict[str, str]]:
    requests: list[dict[str, str]] = []

    def respond(route: Route) -> None:
        requests.append(dict(route.request.headers))
        headers = cors_headers()
        if email is None:
            route.fulfill(
                status=401,
                content_type="application/json",
                headers=headers,
                body=json.dumps({"error": {"code": "authentication_required"}}),
            )
            return
        route.fulfill(
            status=200,
            content_type="application/json",
            headers=headers,
            body=json.dumps({"email": email}),
        )

    page.route(IDENTITY_URL, respond)
    return requests


def wait_for_identity(page: Page) -> None:
    page.get_by_text(
        "Signed in with CUNY Login. We will use this verified email for your request."
    ).wait_for()


def intended_response(page: Page):
    label = "How will you use the Lab’s tools in your course?" if class_choice(page).is_checked() else "Intended Use or Support Request"
    return page.get_by_role("textbox", name=label)


def fill_common(page: Page, affiliation: str = "faculty") -> dict[str, str]:
    values = {
        "name": "Alex Rivera",
        "affiliation": affiliation,
        "department": "Digital Humanities",
        "campus": "Graduate Center",
        "intendedUse": "Coursework using Lab tools.",
    }
    page.get_by_label("Full Name").fill(values["name"])
    page.get_by_label("CUNY Affiliation").select_option(values["affiliation"])
    page.get_by_label("Department/Program").fill(values["department"])
    page.get_by_label("CUNY College/Campus").fill(values["campus"])
    intended_response(page).fill(values["intendedUse"])
    return values


def capture_success(
    page: Page,
    request_id: str,
    intake_url: str,
    request_headers: list[dict[str, str]] | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    payloads: list[dict[str, Any]] = []
    unexpected_urls: list[str] = []

    def respond(route: Route) -> None:
        if route.request.method == "OPTIONS":
            route.fulfill(status=204, headers=cors_headers())
            return
        if request_headers is not None:
            request_headers.append(dict(route.request.headers))
        payloads.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(
            status=201,
            content_type="application/json",
            headers=cors_headers(),
            body=json.dumps({"requestId": request_id}),
        )

    def reject_unexpected(route: Route) -> None:
        if route.request.method == "OPTIONS":
            route.fulfill(status=204, headers=cors_headers())
            return
        unexpected_urls.append(route.request.url)
        route.fulfill(
            status=500,
            content_type="application/json",
            headers=cors_headers(),
            body=json.dumps({"error": {"code": "wrong_intake_endpoint"}}),
        )

    other_url = CLASS_INTAKE_URL if intake_url == INDIVIDUAL_INTAKE_URL else INDIVIDUAL_INTAKE_URL
    page.route(intake_url, respond)
    page.route(other_url, reject_unexpected)
    return payloads, unexpected_urls


def individual_choice(page: Page):
    return page.locator('input[name="application-kind"][value="individual"]')


def class_choice(page: Page):
    return page.locator('input[name="application-kind"][value="class"]')


def assert_request_id(value: Any) -> None:
    assert isinstance(value, str)
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
        value,
    )


def test_unauthenticated_individual_has_cuny_sign_in_path(page: Page) -> None:
    mock_identity(page, email=None)
    page.goto(f"{BASE_URL}/request-access/")
    page.get_by_text("Sign in with CUNY Login before submitting an access request.").wait_for()
    sign_in = page.get_by_role("link", name="Sign in with CUNY Login")
    assert_equal(sign_in.get_attribute("href"), SIGN_IN_URL)
    assert page.get_by_role("button", name="Submit Application").is_disabled()
    assert page.locator("#verified-email").text_content() == (
        "Sign in with CUNY Login to load your verified email."
    )
    class_choice(page).check()
    assert page.get_by_role("link", name="Sign in with CUNY Login").is_visible()
    assert page.get_by_role("button", name="Submit Application").is_disabled()


def test_individual_mode(page: Page) -> None:
    identity_requests = mock_identity(page)
    page.goto(f"{BASE_URL}/request-access/")
    wait_for_identity(page)
    form = page.locator("#access-request-form")
    assert_equal(form.get_attribute("action"), INDIVIDUAL_INTAKE_URL)
    assert_equal(form.get_attribute("data-intake-url"), INDIVIDUAL_INTAKE_URL)
    assert_equal(form.get_attribute("data-class-intake-url"), CLASS_INTAKE_URL)
    assert individual_choice(page).is_checked()
    assert page.locator("#individual-fields").is_visible()
    assert page.locator("#class-fields").is_hidden()
    assert page.locator("#class-fields").evaluate("fieldset => fieldset.disabled")
    assert_equal(page.locator("#verified-email").text_content(), "alex.rivera@cuny.edu")
    assert identity_requests and "cail_test_session=present" in identity_requests[0].get("cookie", "")

    common = fill_common(page)
    page.get_by_label("CAIL Sandbox").check()
    page.get_by_label("Dashboard and API keys").check()

    # Values retained in the inactive mode must not leak into the individual payload.
    class_choice(page).check()
    assert_equal(form.get_attribute("action"), CLASS_INTAKE_URL)
    page.get_by_label("Class Name").fill("Introduction to Digital Humanities")
    page.get_by_label("Term").fill("Fall 2026")
    page.get_by_label("Section").fill("01")
    page.get_by_label("Start Date").fill("2026-08-25")
    page.get_by_label("End Date").fill("2026-12-20")
    page.get_by_label("Estimated Enrollment").fill("30")
    individual_choice(page).check()
    assert_equal(form.get_attribute("action"), INDIVIDUAL_INTAKE_URL)
    assert page.locator("#class-fields").evaluate("fieldset => fieldset.disabled")
    assert_equal(page.locator("#class-name").get_attribute("required"), None)
    assert page.get_by_label("I teach or lead this class").is_disabled()

    add_turnstile_token(page)
    request_headers: list[dict[str, str]] = []
    payloads, unexpected_urls = capture_success(
        page,
        "req-individual",
        INDIVIDUAL_INTAKE_URL,
        request_headers,
    )
    page.get_by_role("button", name="Submit Application").click()
    page.get_by_role("heading", name="Thank you").wait_for()
    assert page.locator("#access-request-form").is_hidden()
    assert_equal(page.locator("#submission-confirmation").get_attribute("role"), "region")
    assert_equal(len(payloads), 1)
    assert_equal(unexpected_urls, [])
    assert request_headers and "cail_test_session=present" in request_headers[0].get("cookie", "")

    payload = payloads[0]
    assert_equal(
        set(payload),
        {
            "clientRequestId",
            "turnstileToken",
            "name",
            "affiliation",
            "department",
            "campus",
            "intendedUse",
            "tools",
        },
    )
    assert_request_id(payload.pop("clientRequestId"))
    assert_equal(
        payload,
        {
            "turnstileToken": "test-turnstile-token",
            **common,
            "tools": ["sandbox", "model-access"],
        },
    )
    assert page.get_by_text(
        "Your application has been submitted. The CUNY AI Lab will review it and contact you by email."
    ).is_visible()


def test_post_session_expiry_requires_reauth_and_keeps_retry_id(page: Page) -> None:
    state: dict[str, Any] = {
        "posts": 0,
        "payloads": [],
    }

    def respond_identity(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            headers=cors_headers(),
            body=json.dumps({"email": "alex.rivera@cuny.edu"}),
        )

    def respond_intake(route: Route) -> None:
        if route.request.method == "OPTIONS":
            route.fulfill(status=204, headers=cors_headers())
            return
        if route.request.method != "POST":
            route.continue_()
            return
        payload = json.loads(route.request.post_data or "{}")
        state["payloads"].append(payload)
        state["posts"] += 1
        if state["posts"] == 1:
            route.fulfill(
                status=401,
                content_type="application/json",
                headers=cors_headers(),
                body=json.dumps(
                    {
                        "error": {
                            "code": "authentication_required"
                        }
                    }
                ),
            )
            return
        route.fulfill(
            status=201,
            content_type="application/json",
            headers=cors_headers(),
            body=json.dumps({"requestId": "req-reauth-individual"}),
        )

    page.route(IDENTITY_URL, respond_identity)
    page.route(INDIVIDUAL_INTAKE_URL, respond_intake)
    page.goto(f"{BASE_URL}/request-access/")
    wait_for_identity(page)
    fill_common(page)
    add_turnstile_token(page)

    page.get_by_role("button", name="Submit Application").click()
    page.get_by_text("Your CUNY sign-in expired. Sign in again before resending this request.").wait_for()
    assert page.get_by_role("link", name="Sign in with CUNY Login").get_attribute("href") == SIGN_IN_URL
    assert page.get_by_role("button", name="Submit Application").is_disabled()
    assert page.locator("#verified-email").text_content() == (
        "Sign in with CUNY Login to load your verified email."
    )
    assert page.get_by_role("button", name="Check again").is_visible()

    add_turnstile_token(page, "refreshed-token")
    assert page.get_by_role("button", name="Submit Application").is_disabled()
    page.get_by_role("button", name="Check again").click()
    wait_for_identity(page)
    page.get_by_role("button", name="Submit Application").click()
    page.get_by_role("heading", name="Thank you").wait_for()

    payloads = state["payloads"]
    assert_equal(len(payloads), 2)
    assert_equal(payloads[0]["clientRequestId"], payloads[1]["clientRequestId"])


def test_reauth_as_different_identity_gets_new_retry_id(page: Page) -> None:
    state: dict[str, Any] = {
        "identity_email": "alex.rivera@cuny.edu",
        "posts": 0,
        "payloads": [],
    }

    def respond_identity(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            headers=cors_headers(),
            body=json.dumps({"email": state["identity_email"]}),
        )

    def respond_intake(route: Route) -> None:
        if route.request.method == "OPTIONS":
            route.fulfill(status=204, headers=cors_headers())
            return
        payload = json.loads(route.request.post_data or "{}")
        state["payloads"].append(payload)
        state["posts"] += 1
        if state["posts"] == 1:
            state["identity_email"] = "different.user@cuny.edu"
            route.fulfill(
                status=401,
                content_type="application/json",
                headers=cors_headers(),
                body=json.dumps({"error": {"code": "authentication_required"}}),
            )
            return
        route.fulfill(
            status=201,
            content_type="application/json",
            headers=cors_headers(),
            body=json.dumps({"requestId": "req-different-identity"}),
        )

    page.route(IDENTITY_URL, respond_identity)
    page.route(INDIVIDUAL_INTAKE_URL, respond_intake)
    page.goto(f"{BASE_URL}/request-access/")
    wait_for_identity(page)
    fill_common(page)
    add_turnstile_token(page)

    page.get_by_role("button", name="Submit Application").click()
    page.get_by_text("Your CUNY sign-in expired. Sign in again before resending this request.").wait_for()
    page.get_by_role("button", name="Check again").click()
    wait_for_identity(page)
    assert page.locator("#verified-email").text_content() == "different.user@cuny.edu"
    assert page.get_by_role("button", name="Submit Application").is_disabled()
    add_turnstile_token(page, "refreshed-token")
    page.get_by_role("button", name="Submit Application").click()
    page.get_by_role("heading", name="Thank you").wait_for()

    payloads = state["payloads"]
    assert_equal(len(payloads), 2)
    assert payloads[0]["clientRequestId"] != payloads[1]["clientRequestId"]


def test_class_mode(page: Page) -> None:
    mock_identity(page)
    page.goto(f"{BASE_URL}/request-access/?kind=class")
    wait_for_identity(page)
    assert class_choice(page).is_checked()
    assert_equal(page.locator("#access-request-form").get_attribute("action"), CLASS_INTAKE_URL)
    assert page.locator("#class-fields").is_visible()
    assert not page.locator("#class-fields").evaluate("fieldset => fieldset.disabled")
    assert page.locator("#individual-fields").is_hidden()
    assert page.locator("#individual-fields").evaluate("fieldset => fieldset.disabled")
    assert_equal(page.get_by_label("Class Name").get_attribute("required"), "")

    # An individual-only tool selection must stay out of a later class payload.
    individual_choice(page).check()
    page.get_by_label("CAIL Sandbox").check()
    class_choice(page).check()
    assert_equal(page.locator("#access-request-form").get_attribute("action"), CLASS_INTAKE_URL)
    assert page.get_by_label("CAIL Sandbox").is_disabled()

    # Class intake is not restricted to faculty or to existing Lab members.
    common = fill_common(page, affiliation="other")
    add_turnstile_token(page)
    request_headers: list[dict[str, str]] = []
    payloads, unexpected_urls = capture_success(
        page,
        "req-class",
        CLASS_INTAKE_URL,
        request_headers,
    )

    # Native required validation blocks submission before any request is sent.
    page.get_by_role("button", name="Submit Application").click()
    assert_equal(len(payloads), 0)
    assert_equal(page.evaluate("document.activeElement?.id"), "class-name")

    page.get_by_label("Class Name").fill("Introduction to Digital Humanities")
    page.get_by_label("Term").fill("Fall 2026")
    page.get_by_label("Section").fill("01")
    page.get_by_label("Start Date").fill("2026-08-25")
    page.get_by_label("End Date").fill("2026-12-20")
    page.get_by_label("Estimated Enrollment").fill("30")

    # The checkbox gates submission locally; Admission accepts no classLeader field.
    page.get_by_role("button", name="Submit Application").click()
    assert_equal(len(payloads), 0)
    assert_equal(page.evaluate("document.activeElement?.id"), "class-leader")
    page.get_by_label("I teach or lead this class").check()

    # Fallback browsers that treat date inputs as text still cannot send non-ISO dates.
    page.get_by_label("Start Date").evaluate("input => input.type = 'text'")
    page.get_by_label("End Date").evaluate("input => input.type = 'text'")
    page.get_by_label("Start Date").fill("08/25/2026")
    page.get_by_label("End Date").fill("12/20/2026")
    page.get_by_role("button", name="Submit Application").click()
    page.get_by_text("Enter valid class start and end dates.").wait_for()
    assert_equal(len(payloads), 0)
    assert_equal(page.evaluate("document.activeElement?.id"), "starts-on")
    page.get_by_label("Start Date").evaluate("input => input.type = 'date'")
    page.get_by_label("End Date").evaluate("input => input.type = 'date'")
    page.get_by_label("Start Date").fill("2026-08-25")
    page.get_by_label("End Date").fill("2026-12-20")

    page.get_by_label("End Date").fill("2026-08-24")
    page.get_by_role("button", name="Submit Application").click()
    page.get_by_text("The class end date must be on or after the start date.").wait_for()
    assert_equal(len(payloads), 0)
    assert_equal(page.evaluate("document.activeElement?.id"), "ends-on")

    # The public end date is inclusive, so a same-day class is valid.
    page.get_by_label("End Date").fill("2026-08-25")
    page.get_by_role("button", name="Submit Application").click()
    page.get_by_role("heading", name="Thank you").wait_for()
    assert page.locator("#access-request-form").is_hidden()
    assert page.get_by_text(
        "Your class application has been submitted. The CUNY AI Lab will review it and contact you by email."
    ).is_visible()
    assert_equal(len(payloads), 1)
    assert_equal(unexpected_urls, [])

    payload = payloads[0]
    assert_equal(
        set(payload),
        {
            "clientRequestId",
            "turnstileToken",
            "name",
            "affiliation",
            "department",
            "campus",
            "intendedUse",
            "className",
            "term",
            "section",
            "startsOn",
            "endsOn",
            "estimatedSeats",
        },
    )
    assert_request_id(payload.pop("clientRequestId"))
    assert_equal(
        payload,
        {
            "turnstileToken": "test-turnstile-token",
            **common,
            "className": "Introduction to Digital Humanities",
            "term": "Fall 2026",
            "section": "01",
            "startsOn": "2026-08-25",
            "endsOn": "2026-08-25",
            "estimatedSeats": 30,
        },
    )


def test_keyboard_navigation_and_safe_error_retry(page: Page) -> None:
    mock_identity(page)
    page.goto(f"{BASE_URL}/request-access/")
    wait_for_identity(page)
    individual = individual_choice(page)
    individual.focus()
    individual.press("ArrowRight")
    assert class_choice(page).is_checked()
    assert "kind=class" in page.url
    class_choice(page).press("ArrowLeft")
    assert individual.is_checked()
    assert "kind=individual" in page.url

    fill_common(page)
    add_turnstile_token(page)
    attempts = 0

    def fail_once_then_succeed(route: Route) -> None:
        nonlocal attempts
        if route.request.method == "OPTIONS":
            route.fulfill(status=204, headers=cors_headers())
            return
        attempts += 1
        if attempts == 1:
            route.fulfill(
                status=503,
                content_type="application/json",
                headers=cors_headers(),
                body=json.dumps({"error": {"code": "admission_unavailable", "message": "private detail"}}),
            )
            return
        route.fulfill(
            status=201,
            content_type="application/json",
            headers=cors_headers(),
            body=json.dumps({"requestId": "req-retry"}),
        )

    page.route(INDIVIDUAL_INTAKE_URL, fail_once_then_succeed)
    submit = page.get_by_role("button", name="Submit Application")
    submit.click()
    status = page.locator("#form-status")
    status.get_by_text("The access service is temporarily unavailable. Try again shortly.").wait_for()
    expect(submit).to_be_disabled()
    assert "private detail" not in status.inner_text()

    add_turnstile_token(page, "refreshed-token")
    expect(submit).to_be_enabled()
    submit.click()
    page.get_by_role("heading", name="Thank you").wait_for()
    assert_equal(attempts, 2)


def test_ambiguous_retry_reuses_client_request_id(page: Page) -> None:
    mock_identity(page)
    page.goto(f"{BASE_URL}/request-access/")
    wait_for_identity(page)
    fill_common(page)
    add_turnstile_token(page)
    payloads: list[dict[str, Any]] = []
    attempts = 0

    def lose_first_response(route: Route) -> None:
        nonlocal attempts
        if route.request.method == "OPTIONS":
            route.fulfill(status=204, headers=cors_headers())
            return
        attempts += 1
        payloads.append(json.loads(route.request.post_data or "{}"))
        if attempts == 1:
            route.abort("failed")
            return
        route.fulfill(
            status=201,
            content_type="application/json",
            headers=cors_headers(),
            body=json.dumps({"requestId": "req-ambiguous"}),
        )

    page.route(INDIVIDUAL_INTAKE_URL, lose_first_response)
    submit = page.get_by_role("button", name="Submit Application")
    submit.click()
    page.get_by_text("The access service could not be reached. Check your connection and try again.").wait_for()
    expect(submit).to_be_disabled()

    add_turnstile_token(page, "refreshed-token")
    submit.click()
    page.get_by_role("heading", name="Thank you").wait_for()
    assert_equal(attempts, 2)
    assert_equal(payloads[0]["clientRequestId"], payloads[1]["clientRequestId"])
    assert payloads[0]["turnstileToken"] != payloads[1]["turnstileToken"]


def test_changed_payload_gets_new_client_request_id(page: Page) -> None:
    mock_identity(page)
    page.goto(f"{BASE_URL}/request-access/")
    wait_for_identity(page)
    fill_common(page)
    add_turnstile_token(page)
    payloads: list[dict[str, Any]] = []
    attempts = 0

    def fail_then_succeed(route: Route) -> None:
        nonlocal attempts
        if route.request.method == "OPTIONS":
            route.fulfill(status=204, headers=cors_headers())
            return
        attempts += 1
        payloads.append(json.loads(route.request.post_data or "{}"))
        if attempts == 1:
            route.fulfill(
                status=503,
                content_type="application/json",
                headers=cors_headers(),
                body=json.dumps({"error": {"code": "admission_unavailable"}}),
            )
            return
        route.fulfill(
            status=201,
            content_type="application/json",
            headers=cors_headers(),
            body=json.dumps({"requestId": "req-changed"}),
        )

    page.route(INDIVIDUAL_INTAKE_URL, fail_then_succeed)
    submit = page.get_by_role("button", name="Submit Application")
    submit.click()
    page.get_by_text("The access service is temporarily unavailable. Try again shortly.").wait_for()
    page.get_by_label("Department/Program").fill("English")
    add_turnstile_token(page, "refreshed-token")
    submit.click()
    page.get_by_role("heading", name="Thank you").wait_for()
    assert_equal(attempts, 2)
    assert payloads[0]["clientRequestId"] != payloads[1]["clientRequestId"]
    assert_equal(payloads[1]["department"], "English")


def test_mobile_layout(page: Page) -> None:
    mock_identity(page)
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{BASE_URL}/request-access/?kind=class")
    wait_for_identity(page)
    assert class_choice(page).is_checked()
    dimensions = page.evaluate(
        "({ scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth })"
    )
    assert dimensions["scrollWidth"] <= dimensions["innerWidth"]


def test_class_activity_survives_paste_mode_switch_and_verification_retry(page: Page) -> None:
    mock_identity(page)
    page.goto(f"{BASE_URL}/request-access/?kind=class")
    wait_for_identity(page)
    fill_common(page)
    page.get_by_label("Class Name").fill("Critical Reading")
    page.get_by_label("Term").fill("Fall 2026")
    page.get_by_label("Section").fill("01")
    page.get_by_label("Start Date").fill("2026-09-22")
    page.get_by_label("End Date").fill("2026-12-20")
    page.get_by_label("Estimated Enrollment").fill("25")
    page.get_by_label("I teach or lead this class").check()
    intended = intended_response(page)
    expect(page.get_by_role("textbox", name="Intended Use or Support Request")).to_have_count(0)
    expect(page.locator("#class-application-guidance")).to_be_visible()
    expect(page.locator("#class-intended-use-help")).to_be_visible()
    expect(intended).to_have_attribute("aria-describedby", "class-intended-use-help")

    pasted = "Students compare ‘AI interpretations’ with their own close reading.\r\n\r\n• Model:\tpropose an interpretation.\r\n• Students:\tcheck evidence—then revise.\r\nI assess their reasoning, not agreement. Café\u00a0/ 中文 🥬"
    expected = pasted.replace("\r\n", "\n")
    if os.environ.get("CAIL_TEST_BROWSER", "chromium") == "chromium":
        # Exercise a real clipboard paste in Chromium, not a synthetic paste event.
        page.context.grant_permissions(["clipboard-read", "clipboard-write"])
        page.evaluate("text => navigator.clipboard.writeText(text)", pasted)
        intended.fill("")
        intended.press("ControlOrMeta+V")
    else:
        # Firefox/WebKit check multiline insertion and normalization without clipboard permissions.
        intended.fill(pasted)
    expect(intended).to_have_value(expected)

    individual_choice(page).check()
    expect(intended_response(page)).to_have_value(expected)
    expect(page.locator("#class-application-guidance")).to_be_hidden()
    expect(page.locator("#class-intended-use-help")).to_be_hidden()
    assert intended_response(page).get_attribute("aria-describedby") is None
    class_choice(page).check()
    expect(intended_response(page)).to_have_value(expected)

    payloads: list[dict[str, Any]] = []

    def reject_expired_then_accept(route: Route) -> None:
        if route.request.method == "OPTIONS":
            route.fulfill(status=204, headers=cors_headers())
            return
        payloads.append(route.request.post_data_json)
        first = len(payloads) == 1
        route.fulfill(status=403 if first else 201, headers=cors_headers(), content_type="application/json",
                      body=json.dumps({"error": {"code": "turnstile_failed"}} if first else {"requestId": "req-class-paste"}))

    page.route(CLASS_INTAKE_URL, reject_expired_then_accept)
    add_turnstile_token(page)
    submit = page.get_by_role("button", name="Submit Application")
    intended_response(page).fill(" \n\t\u00a0")
    submit.click()
    expect(intended_response(page)).to_be_focused()
    assert_equal(payloads, [])
    expect(submit).to_be_enabled()
    intended_response(page).fill(expected)
    submit.click()
    expect(page.locator("#form-status")).to_be_visible()
    expect(submit).to_be_disabled()
    expect(intended_response(page)).to_have_value(expected)
    add_turnstile_token(page, "fresh-class-token")
    submit.click()
    expect(page.get_by_role("heading", name="Thank you", exact=True)).to_be_visible()
    assert_equal(len(payloads), 2)
    assert_equal(payloads[0]["intendedUse"], expected)
    assert_equal(payloads[1]["intendedUse"], expected)
    assert_equal(payloads[0]["clientRequestId"], payloads[1]["clientRequestId"])
    assert_equal(payloads[1]["turnstileToken"], "fresh-class-token")
    assert "tools" not in payloads[1]
    assert "classLeader" not in payloads[1]


def test_verification_lifecycle_keeps_entries_and_blocks_unready_posts(page: Page) -> None:
    mock_identity(page)
    page.goto(f"{BASE_URL}/request-access/")
    wait_for_identity(page)
    fill_common(page)
    intended = page.get_by_label("Intended Use or Support Request")
    text = "Research\twith pasted text\n\nAnd multiple paragraphs."
    intended.fill(text)
    payloads, _ = capture_success(page, "req-recovered", INDIVIDUAL_INTAKE_URL)
    submit = page.get_by_role("button", name="Submit Application")
    expect(submit).to_be_disabled()
    # Enter/requestSubmit must not bypass the disabled-button gate.
    page.locator("form").evaluate("form => form.requestSubmit()")
    assert_equal(payloads, [])

    for callback in ("expired-callback", "error-callback", "timeout-callback"):
        add_turnstile_token(page)
        expect(submit).to_be_enabled()
        page.evaluate("name => window.testTurnstile.notify(name)", callback)
        expect(submit).to_be_disabled()
        expect(intended).to_have_value(text)
        page.get_by_role("button", name="Retry verification").click()
        expect(submit).to_be_disabled()
        page.locator("form").evaluate("form => form.requestSubmit()")
        assert_equal(payloads, [])

    add_turnstile_token(page, "fresh-token")
    submit.click()
    expect(page.get_by_role("heading", name="Thank you", exact=True)).to_be_visible()
    assert_equal(payloads[0]["intendedUse"], text)
    assert_equal(payloads[0]["turnstileToken"], "fresh-token")


def test_rejection_keeps_original_error_until_verified_retry(page: Page) -> None:
    for kind, code in (("individual", 400), ("class", 403)):
        mock_identity(page)
        page.goto(f"{BASE_URL}/request-access/?kind={kind}")
        wait_for_identity(page)
        common = fill_common(page)
        if kind == "class":
            page.get_by_label("Class Name").fill("Research Methods")
            page.get_by_label("Term").fill("Fall 2026")
            page.get_by_label("Section").fill("01")
            page.get_by_label("Start Date").fill("2026-08-25")
            page.get_by_label("End Date").fill("2026-12-20")
            page.get_by_label("Estimated Enrollment").fill("30")
            page.get_by_label("I teach or lead this class").check()
        add_turnstile_token(page)
        payloads = []

        def respond(route: Route) -> None:
            if route.request.method == "OPTIONS":
                route.fulfill(status=204, headers=cors_headers())
                return
            payloads.append(route.request.post_data_json)
            first = len(payloads) == 1
            route.fulfill(
                status=code if first else 201, headers=cors_headers(),
                content_type="application/json",
                body=json.dumps({"error": {"code": "turnstile_failed" if code == 403 else "intake_invalid"}}
                                if first else {"requestId": "req-retried"}),
            )

        endpoint = CLASS_INTAKE_URL if kind == "class" else INDIVIDUAL_INTAKE_URL
        page.route(endpoint, respond)
        submit = page.get_by_role("button", name="Submit Application")
        submit.click()
        status = page.locator("#form-status")
        expect(status).to_be_visible()
        original_error = status.inner_text()
        expect(submit).to_be_disabled()
        expect(page.locator('input[name="cf-turnstile-response"]')).to_have_value("")
        page.locator("form").evaluate("form => form.requestSubmit()")
        expect(status).to_have_text(original_error)
        assert_equal(len(payloads), 1)
        expect(intended_response(page)).to_have_value(common["intendedUse"])
        add_turnstile_token(page, "refreshed-token")
        expect(status).to_have_text(original_error)
        submit.click()
        expect(page.get_by_role("heading", name="Thank you", exact=True)).to_be_visible()
        assert_equal(len(payloads), 2)
        assert_equal(payloads[0]["clientRequestId"], payloads[1]["clientRequestId"])
        assert_equal(payloads[1]["turnstileToken"], "refreshed-token")
        page.unroute(endpoint, respond)


def test_script_failure_can_retry_without_losing_text(page: Page) -> None:
    mock_identity(page)
    script_calls = []

    def script(route: Route) -> None:
        script_calls.append(route.request.url)
        if len(script_calls) == 1:
            route.abort()
        else:
            route.fulfill(content_type="application/javascript", body=TURNSTILE_SCRIPT)

    page.route("https://challenges.cloudflare.com/**", script)
    page.goto(f"{BASE_URL}/request-access/")
    wait_for_identity(page)
    common = fill_common(page)
    submit = page.get_by_role("button", name="Submit Application")
    expect(submit).to_be_disabled()
    page.get_by_role("button", name="Retry verification").click()
    add_turnstile_token(page)
    expect(submit).to_be_enabled()
    expect(page.get_by_label("Intended Use or Support Request")).to_have_value(common["intendedUse"])
    assert_equal(len(script_calls), 2)


def test_verification_before_identity_does_not_enable_submission(page: Page) -> None:
    pending = []
    page.route(IDENTITY_URL, lambda route: pending.append(route))
    page.goto(f"{BASE_URL}/request-access/")
    add_turnstile_token(page)
    submit = page.get_by_role("button", name="Submit Application")
    expect(submit).to_be_disabled()
    # The header and form each check identity; neither may bypass verification.
    assert pending
    for request in pending:
        request.fulfill(status=200, headers=cors_headers(), content_type="application/json",
                        body=json.dumps({"email": "alex.rivera@cuny.edu"}))
    wait_for_identity(page)
    expect(submit).to_be_enabled()
    page.evaluate("window.testTurnstile.notify('unsupported-callback')")
    expect(submit).to_be_disabled()
    expect(page.locator("#verification-status")).to_be_visible()
    expect(page.get_by_role("button", name="Retry verification")).to_be_hidden()


def test_intended_use_validation_focuses_field_without_consuming_token(page: Page) -> None:
    mock_identity(page)
    page.goto(f"{BASE_URL}/request-access/")
    wait_for_identity(page)
    fill_common(page)
    add_turnstile_token(page)
    payloads, _ = capture_success(page, "req-corrected", INDIVIDUAL_INTAKE_URL)
    intended = page.get_by_label("Intended Use or Support Request")
    submit = page.get_by_role("button", name="Submit Application")
    for text in ("   ", "Research\x01analysis"):
        intended.fill(text)
        if intended.input_value() != text:
            # Firefox removes C0 controls during text insertion, before our validator.
            assert_equal(intended.input_value(), text.replace("\x01", ""))
            continue
        submit.click()
        expect(intended).to_be_focused()
        assert intended.evaluate("field => !field.validity.valid")
        assert_equal(payloads, [])
        expect(submit).to_be_enabled()
    intended.fill("Research")
    submit.click()
    expect(page.get_by_role("heading", name="Thank you", exact=True)).to_be_visible()
    assert_equal(len(payloads), 1)


def test_verification_callbacks_cannot_duplicate_inflight_request(page: Page) -> None:
    mock_identity(page)
    page.goto(f"{BASE_URL}/request-access/")
    wait_for_identity(page)
    fill_common(page)
    add_turnstile_token(page)
    pending = []

    def hold(route: Route) -> None:
        if route.request.method == "OPTIONS":
            route.fulfill(status=204, headers=cors_headers())
        else:
            pending.append(route)

    page.route(INDIVIDUAL_INTAKE_URL, hold)
    submit = page.locator("#access-request-submit")
    with page.expect_request(lambda request: request.url == INDIVIDUAL_INTAKE_URL and request.method == "POST"):
        submit.click()
    page.evaluate("window.testTurnstile.notify('expired-callback')")
    add_turnstile_token(page, "another-token")
    expect(submit).to_be_disabled()
    page.locator("form").evaluate("form => form.requestSubmit()")
    assert_equal(len(pending), 1)
    pending[0].fulfill(status=201, headers=cors_headers(), content_type="application/json",
                       body=json.dumps({"requestId": "req-once"}))
    expect(page.get_by_role("heading", name="Thank you", exact=True)).to_be_visible()


def test_public_access_links_use_the_canonical_application(page: Page) -> None:
    page.goto(f"{BASE_URL}/contact/", wait_until="domcontentloaded")
    access_link = page.get_by_role("link", name="CAIL Access")
    assert_equal(access_link.get_attribute("href"), "/request-access/")
    assert access_link.get_attribute("target") is None

    page.goto(f"{BASE_URL}/blog/cuny-login-sso/", wait_until="domcontentloaded")
    assert_equal(
        page.get_by_role("link", name="CAIL access application").get_attribute("href"),
        "/request-access/",
    )


def main() -> None:
    with sync_playwright() as playwright:
        browser = getattr(playwright, os.environ.get("CAIL_TEST_BROWSER", "chromium")).launch()
        try:
            for test in (
                test_unauthenticated_individual_has_cuny_sign_in_path,
                test_individual_mode,
                test_post_session_expiry_requires_reauth_and_keeps_retry_id,
                test_reauth_as_different_identity_gets_new_retry_id,
                test_class_mode,
                test_keyboard_navigation_and_safe_error_retry,
                test_ambiguous_retry_reuses_client_request_id,
                test_changed_payload_gets_new_client_request_id,
                test_class_activity_survives_paste_mode_switch_and_verification_retry,
                test_verification_lifecycle_keeps_entries_and_blocks_unready_posts,
                test_rejection_keeps_original_error_until_verified_retry,
                test_script_failure_can_retry_without_losing_text,
                test_verification_before_identity_does_not_enable_submission,
                test_intended_use_validation_focuses_field_without_consuming_token,
                test_verification_callbacks_cannot_duplicate_inflight_request,
                test_mobile_layout,
                test_public_access_links_use_the_canonical_application,
            ):
                context = browser.new_context(viewport={"width": 1440, "height": 1000})
                page = context.new_page()
                add_test_cookie(page)
                mock_turnstile(page)
                errors: list[str] = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                test(page)
                assert_equal(errors, [])
                context.close()
                print(f"PASS {test.__name__}")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
