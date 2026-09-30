"""
Visual / interactive UI tests.

These tests launch real UI components for visual inspection. They require
a display and user interaction — do NOT run these in CI.

Run with:
  python run_tests.py ui            all UI tests
  python run_tests.py ui selector   only location-selector tests

Each test prints a one-line instruction before launching the dialog.
Tests that ask you to click a specific button will FAIL if you click the wrong one —
this validates that dialogs respond correctly to user input.
"""
import pytest

pytestmark = pytest.mark.ui


# ── ask_yes_no ─────────────────────────────────────────────────────────────────

def test_ask_yes_no_click_yes():
    """Click YES → test passes.  Click No or close → test fails."""
    from ui.ctk_utils import ask_yes_no
    print("\n→ Click YES")
    result = ask_yes_no(
        "UI Test — Yes/No",
        "Click YES to pass this test.\nClick No or close the window to fail.",
    )
    assert result is True, "Expected Yes click"


def test_ask_yes_no_click_no():
    """Click NO → test passes.  Click Yes or close → test fails."""
    from ui.ctk_utils import ask_yes_no
    print("\n→ Click NO")
    result = ask_yes_no(
        "UI Test — Yes/No",
        "Click NO to pass this test.\nClick Yes or close the window to fail.",
    )
    assert result is False, "Expected No click"


# ── show_info ──────────────────────────────────────────────────────────────────

def test_show_info_smoke():
    """Smoke test — info dialog should open and close without error."""
    from ui.ctk_utils import show_info
    print("\n→ Dismiss the info dialog (click OK or close it)")
    show_info("UI Test — Info Dialog", "This is an info dialog.\nClick OK to continue.")


# ── location_selector ──────────────────────────────────────────────────────────

def test_location_selector_no_suggestion():
    """Basic picker with no suggestion — no option is pre-highlighted."""
    from ui.location_selector import select_location
    print("\n→ Pick any option or click Skip — just checking the layout looks right")
    result = select_location(
        [("Documents", r"C:\Users\test\Documents"), ("Downloads", r"C:\Users\test\Downloads")],
        title="UI Test — Basic location picker\nNo option is suggested — pick anything or Skip",
        allow_browse=False,
    )
    print(f"   Selected: {result!r}")


def test_location_selector_with_suggestion():
    """
    The top option should be highlighted in blue with a ↵ hint.
    Pressing Enter should select it without clicking.
    """
    from ui.location_selector import select_location
    print("\n→ The TOP option should be highlighted blue with ↵")
    print("  Press Enter (or click the top option) to confirm")
    result = select_location(
        [
            ("Physio Receipts", r"C:\Users\test\Physio\Receipts"),
            ("Documents",       r"C:\Users\test\Documents"),
            ("Downloads",       r"C:\Users\test\Downloads"),
        ],
        title="UI Test — Suggested option\nPhysio Receipts should be highlighted at the top",
        suggestion=r"C:\Users\test\Physio\Receipts",
        allow_browse=True,
    )
    print(f"   Selected: {result!r}")


def test_location_selector_many_options():
    """Picker with several options — verify layout doesn't break."""
    from ui.location_selector import select_location
    print("\n→ Check all options are visible — Skip when done")
    select_location(
        [
            ("Physio Receipts",    r"C:\test\Physio"),
            ("Dental Receipts",    r"C:\test\Dental"),
            ("GP Receipts",        r"C:\test\GP"),
            ("Documents",          r"C:\test\Documents"),
            ("Downloads",          r"C:\test\Downloads"),
        ],
        title="UI Test — Many options\nVerify all five options are visible",
        allow_browse=True,
    )


def test_location_selector_browse_saves_new_location(tmp_path, monkeypatch):
    """
    Click Browse, pick a folder → the save dialog should appear.
    Enter a name and click Save → verify save_location was called with correct args.
    """
    from ui.location_selector import select_location
    import unittest.mock as mock

    saved: list = []
    with mock.patch("utils.location_manager.save_location",
                    side_effect=lambda name, path, lst: saved.append((name, path, lst))):
        print("\n→ Click Browse, pick ANY folder, enter a name, click Save")
        result = select_location(
            [("Documents", r"C:\test\Documents")],
            title="UI Test — Browse + Save dialog\nClick Browse → pick a folder → save it",
            allow_browse=True,
            save_to_list="DEFAULT_LOCATION_KEYS",
        )

    print(f"   Selected: {result!r}")
    if saved:
        print(f"   save_location called with: {saved[0]}")
        name, path, lst = saved[0]
        assert isinstance(name, str) and len(name) > 0, "Name should be non-empty"
        assert lst == "DEFAULT_LOCATION_KEYS", "Should save to DEFAULT_LOCATION_KEYS"
    else:
        print("   (save dialog was skipped or 'Not now' was clicked — that's fine)")


def test_location_selector_browse_skip_save(monkeypatch):
    """
    Click Browse, pick a folder, then click 'Not now' in the save dialog.
    File should still be selected but save_location must NOT be called.
    """
    from ui.location_selector import select_location
    import unittest.mock as mock

    saved: list = []
    with mock.patch("utils.location_manager.save_location",
                    side_effect=lambda *a: saved.append(a)):
        print("\n→ Click Browse, pick a folder, then click NOT NOW in the save dialog")
        result = select_location(
            [("Documents", r"C:\test\Documents")],
            title="UI Test — Browse without saving\nBrowse → pick folder → click NOT NOW",
            allow_browse=True,
            save_to_list="DEFAULT_LOCATION_KEYS",
        )

    print(f"   Selected: {result!r}")
    assert saved == [], "save_location should NOT have been called"
