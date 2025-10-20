#!/usr/bin/env python3
"""
Screenshot Capture Script for Meal Planner API Documentation

This script uses Playwright to automatically capture screenshots of the
Swagger UI API documentation interface.

Prerequisites:
    pip install playwright
    playwright install chromium

Usage:
    python docs/capture_screenshots.py
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright


async def capture_screenshots():
    """Capture screenshots of the API documentation."""

    # Define screenshot targets
    screenshots = [
        {
            "name": "01-swagger-overview.png",
            "url": "http://localhost:8000/docs",
            "description": "Full Swagger UI API Documentation Overview",
            "wait_for": ".swagger-ui",
        },
        {
            "name": "02-auth-endpoints.png",
            "url": "http://localhost:8000/docs",
            "description": "Authentication Endpoints",
            "wait_for": ".swagger-ui",
            "click_section": "Authentication",
        },
        {
            "name": "03-users-endpoints.png",
            "url": "http://localhost:8000/docs",
            "description": "User Management Endpoints",
            "wait_for": ".swagger-ui",
            "click_section": "Users",
        },
        {
            "name": "04-foods-endpoints.png",
            "url": "http://localhost:8000/docs",
            "description": "Food Search and Management Endpoints",
            "wait_for": ".swagger-ui",
            "click_section": "Foods",
        },
        {
            "name": "05-recipes-endpoints.png",
            "url": "http://localhost:8000/docs",
            "description": "Recipe Management Endpoints",
            "wait_for": ".swagger-ui",
            "click_section": "Recipes",
        },
        {
            "name": "06-meal-logs-endpoints.png",
            "url": "http://localhost:8000/docs",
            "description": "Meal Logging Endpoints",
            "wait_for": ".swagger-ui",
            "click_section": "Meal Logs",
        },
    ]

    # Create output directory
    output_dir = Path(__file__).parent / "screenshots"
    output_dir.mkdir(exist_ok=True)

    print(f"📸 Starting screenshot capture...")
    print(f"Output directory: {output_dir.absolute()}\n")

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,  # Retina display
        )
        page = await context.new_page()

        for idx, screenshot_config in enumerate(screenshots, 1):
            name = screenshot_config["name"]
            url = screenshot_config["url"]
            description = screenshot_config["description"]

            print(f"[{idx}/{len(screenshots)}] Capturing: {description}")
            print(f"    URL: {url}")

            try:
                # Navigate to the page
                await page.goto(url, wait_until="networkidle")

                # Wait for specific element to ensure page is loaded
                if "wait_for" in screenshot_config:
                    await page.wait_for_selector(screenshot_config["wait_for"], timeout=10000)

                # Click section to expand if specified
                if "click_section" in screenshot_config:
                    section_name = screenshot_config["click_section"]
                    try:
                        # Find and click the section header
                        section = page.get_by_text(section_name, exact=False).first
                        await section.click()
                        await page.wait_for_timeout(500)
                    except Exception as e:
                        print(f"    Warning: Could not click section '{section_name}': {e}")

                # Wait a bit for animations
                await page.wait_for_timeout(1000)

                # Take screenshot
                screenshot_path = output_dir / name
                await page.screenshot(path=str(screenshot_path), full_page=True)

                print(f"    ✓ Saved: {screenshot_path.name}\n")

            except Exception as e:
                print(f"    ✗ Error: {e}\n")
                continue

        await browser.close()

    print("✅ Screenshot capture complete!")
    print(f"\nScreenshots saved to: {output_dir.absolute()}")
    print(f"Total screenshots: {len(list(output_dir.glob('*.png')))}")


async def verify_server():
    """Verify that the API server is running."""
    import aiohttp

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    return True
    except Exception:
        return False

    return False


async def main():
    """Main entry point."""
    print("=" * 60)
    print("Meal Planner API - Screenshot Capture Tool")
    print("=" * 60)
    print()

    # Check if server is running
    print("🔍 Checking if API server is running...")
    server_running = await verify_server()

    if not server_running:
        print("❌ Error: API server is not running at http://localhost:8000")
        print("\nPlease start the server first:")
        print("  cd backend")
        print("  source venv/bin/activate")
        print("  uvicorn app.main:app --host 127.0.0.1 --port 8000")
        sys.exit(1)

    print("✓ API server is running\n")

    # Capture screenshots
    await capture_screenshots()


if __name__ == "__main__":
    asyncio.run(main())
