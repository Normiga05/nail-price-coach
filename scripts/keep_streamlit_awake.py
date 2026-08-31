"""Visita la app de Streamlit Community Cloud con un navegador real y, si
salió la pantalla de "esta app se durmió", hace clic en el botón de
despertarla.

Un simple curl/GET no sirve: Streamlit Cloud responde HTTP 200 igual
aunque la app esté dormida (te da la pantalla de "wake up"), así que un
ping normal nunca la mantiene despierta de verdad.
"""

import sys

from playwright.sync_api import sync_playwright

APP_URL = "https://nail-price-coach-norja.streamlit.app/"
WAKE_BUTTON_TEXT = "Yes, get this app back up!"


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(APP_URL, wait_until="networkidle", timeout=60_000)

        wake_button = page.get_by_role("button", name=WAKE_BUTTON_TEXT)
        try:
            wake_button.wait_for(state="visible", timeout=10_000)
            print("La app estaba dormida, haciendo clic para despertarla...")
            wake_button.click()
            page.wait_for_timeout(15_000)
            print("Clic hecho. La app debería estar despertando.")
        except Exception:
            print("La app ya estaba despierta (no apareció el botón de wake up).")

        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
