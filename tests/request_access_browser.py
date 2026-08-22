"""Browser contract tests for the two request-access intake routes.

Individual applications retain the legacy body at `/request-access/api`.
Class applications use their class-only body at `/request-access/class-api`.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, Route, sync_playwright


BASE_URL = os.environ.get("CAIL_TEST_BASE", "http://127.0.0.1:4321")
INDIVIDUAL_INTAKE_URL = "https://tools.ailab.gc.cuny.edu/request-access/api"
CLASS_INTAKE_URL = "https://tools.ailab.gc.cuny.edu/request-access/class-api"
ARTIFACTS = Path(os.environ.get("CAIL_TEST_ARTIFACTS", "/tmp/cail-request-access-browser"))


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


def fill_common(page: Page, affiliation: str = "faculty") -> dict[str, str]:
    values = {
        "name": "Professor Ada Lovelace",
        "email": "ada.lovelace@cuny.edu",
        "affiliation": affiliation,
        "department": "Digital Humanities",
        "campus": "Graduate Center",
        "intendedUse": "Coursework using Lab tools.",
    }
    page.get_by_label("Full Name").fill(values["name"])
    page.get_by_label("Email Address").fill(values["email"])
    page.get_by_label("CUNY Affiliation").select_option(values["affiliation"])
    page.get_by_label("Department/Program").fill(values["department"])
    page.get_by_label("CUNY College/Campus").fill(values["campus"])
    page.get_by_label("Intended Use or Support Request").fill(values["intendedUse"])
    return values


def capture_success(page: Page, request_id: str, intake_url: str) -> tuple[list[dict[str, Any]], list[str]]:
    payloads: list[dict[str, Any]] = []
    unexpected_urls: list[str] = []

    def respond(route: Route) -> None:
        payloads.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(
            status=201,
            content_type="application/json",
            headers={"access-control-allow-origin": "*"},
            body=json.dumps({"requestId": request_id}),
        )

    def reject_unexpected(route: Route) -> None:
        unexpected_urls.append(route.request.url)
        route.fulfill(
            status=500,
            content_type="application/json",
            headers={"access-control-allow-origin": "*"},
            body=json.dumps({"error": {"code": "wrong_intake_endpoint"}}),
        )

    other_url = CLASS_INTAKE_URL if intake_url == INDIVIDUAL_INTAKE_URL else INDIVIDUAL_INTAKE_URL
    page.route(intake_url, respond)
    page.route(other_url, reject_unexpected)
    return payloads, unexpected_urls


def individual_choice(page: Page):
    return page.get_by_role("radio", name=re.compile(r"^Individual\b"))


def class_choice(page: Page):
    return page.get_by_role("radio", name=re.compile(r"^Class\b"))


def assert_request_id(value: Any) -> None:
    assert isinstance(value, str)
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
        value,
    )


def test_individual_mode(page: Page) -> None:
    page.goto(f"{BASE_URL}/request-access/")
    form = page.locator("#access-request-form")
    assert_equal(form.get_attribute("action"), INDIVIDUAL_INTAKE_URL)
    assert_equal(form.get_attribute("data-intake-url"), INDIVIDUAL_INTAKE_URL)
    assert_equal(form.get_attribute("data-class-intake-url"), CLASS_INTAKE_URL)
    assert individual_choice(page).is_checked()
    assert page.locator("#individual-fields").is_visible()
    assert page.locator("#class-fields").is_hidden()
    assert page.locator("#class-fields").evaluate("fieldset => fieldset.disabled")

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

    add_turnstile_token(page)
    payloads, unexpected_urls = capture_success(page, "req-individual", INDIVIDUAL_INTAKE_URL)
    page.get_by_role("button", name="Submit Application").click()
    page.get_by_text("Application received. Reference: req-individual").wait_for()
    assert_equal(len(payloads), 1)
    assert_equal(unexpected_urls, [])

    payload = payloads[0]
    assert_equal(
        set(payload),
        {
            "clientRequestId",
            "turnstileToken",
            "name",
            "email",
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
    assert individual_choice(page).is_checked()
    assert_equal(page.get_by_role("button", name="Submit Application").text_content(), "Submit Application")


def test_class_mode(page: Page) -> None:
    page.goto(f"{BASE_URL}/request-access/?kind=class")
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

    common = fill_common(page, affiliation="staff")
    add_turnstile_token(page)
    payloads, unexpected_urls = capture_success(page, "req-class", CLASS_INTAKE_URL)

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
    page.get_by_text("Application received. Reference: req-class").wait_for()
    assert_equal(len(payloads), 1)
    assert_equal(unexpected_urls, [])

    payload = payloads[0]
    assert_equal(
        set(payload),
        {
            "clientRequestId",
            "turnstileToken",
            "name",
            "email",
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


def test_keyboard_copy_and_safe_error(page: Page) -> None:
    page.goto(f"{BASE_URL}/request-access/")
    individual = individual_choice(page)
    individual.focus()
    individual.press("ArrowRight")
    assert class_choice(page).is_checked()
    assert "kind=class" in page.url
    class_choice(page).press("ArrowLeft")
    assert individual.is_checked()
    assert "kind=individual" in page.url

    body = page.locator("body").inner_text().lower()
    assert "admin desk" not in body
    assert "receive an email" not in body
    assert "email notification" not in body
    assert "faculty manage" not in body
    assert_equal(page.locator('a[href*="/admin/admission"]').count(), 0)
    assert page.get_by_text("The Lab reviews the application and decides whether to approve the class.").is_visible()
    assert page.get_by_text("After class approval, coordinators use CUNY Login; students use the class invitation.").is_visible()
    assert "faculty automatically" not in body
    assert "automatically granted" not in body

    common = fill_common(page)
    add_turnstile_token(page)

    def fail(route: Route) -> None:
        route.fulfill(
            status=500,
            content_type="application/json",
            headers={"access-control-allow-origin": "*"},
            body=json.dumps({"error": {"code": "private_stack_trace", "message": "secret detail"}}),
        )

    page.route(INDIVIDUAL_INTAKE_URL, fail)
    page.get_by_role("button", name="Submit Application").click()
    status = page.locator("#form-status")
    status.get_by_text("The access service is temporarily unavailable. Try again shortly.").wait_for()
    assert "secret detail" not in status.inner_text()
    assert_equal(common["affiliation"], "faculty")


def test_backend_error_and_retry(page: Page) -> None:
    page.goto(f"{BASE_URL}/request-access/")
    fill_common(page)
    add_turnstile_token(page)
    attempts = 0

    def fail_once_then_succeed(route: Route) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            route.fulfill(
                status=503,
                content_type="application/json",
                headers={"access-control-allow-origin": "*"},
                body=json.dumps({"error": {"code": "admission_unavailable", "message": "private detail"}}),
            )
            return
        route.fulfill(
            status=201,
            content_type="application/json",
            headers={"access-control-allow-origin": "*"},
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
    page.get_by_text("Application received. Reference: req-retry").wait_for()
    assert_equal(attempts, 2)


def test_ambiguous_retry_reuses_client_request_id(page: Page) -> None:
    page.goto(f"{BASE_URL}/request-access/")
    fill_common(page)
    add_turnstile_token(page)
    payloads: list[dict[str, Any]] = []
    attempts = 0

    def lose_first_response(route: Route) -> None:
        nonlocal attempts
        attempts += 1
        payloads.append(json.loads(route.request.post_data or "{}"))
        if attempts == 1:
            route.abort("failed")
            return
        route.fulfill(
            status=201,
            content_type="application/json",
            headers={"access-control-allow-origin": "*"},
            body=json.dumps({"requestId": "req-ambiguous"}),
        )

    page.route(INDIVIDUAL_INTAKE_URL, lose_first_response)
    submit = page.get_by_role("button", name="Submit Application")
    submit.click()
    page.get_by_text("The access service could not be reached. Check your connection and try again.").wait_for()
    assert not submit.is_disabled()

    submit.click()
    page.get_by_text("Application received. Reference: req-ambiguous").wait_for()
    assert_equal(attempts, 2)
    assert_equal(payloads[0]["clientRequestId"], payloads[1]["clientRequestId"])


def test_changed_payload_gets_new_client_request_id(page: Page) -> None:
    page.goto(f"{BASE_URL}/request-access/")
    fill_common(page)
    add_turnstile_token(page)
    payloads: list[dict[str, Any]] = []
    attempts = 0

    def fail_then_succeed(route: Route) -> None:
        nonlocal attempts
        attempts += 1
        payloads.append(json.loads(route.request.post_data or "{}"))
        if attempts == 1:
            route.fulfill(
                status=503,
                content_type="application/json",
                headers={"access-control-allow-origin": "*"},
                body=json.dumps({"error": {"code": "admission_unavailable"}}),
            )
            return
        route.fulfill(
            status=201,
            content_type="application/json",
            headers={"access-control-allow-origin": "*"},
            body=json.dumps({"requestId": "req-changed"}),
        )

    page.route(INDIVIDUAL_INTAKE_URL, fail_then_succeed)
    submit = page.get_by_role("button", name="Submit Application")
    submit.click()
    page.get_by_text("The access service is temporarily unavailable. Try again shortly.").wait_for()
    page.get_by_label("Department/Program").fill("English")
    submit.click()
    page.get_by_text("Application received. Reference: req-changed").wait_for()
    assert_equal(attempts, 2)
    assert payloads[0]["clientRequestId"] != payloads[1]["clientRequestId"]
    assert_equal(payloads[1]["department"], "English")


def test_mobile_layout_and_deep_link(page: Page) -> None:
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(f"{BASE_URL}/request-access/?kind=class")
    assert class_choice(page).is_checked()
    assert page.get_by_text("Request class access for a course; the course coordinator submits details for Lab review before students are invited.").is_visible()
    assert page.get_by_text("Submitting this form does not grant Lab membership. Course coordinators can apply whether or not they already have Lab access.").is_visible()
    dimensions = page.evaluate(
        "({ scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth })"
    )
    assert dimensions["scrollWidth"] <= dimensions["innerWidth"]

    individual_box = individual_choice(page).locator("xpath=..").bounding_box()
    class_box = class_choice(page).locator("xpath=..").bounding_box()
    assert individual_box is not None and class_box is not None
    assert class_box["y"] > individual_box["y"] + individual_box["height"] - 1
    page.screenshot(path=str(ARTIFACTS / "class-mobile.png"), full_page=True)


def main() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for test in (
                test_individual_mode,
                test_class_mode,
                test_keyboard_copy_and_safe_error,
                test_backend_error_and_retry,
                test_ambiguous_retry_reuses_client_request_id,
                test_changed_payload_gets_new_client_request_id,
                test_mobile_layout_and_deep_link,
            ):
                context = browser.new_context(viewport={"width": 1440, "height": 1000})
                page = context.new_page()
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
