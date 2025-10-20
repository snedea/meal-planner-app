# Screenshot Automation Guide

This guide explains how to automatically capture screenshots of the Meal Planner API documentation using the provided Playwright-based automation script.

## Overview

The screenshot capture tool uses [Playwright](https://playwright.dev/) to automate browser interactions and capture high-quality screenshots of the Swagger UI documentation interface. This ensures consistent, up-to-date visual documentation of the API.

## Prerequisites

### 1. Install Playwright

```bash
# Install Playwright and dependencies
pip install playwright aiohttp

# Install Chromium browser
playwright install chromium
```

### 2. Start the Backend Server

The API server must be running before capturing screenshots:

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Verify the server is running by visiting: http://localhost:8000/docs

## Usage

### Basic Usage

From the project root directory:

```bash
python3 docs/capture_screenshots.py
```

The script will:
1. Verify the API server is running
2. Launch a headless Chromium browser
3. Navigate to the Swagger UI
4. Capture screenshots of each API section
5. Save high-resolution images to `docs/screenshots/`

### Expected Output

```
============================================================
Meal Planner API - Screenshot Capture Tool
============================================================

🔍 Checking if API server is running...
✓ API server is running

📸 Starting screenshot capture...
Output directory: /Users/name/homelab/meal-planner-app/docs/screenshots

[1/6] Capturing: Full Swagger UI API Documentation Overview
    URL: http://localhost:8000/docs
    ✓ Saved: 01-swagger-overview.png

[2/6] Capturing: Authentication Endpoints
    URL: http://localhost:8000/docs
    ✓ Saved: 02-auth-endpoints.png

...

✅ Screenshot capture complete!
Screenshots saved to: /Users/name/homelab/meal-planner-app/docs/screenshots
Total screenshots: 6
```

## Screenshots Captured

The tool captures the following screenshots:

| Filename | Description | URL |
|----------|-------------|-----|
| `01-swagger-overview.png` | Full API documentation overview | http://localhost:8000/docs |
| `02-auth-endpoints.png` | Authentication endpoints | http://localhost:8000/docs |
| `03-users-endpoints.png` | User management endpoints | http://localhost:8000/docs |
| `04-foods-endpoints.png` | Food search and management | http://localhost:8000/docs |
| `05-recipes-endpoints.png` | Recipe management | http://localhost:8000/docs |
| `06-meal-logs-endpoints.png` | Meal logging endpoints | http://localhost:8000/docs |

## Configuration

### Screenshot Settings

The script uses the following settings for optimal quality:

- **Viewport**: 1920x1080 (Full HD)
- **Device Scale Factor**: 2x (Retina display quality)
- **Format**: PNG (lossless compression)
- **Mode**: Full page screenshots

### Customizing Screenshots

To add or modify screenshots, edit the `screenshots` list in `capture_screenshots.py`:

```python
screenshots = [
    {
        "name": "01-swagger-overview.png",
        "url": "http://localhost:8000/docs",
        "description": "Full Swagger UI API Documentation Overview",
        "wait_for": ".swagger-ui",
    },
    # Add more screenshots here...
]
```

Available options:
- `name`: Output filename
- `url`: URL to navigate to
- `description`: Human-readable description
- `wait_for`: CSS selector to wait for before capturing
- `click_section`: (Optional) Section name to click/expand

## Troubleshooting

### Server Not Running

**Error**: `❌ Error: API server is not running at http://localhost:8000`

**Solution**: Start the backend server:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Playwright Not Installed

**Error**: `ModuleNotFoundError: No module named 'playwright'`

**Solution**: Install Playwright and browsers:
```bash
pip install playwright
playwright install chromium
```

### Port Conflict

**Error**: Server won't start due to port 8000 being in use

**Solution**: Find and kill the process using port 8000:
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database Connection Issues

**Error**: Server fails to start due to database connection

**Solution**: Ensure Docker containers are running:
```bash
docker-compose up -d
docker-compose ps  # Verify services are healthy
```

## Advanced Usage

### Headful Mode (Visible Browser)

To see the browser while capturing screenshots, modify the script:

```python
# In capture_screenshots.py
browser = await p.chromium.launch(headless=False)  # Changed from True to False
```

### Custom Viewport Size

To change screenshot dimensions:

```python
context = await browser.new_context(
    viewport={"width": 2560, "height": 1440},  # 2K resolution
    device_scale_factor=2,
)
```

### Adding Wait Time

To add delays for slow-loading content:

```python
await page.wait_for_timeout(2000)  # Wait 2 seconds
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Update Documentation Screenshots

on:
  push:
    branches: [main]
    paths:
      - 'backend/app/api/**'

jobs:
  screenshots:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install playwright aiohttp
          playwright install chromium --with-deps

      - name: Start services
        run: |
          docker-compose up -d
          cd backend
          pip install -r requirements.txt
          uvicorn app.main:app --host 127.0.0.1 --port 8000 &
          sleep 10

      - name: Capture screenshots
        run: python3 docs/capture_screenshots.py

      - name: Commit screenshots
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add docs/screenshots/
          git commit -m "Update API documentation screenshots" || echo "No changes"
          git push
```

## Best Practices

1. **Update After API Changes**: Re-capture screenshots whenever API endpoints change
2. **Version Control**: Commit screenshots to Git for historical tracking
3. **Compress Images**: Consider using tools like `pngquant` for smaller file sizes
4. **Consistent Timing**: Always capture at the same time (e.g., after successful tests)
5. **Full Page vs Viewport**: Use full page screenshots for comprehensive documentation

## Alternative Tools

If Playwright doesn't meet your needs, consider these alternatives:

- **Selenium**: More mature, wider browser support
- **Puppeteer**: Chrome-specific, similar to Playwright
- **Cypress**: Great for E2E testing with screenshot capabilities
- **Manual**: Browser DevTools (F12) → Screenshot full page

## Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [Swagger UI Documentation](https://swagger.io/tools/swagger-ui/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Playwright logs for detailed error messages
3. Verify the API server is running and accessible
4. Ensure all dependencies are installed correctly

---

**Last Updated**: October 19, 2025
**Script Location**: `/docs/capture_screenshots.py`
**Output Directory**: `/docs/screenshots/`
