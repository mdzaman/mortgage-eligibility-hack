"""
Test the mortgage engine UI using Playwright - Enhanced version
Tests preset loading and JSON parsing fixes
"""
from playwright.sync_api import sync_playwright
import time

def test_ui():
    console_messages = []
    errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Capture console messages
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        # Navigate to the page
        print("🌐 Navigating to http://localhost:3000")
        page.goto("http://localhost:3000", wait_until="networkidle")

        # Take initial screenshot
        page.screenshot(path="/home/coder/screenshot_initial.png", full_page=True)
        print("✓ Initial screenshot saved: screenshot_initial.png")

        # Get page title
        title = page.title()
        print(f"✓ Page title: {title}")

        # Wait for presets to load
        print("\n⏳ Waiting for presets to load...")
        time.sleep(2)

        # Check preset button state
        button = page.locator("#loadPresetButton")
        button_text = button.inner_text()
        is_disabled = button.is_disabled()

        print(f"📊 Preset button text: '{button_text}'")
        print(f"📊 Preset button disabled: {is_disabled}")

        if "Loading" in button_text or is_disabled:
            print("⏳ Presets still loading, waiting 3 more seconds...")
            time.sleep(3)
            button_text = button.inner_text()
            is_disabled = button.is_disabled()
            print(f"📊 Updated button text: '{button_text}'")
            print(f"📊 Updated button disabled: {is_disabled}")

        # Select Prime Conforming preset
        print("\n✅ Selecting Prime Conforming preset...")
        prime_radio = page.locator('input[name="preset"][value="prime_conforming"]')
        prime_radio.check()
        print("✓ Radio button selected")

        # Take screenshot after selection
        page.screenshot(path="/home/coder/screenshot_preset_selected.png", full_page=True)
        print("✓ Preset selection screenshot saved: screenshot_preset_selected.png")

        # Click the load preset button
        print("\n🚀 Clicking 'Load Selected Preset & Evaluate' button...")
        button.click()

        # Wait for evaluation to complete
        print("⏳ Waiting for evaluation (5 seconds)...")
        time.sleep(5)

        # Check if results are displayed
        results_div = page.locator("#results")
        is_visible = results_div.is_visible()
        print(f"\n📊 Results div visible: {is_visible}")

        # Take screenshot of results
        page.screenshot(path="/home/coder/screenshot_results.png", full_page=True)
        print("✓ Results screenshot saved: screenshot_results.png")

        if is_visible:
            # Get the result status
            status_divs = page.locator(".result-status")
            if status_divs.count() > 0:
                status_text = status_divs.first.inner_text()
                print(f"✅ Result status: {status_text}")

                # Get metrics
                metric_cards = page.locator(".metric-card")
                print(f"✅ Found {metric_cards.count()} metric cards")

                for i in range(min(3, metric_cards.count())):
                    label = metric_cards.nth(i).locator('.label').inner_text()
                    value = metric_cards.nth(i).locator('.value').inner_text()
                    print(f"  - {label}: {value}")
            else:
                print("⚠️ No result status found")
        else:
            print("⚠️ Results not visible")
            # Check for error messages
            empty_state = page.locator("#emptyState")
            if empty_state.is_visible():
                print("ℹ️ Empty state is showing")

        # Print any console messages
        print("\n📝 Console Messages:")
        for msg in console_messages[-10:]:  # Last 10 messages
            print(f"  {msg}")

        # Print any errors
        if errors:
            print("\n❌ JavaScript Errors:")
            for error in errors:
                print(f"  {error}")

        # Test manual test button
        print("\n🔬 Testing manual test button...")
        manual_test_button = page.locator('button:has-text("Run Manual Test")')
        if manual_test_button.count() > 0:
            manual_test_button.click()
            time.sleep(5)
            page.screenshot(path="/home/coder/screenshot_manual_test.png", full_page=True)
            print("✓ Manual test screenshot saved: screenshot_manual_test.png")

            # Check results again
            if results_div.is_visible():
                print("✅ Manual test results displayed")
        else:
            print("⚠️ Manual test button not found")

        browser.close()
        print("\n✅ UI test completed!")

if __name__ == "__main__":
    test_ui()
