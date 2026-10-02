import os
import time
from playwright.sync_api import sync_playwright

DASHBOARD_HTML = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "index.html"))
OUTPUT_SCREENSHOT = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "dashboard_screenshot.png"))

def capture_screenshot():
    os.makedirs(os.path.dirname(OUTPUT_SCREENSHOT), exist_ok=True)
    print(f"[INFO] Rendering Dashboard from: file://{DASHBOARD_HTML}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        
        # Load local HTML dashboard
        page.goto(f"file://{DASHBOARD_HTML}")
        
        # Wait for Chart.js animation to complete
        time.sleep(2.5)
        
        # Capture screenshot
        page.screenshot(path=OUTPUT_SCREENSHOT, full_page=True)
        browser.close()
        
    print(f"[SUCCESS] High-resolution dashboard screenshot saved to: {OUTPUT_SCREENSHOT}")

if __name__ == "__main__":
    capture_screenshot()
