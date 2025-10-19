"""Capture a screenshot of a generated HTML report using Playwright.

This is optional — Playwright is not required by the project. To use:

  pip install playwright
  playwright install

Then run:

  python tools/screenshot_report.py /absolute/path/to/report.html /path/to/out.png

On Windows you may need to provide a full file:// URL (the script will handle it).
"""
import sys
from pathlib import Path

def screenshot_report(html_path: str, out_path: str, wait_ms: int = 800):
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        print('Playwright not installed. Install with: pip install playwright && playwright install')
        raise

    html = Path(html_path).resolve()
    if not html.exists():
        raise SystemExit(f'File not found: {html}')

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        file_url = f'file:///{html.as_posix()}' if sys.platform.startswith('win') else f'file://{html.as_posix()}'
        page.goto(file_url)
        # small wait for client-side DataTables to initialize
        page.wait_for_timeout(wait_ms)
        page.screenshot(path=str(out), full_page=True)
        browser.close()


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) < 2:
        print('Usage: python tools/screenshot_report.py /path/to/report.html /path/to/out.png')
        raise SystemExit(2)
    screenshot_report(argv[0], argv[1])


if __name__ == '__main__':
    main()
