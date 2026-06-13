#!/usr/bin/env python3
"""VhalinorTrade Web Interface (FastAPI)

- Mostra status e métricas
- Permite iniciar/parar o sistema

Como rodar:
  1) . .venv/bin/activate
  2) pip install fastapi uvicorn
  3) uvicorn interface_web:app --reload --host 0.0.0.0 --port 8000

Endpoints:
  GET  /health
  GET  /metrics
  POST /start
  POST /stop

Observação:
- O sistema VhalinorTrade é assíncrono. Este servidor mantém um único
  processo do sistema e controla via filas/eventos.
- Como o arquivo do core começa com número (09_main_system.py), carregamos
  via importlib.
"""

import asyncio
import threading
import importlib.util
import pathlib
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel


APP_PATH = pathlib.Path(__file__).resolve().parent


def load_vhalinor_trade_class():
    main_path = APP_PATH / "09_main_system.py"
    spec = importlib.util.spec_from_file_location("vhalinor_main_system", main_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {main_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "VhalinorTrade")


VhalinorTrade = load_vhalinor_trade_class()

app = FastAPI(title="VhalinorTrade Web Interface")


class ControlResponse(BaseModel):
    ok: bool
    message: str


# Estado compartilhado (controlado pelo event loop do worker)
_system: Optional[object] = None
_loop: Optional[asyncio.AbstractEventLoop] = None
_worker_thread: Optional[threading.Thread] = None
_state_lock = threading.Lock()

_started_event = threading.Event()
_stopped_event = threading.Event()


def _start_worker_thread():
    global _worker_thread, _loop

    if _worker_thread is not None and _worker_thread.is_alive():
        return

    _stopped_event.clear()
    _started_event.clear()

    def runner():
        global _loop, _system
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)

        async def main():
            global _system
            _system = VhalinorTrade()
            _started_event.set()
            await _system.start()

        try:
            _loop.create_task(main())
            _loop.run_forever()
        finally:
            try:
                _stopped_event.set()
            except Exception:
                pass

    _worker_thread = threading.Thread(target=runner, daemon=True)
    _worker_thread.start()


def _schedule_coro(coro):
    if _loop is None:
        raise RuntimeError("Event loop do worker não inicializado")
    return asyncio.run_coroutine_threadsafe(coro, _loop)


@app.get("/health")
async def health():
    return {"ok": True, "started": _started_event.is_set()}


@app.get("/metrics")
async def metrics():
    if _system is None:
        return {"status": "stopped", "metrics": None}

    # get_system_metrics é síncrono no seu core
    try:
        m = _system.get_system_metrics()
        return {"status": "running", "metrics": m}
    except Exception as e:
        return {"status": "error", "metrics": None, "error": str(e)}


@app.post("/start", response_model=ControlResponse)
async def start():
    with _state_lock:
        if _system is not None and _started_event.is_set():
            return ControlResponse(ok=True, message="Sistema já iniciado")
        _start_worker_thread()

    # aguarda sinal de iniciado (instancia feita)
    await asyncio.to_thread(_started_event.wait, 20)
    return ControlResponse(ok=True, message="Solicitado start")


@app.post("/stop", response_model=ControlResponse)
async def stop():
    with _state_lock:
        if _system is None:
            return ControlResponse(ok=True, message="Sistema não iniciado")

        # chama stop no mesmo loop do worker
        try:
            fut = _schedule_coro(_system.stop())
            await asyncio.wrap_future(fut)
        except Exception as e:
            return ControlResponse(ok=False, message=f"Falha ao parar: {e}")

        # encerra loop do worker
        try:
            if _loop is not None:
                _loop.call_soon_threadsafe(_loop.stop)
        except Exception:
            pass

    await asyncio.to_thread(_stopped_event.wait, 20)
    return ControlResponse(ok=True, message="Parado")

