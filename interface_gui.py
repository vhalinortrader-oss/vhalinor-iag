#!/usr/bin/env python3
"""VhalinorTrade GUI (desktop)

Interface mínima para controlar o sistema e visualizar métricas.

Uso:
  . .venv/bin/activate
  python interface_gui.py

Observação:
- O sistema VhalinorTrade é assíncrono; a GUI roda em thread e executa um event loop separado.
- Por padrão, a GUI chama `VhalinorTrade()` e `start()/stop()`.
"""

import threading
import queue
import time
import traceback
import tkinter as tk
from tkinter import ttk, messagebox


class VhalinorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VhalinorTrade Interface")
        self.geometry("900x550")

        self.status_var = tk.StringVar(value="Pronto")
        self.predictions_var = tk.StringVar(value="-")
        self.win_rate_var = tk.StringVar(value="-")
        self.exposure_var = tk.StringVar(value="-")
        self.reserve_var = tk.StringVar(value="-")
        self.active_trades_var = tk.StringVar(value="-")

        self._cmd_q: queue.Queue = queue.Queue()
        self._evt_q: queue.Queue = queue.Queue()

        self._worker_thread = None
        self._running = False
        self._stop_requested = False

        self._build_ui()
        self.after(200, self._poll_events)

    def _build_ui(self):
        top = ttk.Frame(self, padding=12)
        top.pack(fill=tk.BOTH, expand=False)

        controls = ttk.LabelFrame(top, text="Controle", padding=12)
        controls.pack(fill=tk.X)

        self.start_btn = ttk.Button(controls, text="Iniciar", command=self.on_start)
        self.start_btn.pack(side=tk.LEFT)

        self.stop_btn = ttk.Button(controls, text="Parar", command=self.on_stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(8, 0))

        self.quit_btn = ttk.Button(controls, text="Sair", command=self.on_quit)
        self.quit_btn.pack(side=tk.RIGHT)

        ttk.Label(controls, textvariable=self.status_var).pack(side=tk.LEFT, padx=16)

        metrics = ttk.LabelFrame(top, text="Métricas (aprox.)", padding=12)
        metrics.pack(fill=tk.X, pady=(12, 0))

        grid = ttk.Frame(metrics)
        grid.pack(fill=tk.X)

        pairs = [
            ("Trades ativos", self.active_trades_var),
            ("Exposição", self.exposure_var),
            ("Reserva", self.reserve_var),
            ("Predições hoje", self.predictions_var),
            ("Win rate", self.win_rate_var),
        ]

        for i, (label, var) in enumerate(pairs):
            r = i // 2
            c = i % 2
            cell = ttk.Frame(grid, padding=6)
            cell.grid(row=r, column=c, sticky="nsew", padx=8, pady=4)

            ttk.Label(cell, text=label).pack(anchor="w")
            ttk.Label(cell, textvariable=var, font=("TkDefaultFont", 12, "bold")).pack(anchor="w", pady=(4, 0))

        bottom = ttk.LabelFrame(self, text="Log / Eventos", padding=12)
        bottom.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        self.log_text = tk.Text(bottom, height=14, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state=tk.DISABLED)

    def _append_log(self, msg: str):
        self.log_text.configure(state=tk.NORMAL)
        ts = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.configure(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def on_start(self):
        if self._running:
            return
        self._stop_requested = False

        # Se o worker já rodou uma vez, não crie outro thread.
        self._cmd_q.put(("start", None))

        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._worker_thread = threading.Thread(
                target=self._worker_main,
                daemon=True,
            )
            self._worker_thread.start()

        self._running = True
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.status_var.set("Iniciando...")
        self._append_log("Solicitando start()...")

    def on_stop(self):
        if not self._running:
            return
        self._stop_requested = True
        self.status_var.set("Parando...")
        self._append_log("Solicitando stop()...")
        self._cmd_q.put(("stop", None))
        self.stop_btn.configure(state=tk.DISABLED)

    def on_quit(self):
        try:
            if self._running:
                self._stop_requested = True
                self._cmd_q.put(("stop", None))
        except Exception:
            pass
        self.destroy()

    def _poll_events(self):
        try:
            while True:
                evt = self._evt_q.get_nowait()
                etype = evt.get("type")
                if etype == "log":
                    self._append_log(evt.get("message", ""))
                elif etype == "status":
                    self.status_var.set(evt.get("message", ""))
                elif etype == "metrics":
                    m = evt.get("metrics", {})
                    self.active_trades_var.set(str(m.get("active_trades", "-")))
                    exposure = m.get("exposure", None)
                    self.exposure_var.set("-" if exposure is None else (f"{exposure:.2%}" if isinstance(exposure, float) else str(exposure)))
                    self.reserve_var.set("-" if m.get("reserve_fund") is None else str(m.get("reserve_fund")))
                    self.predictions_var.set(str(m.get("predictions_today", "-")))
                    self.win_rate_var.set(str(m.get("win_rate", "-")))
                elif etype == "error":
                    msg = evt.get("message", "Erro")
                    self._append_log("ERRO: " + msg)
                    messagebox.showerror("Erro", msg)
                    self.status_var.set("Erro")
                    self.start_btn.configure(state=tk.NORMAL)
                    self.stop_btn.configure(state=tk.DISABLED)
                    self._running = False
        except queue.Empty:
            pass
        self.after(200, self._poll_events)

    def _worker_main(self):
        # Worker: cria event loop e controla VhalinorTrade
        import asyncio

        # Import aqui para evitar travar o start da GUI caso dependências estejam faltando
        # (módulo com nome começando por número exige carregamento via importlib)
        import importlib.util
        import pathlib

        main_path = pathlib.Path(__file__).resolve().parent / "09_main_system.py"
        spec = importlib.util.spec_from_file_location("vhalinor_main_system", main_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Não foi possível carregar {main_path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        VhalinorTrade = getattr(mod, "VhalinorTrade")

        async def runner():
            vhalinor = VhalinorTrade()
            started = False

            while True:
                # processa comandos recebidos
                try:
                    cmd, _ = self._cmd_q.get_nowait()
                    if cmd == "start" and not started:
                        started = True
                        self._evt_q.put({"type": "log", "message": "start()"})
                        self._evt_q.put({"type": "status", "message": "Rodando"})
                        asyncio.create_task(vhalinor.start())
                    elif cmd == "stop":
                        self._evt_q.put({"type": "log", "message": "stop()"})
                        await vhalinor.stop()
                        self._evt_q.put({"type": "status", "message": "Parado"})
                        self._evt_q.put({"type": "log", "message": "Sistema parado"})
                        break
                except queue.Empty:
                    pass

                # atualiza métricas periodicamente
                try:
                    if started:
                        metrics = vhalinor.get_system_metrics()
                        self._evt_q.put({"type": "metrics", "metrics": metrics})
                except Exception as e:
                    # evita crash do worker
                    self._evt_q.put({"type": "error", "message": str(e)})

                await asyncio.sleep(1.0)

        # Event loop próprio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(runner())
        except Exception as e:
            self._evt_q.put({"type": "error", "message": f"Falha no worker: {e}\n{traceback.format_exc()}"})


if __name__ == "__main__":
    app = VhalinorGUI()
    app.mainloop()

