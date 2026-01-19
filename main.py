import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def make_pdf_debug(url: str, out_pdf: str):
    out_pdf = Path(out_pdf).resolve()
    out_dir = out_pdf.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    debug_png = out_dir / (out_pdf.stem + "_debug.png")
    debug_html = out_dir / (out_pdf.stem + "_debug.html")
    debug_log = out_dir / (out_pdf.stem + "_debug.log")

    log_lines = []

    def log(msg: str):
        log_lines.append(msg)

    ua = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            user_agent=ua,
            viewport={"width": 1366, "height": 768},
            locale="en-US",
        )
        page = context.new_page()

        page.on("console", lambda m: log(f"[console:{m.type}] {m.text}"))
        page.on("pageerror", lambda e: log(f"[pageerror] {e}"))
        page.on("requestfailed", lambda r: log(f"[requestfailed] {r.url} -> {r.failure}"))

        # 1) Sahifaga kirish
        try:
            resp = page.goto(url, wait_until="domcontentloaded", timeout=90000)
            if resp:
                log(f"[response] {resp.status} {resp.url}")
        except PlaywrightTimeoutError:
            log("[goto] TIMEOUT on domcontentloaded")

        # 2) Qo‘shimcha kutish: ko‘p saytlar keyinroq chizadi
        try:
            page.wait_for_load_state("networkidle", timeout=90000)
        except PlaywrightTimeoutError:
            log("[load_state] TIMEOUT on networkidle")

        # 3) Lazy-load bo‘lsa, biroz scroll
        try:
            for _ in range(6):
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(700)
        except Exception as e:
            log(f"[scroll] {e}")

        # 4) SCREEN ko‘rinishida screenshot (render bormi yo‘qmi tekshiramiz)
        page.emulate_media(media="screen")
        page.wait_for_timeout(1000)
        page.screenshot(path=str(debug_png), full_page=True)

        # 5) HTML dump
        try:
            html = page.content()
            debug_html.write_text(html, encoding="utf-8")
            log(f"[html] saved {debug_html.name} ({len(html)} chars)")
        except Exception as e:
            log(f"[html] failed: {e}")

        # 6) Print CSS hammasini yashirayotgan bo‘lsa, override qilib ko‘ramiz
        page.add_style_tag(content="""
            @media print {
              html, body { display: block !important; visibility: visible !important; }
              * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
            }
        """)

        # 7) PDF
        page.emulate_media(media="screen")  # print emas, aynan screen CSS
        page.pdf(
            path=str(out_pdf),
            format="A4",
            print_background=True,
            margin={"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"},
            scale=1.0,
            prefer_css_page_size=True,
        )

        context.close()
        browser.close()

    debug_log.write_text("\n".join(log_lines), encoding="utf-8")
    print("PDF:", out_pdf)
    print("SCREENSHOT:", debug_png)
    print("HTML:", debug_html)
    print("LOG:", debug_log)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("-o", "--out", default="page.pdf")
    args = ap.parse_args()
    make_pdf_debug(args.url, args.out)


# python main.py "link" -o result.pdf
