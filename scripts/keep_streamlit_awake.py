"""Visita la app de Streamlit Community Cloud con un navegador real y, si
salió la pantalla de "esta app se durmió", hace clic en el botón de
despertarla.

Un simple curl/GET no sirve: Streamlit Cloud responde HTTP 200 igual
aunque la app esté dormida (te da la pantalla de "wake up"), así que un
ping normal nunca la mantiene despierta de verdad.

Además de clicar el botón, el script confirma que la app real (su
título) terminó de cargar. Si no aparece ni el botón de "despertar" ni
el título de la app, algo distinto está pasando (un error, un timeout,
un cambio en la pantalla de Streamlit) y el script falla en vez de
reportar éxito a ciegas, guardando una captura de pantalla para poder
diagnosticarlo.
"""

import sys

from playwright.sync_api import sync_playwright

APP_URL = "https://nail-price-coach-norja.streamlit.app/"
WAKE_BUTTON_TEXT = "Yes, get this app back up!"
APP_TITLE_TEXT = "Nail Price Coach"
SCREENSHOT_PATH = "keep_alive_failure.png"


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
        except Exception:
            print("No apareció el botón de wake up (puede que ya estuviera despierta).")

        app_title = page.get_by_text(APP_TITLE_TEXT)
        try:
            app_title.wait_for(state="visible", timeout=30_000)
            print("Confirmado: la app está arriba y mostrando su contenido real.")
            browser.close()
            return 0
        except Exception:
            print(
                "No se pudo confirmar que la app cargó su contenido real "
                "(ni título ni botón de wake up visibles). Guardando captura "
                "de pantalla para diagnosticar."
            )
            page.screenshot(path=SCREENSHOT_PATH)
            print(f"Título de la pestaña: {page.title()!r}")
            print(f"Texto visible (primeros 500 caracteres): {page.inner_text('body')[:500]!r}")
            browser.close()
            return 1


if __name__ == "__main__":
    sys.exit(main())
