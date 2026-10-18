"""Visita la app de Streamlit Community Cloud con un navegador real y, si
salió la pantalla de "esta app se durmió", hace clic en el botón de
despertarla.

Un simple curl/GET no sirve: Streamlit Cloud responde HTTP 200 igual
aunque la app esté dormida (te da la pantalla de "wake up"), así que un
ping normal nunca la mantiene despierta de verdad.

Streamlit Cloud renderiza la app real dentro de un <iframe> (el host
externo solo pone el marco, el badge y el botón de "wake up" alrededor).
Por eso hay que buscar tanto el botón de despertar como el contenido
real de la app dentro de ese iframe, no en el documento principal.
"""

import sys
import time

from playwright.sync_api import sync_playwright

APP_URL = "https://nail-price-coach-norja.streamlit.app/"
WAKE_BUTTON_TEXT = "Yes, get this app back up!"
APP_TITLE_TEXT = "Nail Price Coach"
APP_IFRAME_SELECTOR = "iframe[title='streamlitApp']"
SCREENSHOT_PATH = "keep_alive_failure.png"
MAX_WAIT_SECONDS = 60
POLL_INTERVAL_SECONDS = 3


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(APP_URL, wait_until="load", timeout=60_000)

        # El botón de "wake up" puede estar en la página principal (app
        # totalmente dormida) o dentro del iframe (app arrancando). Se
        # buscan ambos.
        top_wake_button = page.get_by_role("button", name=WAKE_BUTTON_TEXT)
        app_frame = page.frame_locator(APP_IFRAME_SELECTOR)
        frame_wake_button = app_frame.get_by_role("button", name=WAKE_BUTTON_TEXT)
        app_title = app_frame.get_by_text(APP_TITLE_TEXT)
        clicked_wake_button = False

        deadline = time.monotonic() + MAX_WAIT_SECONDS
        while time.monotonic() < deadline:
            if app_title.count() > 0 and app_title.first.is_visible():
                print("Confirmado: la app está arriba y mostrando su contenido real.")
                browser.close()
                return 0

            if not clicked_wake_button:
                for button in (top_wake_button, frame_wake_button):
                    if button.count() > 0 and button.first.is_visible():
                        print("La app estaba dormida, haciendo clic para despertarla...")
                        button.first.click()
                        clicked_wake_button = True
                        break

            time.sleep(POLL_INTERVAL_SECONDS)

        print(
            f"Pasaron {MAX_WAIT_SECONDS}s y no se pudo confirmar que la app cargó su "
            "contenido real dentro del iframe. Guardando diagnóstico."
        )
        page.screenshot(path=SCREENSHOT_PATH)
        print(f"¿Se hizo clic en el botón de despertar?: {clicked_wake_button}")
        print(f"Título de la pestaña: {page.title()!r}")
        try:
            frame_body_text = app_frame.locator("body").inner_text()[:500]
        except Exception as exc:
            frame_body_text = f"(no se pudo leer el body del iframe: {exc})"
        print(f"Texto visible dentro del iframe de la app: {frame_body_text!r}")
        browser.close()
        return 1


if __name__ == "__main__":
    sys.exit(main())
