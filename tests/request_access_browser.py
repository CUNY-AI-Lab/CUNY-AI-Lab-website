"""Browser contract tests for the signed request-access intake routes.

Both modes use the verified CUNY session identity. Class applications retain
their class-specific fields at `/request-access/class-api`.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, Route, sync_playwright


BASE_URL = os.environ.get("CAIL_TEST_BASE", "http://127.0.0.1:4321")
IDENTITY_URL = "https://tools.ailab.gc.cuny.edu/request-access/identity"
SIGN_IN_URL = "https://tools.ailab.gc.cuny.edu/request-access/sign-in"
INDIVIDUAL_INTAKE_URL = "https://tools.ailab.gc.cuny.edu/request-access/api"
CLASS_INTAKE_URL = "https://tools.ailab.gc.cuny.edu/request-access/class-api"
ARTIFACTS = Path(os.environ.get("CAIL_TEST_ARTIFACTS", "/tmp/cail-request-access-browser"))


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


def block_turnstile(page: Page) -> None:
    page.route(
        "https://challenges.cloudflare.com/**",
        lambda route: route.fulfill(status=200, content_type="application/javascript", body=""),
    )


def add_turnstile_token(page: Page, value: str = "test-turnstile-token") -> None:
    page.locator("form").evaluate(
        """(form, token) => {
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = 'cf-turnstile-response';
          input.value = token;
          form.append(input);
        }""",
        value,
    )


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
    page.get_by_label("Intended Use or Support Request").fill(values["intendedUse"])
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
    page.get_by_label("Model Access and API keys").check()

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
    assert "email" not in payloads[0]
    assert "subject" not in payloads[0]

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
        "kind": "individual",
        "intake_url": INDIVIDUAL_INTAKE_URL,
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
                            "code": "session_invalid"
                            if state["kind"] == "class"
                            else "authentication_required"
                        }
                    }
                ),
            )
            return
        route.fulfill(
            status=201,
            content_type="application/json",
            headers=cors_headers(),
            body=json.dumps({"requestId": f"req-reauth-{state['kind']}"}),
        )

    page.route(IDENTITY_URL, respond_identity)
    page.route(INDIVIDUAL_INTAKE_URL, respond_intake)
    page.route(CLASS_INTAKE_URL, respond_intake)

    for kind in ("individual", "class"):
        state["kind"] = kind
        state["intake_url"] = CLASS_INTAKE_URL if kind == "class" else INDIVIDUAL_INTAKE_URL
        state["posts"] = 0
        state["payloads"] = []
        page.goto(f"{BASE_URL}/request-access/" + ("?kind=class" if kind == "class" else ""))
        wait_for_identity(page)
        if kind == "class":
            fill_common(page, affiliation="other")
            class_fields = {
                "Class Name": "Introduction to Digital Humanities",
                "Term": "Fall 2026",
                "Section": "01",
                "Start Date": "2026-08-25",
                "End Date": "2026-08-25",
                "Estimated Enrollment": "30",
            }
            for label, value in class_fields.items():
                page.get_by_label(label).fill(value)
            page.get_by_label("I teach or lead this class").check()
        else:
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

        page.get_by_role("button", name="Check again").click()
        wait_for_identity(page)
        page.get_by_role("button", name="Submit Application").click()
        page.get_by_role("heading", name="Thank you").wait_for()

        payloads = state["payloads"]
        assert_equal(len(payloads), 2)
        assert_equal(payloads[0]["clientRequestId"], payloads[1]["clientRequestId"])
        assert "email" not in payloads[0] and "subject" not in payloads[0]
        assert "email" not in payloads[1] and "subject" not in payloads[1]


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
    page.get_by_role("button", name="Submit Application").click()
    page.get_by_role("heading", name="Thank you").wait_for()

    payloads = state["payloads"]
    assert_equal(len(payloads), 2)
    assert payloads[0]["clientRequestId"] != payloads[1]["clientRequestId"]
    assert "email" not in payloads[0] and "subject" not in payloads[0]
    assert "email" not in payloads[1] and "subject" not in payloads[1]


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
    page.locator("main").screenshot(path=str(ARTIFACTS / "class-desktop.png"))

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
    assert request_headers and "cail_test_session=present" in request_headers[0].get("cookie", "")
    assert "email" not in payloads[0]
    assert "subject" not in payloads[0]

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
    assert not submit.is_disabled()
    assert "private detail" not in status.inner_text()

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
    assert not submit.is_disabled()

    submit.click()
    page.get_by_role("heading", name="Thank you").wait_for()
    assert_equal(attempts, 2)
    assert_equal(payloads[0]["clientRequestId"], payloads[1]["clientRequestId"])


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
    submit.click()
    page.get_by_role("heading", name="Thank you").wait_for()
    assert_equal(attempts, 2)
    assert payloads[0]["clientRequestId"] != payloads[1]["clientRequestId"]
    assert_equal(payloads[1]["department"], "English")


def test_mobile_layout_and_deep_link(page: Page) -> None:
    mock_identity(page)
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{BASE_URL}/request-access/?kind=class")
    wait_for_identity(page)
    assert class_choice(page).is_checked()
    dimensions = page.evaluate(
        "({ scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth })"
    )
    assert dimensions["scrollWidth"] <= dimensions["innerWidth"]


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
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
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
                test_mobile_layout_and_deep_link,
                test_public_access_links_use_the_canonical_application,
            ):
                context = browser.new_context(viewport={"width": 1440, "height": 1000})
                page = context.new_page()
                add_test_cookie(page)
                block_turnstile(page)
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
