from __future__ import annotations

import queue
import streamlit as st

# Persistent log queue across reruns
@st.cache_resource
def get_log_queue() -> "queue.Queue[str]":
    # Persist across Streamlit reruns
    return queue.Queue()


def clear_queue(q: "queue.Queue[str]") -> None:
    try:
        while True:
            q.get_nowait()
    except queue.Empty:
        return

import threading
import time
from typing import List, Optional

import sys
from pathlib import Path

# Streamlit führt Scripts so aus, dass nur der Script-Ordner (src/) auf sys.path ist.
# Damit `import src....` zuverlässig funktioniert, fügen wir den Projekt-Root hinzu.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.config.settings import load_settings
from src.core.runner import Runner


def _init_state() -> None:
    if "logs" not in st.session_state:
        st.session_state.logs = []  # type: List[str]
    if "runner" not in st.session_state:
        st.session_state.runner = None  # type: Optional[Runner]
    if "thread" not in st.session_state:
        st.session_state.thread = None  # type: Optional[threading.Thread]
    if "running" not in st.session_state:
        st.session_state.running = False


def _on_log(message: str) -> None:
    ts = time.strftime("%H:%M:%S")
    q = get_log_queue()
    q.put(f"{ts} | {message}")


def _drain_logs(max_items: int = 200) -> None:
    q = get_log_queue()
    logs: List[str] = st.session_state.logs

    drained = 0
    while drained < max_items:
        try:
            msg = q.get_nowait()
        except queue.Empty:
            break
        
        if msg == "__RUN_DONE__":
            st.session_state.running = False
            continue
        
        logs.append(msg)
        drained += 1

    # Begrenze Log-Historie
    if len(logs) > 500:
        st.session_state.logs = logs[-500:]


def _reset_logs_and_queue() -> None:
    st.session_state.logs = []
    clear_queue(get_log_queue())


def _start_run(to_email: str, count: int, interval_seconds: int) -> None:
    settings = load_settings()

    runner = Runner(
        settings=settings,
        to_email=to_email,
        count=count,
        interval_seconds=interval_seconds,
        on_log=_on_log,
    )

    def _run_and_signal() -> None:
        try:
            runner.run()
        finally:
            # Signal the UI that the run is finished
            get_log_queue().put("__RUN_DONE__")

    t = threading.Thread(target=_run_and_signal, daemon=True)

    st.session_state.runner = runner
    st.session_state.thread = t
    st.session_state.running = True

    t.start()


def _stop_run() -> None:
    runner: Optional[Runner] = st.session_state.runner
    if runner is not None:
        runner.stop()


def _is_thread_alive() -> bool:
    t: Optional[threading.Thread] = st.session_state.thread
    return bool(t and t.is_alive())


def main() -> None:
    st.set_page_config(page_title="Gmail Random Mailer", layout="centered")
    st.title("Gmail Random Mailer")
    st.caption("KI-generierte Test-E-Mails via Gmail SMTP (App Password)")

    _init_state()

    with st.form("config"):
        to_email = st.text_input("Empfänger E-Mail", placeholder="test@example.com")
        count = st.number_input("Anzahl Mails", min_value=1, max_value=500, value=1, step=1)
        interval_seconds = st.number_input(
            "Intervall (Sekunden)", min_value=10, max_value=3600, value=120, step=10
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            start = st.form_submit_button("Start")
        with col2:
            stop = st.form_submit_button("Stop")
        with col3:
            clear = st.form_submit_button("Logs leeren")

    if clear:
        _reset_logs_and_queue()

    if start:
        if st.session_state.running and _is_thread_alive():
            st.warning("Läuft bereits. Bitte zuerst Stop.")
        elif not to_email.strip():
            st.error("Bitte Empfänger-E-Mail angeben.")
        else:
            _reset_logs_and_queue()
            _start_run(to_email.strip(), int(count), int(interval_seconds))
            st.success("Run gestartet.")

    if stop:
        _stop_run()

    _drain_logs()
    alive = _is_thread_alive()
    if st.session_state.running and alive:
        st.info("Status: Running")
    elif (not st.session_state.running) and (st.session_state.thread is not None or len(st.session_state.logs) > 0):
        st.info("Status: Finished")
    else:
        st.info("Status: Idle")

    logs_text = "\n".join(st.session_state.logs)
    # Quick error hint
    last_error = next((l for l in reversed(st.session_state.logs) if "FEHLER" in l), None)
    if last_error:
        st.error(last_error)
    st.text_area("Logs", value=logs_text, height=320)

    # Auto-refresh while a run is active, or while there are still pending log lines.
    # This ensures the UI shows the full log output without manual interaction.
    if (alive or not get_log_queue().empty()) and (st.session_state.thread is not None):
        time.sleep(0.5)
        st.rerun()


if __name__ == "__main__":
    main()