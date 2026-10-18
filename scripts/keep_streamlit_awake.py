"""Visita la app de Streamlit Community Cloud con un navegador real y, si
salió la pantalla de "esta app se durmió", hace clic en el botón de
despertarla.

Un simple curl/GET no sirve: Streamlit Cloud responde HTTP 200 igual
aunque la app esté dormida (te da la pantalla de "wake up"), así que un
ping normal nunca la mantiene despierta de verdad.

Cuando la app estaba realmente dormida, levantarla de nuevo (reinstalar
dependencias, arrancar el contenedor) puede tardar más que unos segundos,
así que el script reintenta durante un par de minutos en vez de rendirse
rápido. Si después de todo ese tiempo no aparece ni el botón de
"despertar" ni el contenido real de la app, vuelca errores de consola,
errores de página y el HTML real del <body> (no del <head>, que ya ocupa
de sobra cualquier límite corto de caracteres) para poder diagnosticar
qué pantalla está mostrando en realidad.
"""

import sys
import time

from playwright.sync_api import sync_playwright

APP_URL = "https://nail-price-coach-norja.streamlit.app/"
WAKE_BUTTON_TEXT = "Yes, get this app back up!"
APP_TITLE_TEXT = "Nail Price Coach"
SCREENSHOT_PATH = "keep_alive_failure.png"
MAX_WAIT_SECONDS = 150
POLL_INTERVAL_SECONDS = 5
PROGRESS_LOG_EVERY_SECONDS = 30


def main() -> int:
    console_messages = []
    page_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))

        response = page.goto(APP_URL, wait_until="load", timeout=60_000)
        print(f"Respuesta de navegación: status={response.status if response else None}")

        wake_button = page.get_by_role("button", name=WAKE_BUTTON_TEXT)
        app_title = page.get_by_text(APP_TITLE_TEXT)
        clicked_wake_button = False

        start = time.monotonic()
        deadline = start + MAX_WAIT_SECONDS
        next_progress_log = start + PROGRESS_LOG_EVERY_SECONDS
        while time.monotonic() < deadline:
            if app_title.count() > 0 and app_title.first.is_visible():
                print("Confirmado: la app está arriba y mostrando su contenido real.")
                browser.close()
                return 0

            if not clicked_wake_button and wake_button.count() > 0 and wake_button.first.is_visible():
                print("La app estaba dormida, haciendo clic para despertarla...")
                wake_button.first.click()
                clicked_wake_button = True

            now = time.monotonic()
            if now >= next_progress_log:
                body_len = len(page.inner_text("body"))
                print(f"[{int(now - start)}s] body todavía sin título real. Caracteres visibles en body: {body_len}")
                next_progress_log += PROGRESS_LOG_EVERY_SECONDS

            time.sleep(POLL_INTERVAL_SECONDS)

        print(
            f"Pasaron {MAX_WAIT_SECONDS}s y no se pudo confirmar que la app cargó su "
            "contenido real. Guardando diagnóstico."
        )
        page.screenshot(path=SCREENSHOT_PATH)

        html = page.content()
        body_start = html.find("<body")
        body_snippet = html[body_start:body_start + 3000] if body_start != -1 else "(no se encontró <body> en el HTML)"

        print(f"¿Se hizo clic en el botón de despertar?: {clicked_wake_button}")
        print(f"Título de la pestaña: {page.title()!r}")
        print(f"Longitud total del HTML: {len(html)}")
        print(f"Texto visible del body: {page.inner_text('body')[:500]!r}")
        print(f"HTML del <body> (primeros 3000 caracteres desde <body>): {body_snippet!r}")
        print(f"Errores de página (excepciones JS no capturadas): {page_errors!r}")
        print(f"Mensajes de consola ({len(console_messages)} en total, últimos 20): {console_messages[-20:]!r}")

        browser.close()
        return 1


if __name__ == "__main__":
    sys.exit(main())
