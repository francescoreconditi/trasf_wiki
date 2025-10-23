"""GUI Launcher for PDF/Word → MediaWiki Converter.

This application provides a simple graphical interface to:
- Start/stop the FastAPI backend server
- Open the application in the default web browser
"""

import os
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, scrolledtext


def get_base_path() -> Path:
    """Get the base path for the application.

    When running as a PyInstaller executable, returns sys._MEIPASS.
    Otherwise returns the directory containing this script.

    Returns:
        Path to the base directory
    """
    if getattr(sys, "frozen", False):
        # Running as PyInstaller executable
        return Path(sys._MEIPASS)
    else:
        # Running as normal Python script
        return Path(__file__).parent


class AppLauncher:
    """Main application launcher window."""

    def __init__(self) -> None:
        """Initialize the launcher window and UI components."""
        self.window = tk.Tk()
        self.window.title("Convertitore PDF/Word → MediaWiki")
        self.window.geometry("600x500")
        self.window.resizable(True, True)

        # Server process and state
        self.server_process: subprocess.Popen | None = None
        self.server_thread: threading.Thread | None = None
        self.uvicorn_server = None  # For embedded mode
        self.is_running = False
        self.is_frozen = getattr(sys, "frozen", False)

        # Server configuration
        self.host = "localhost"
        self.port = 8001  # Changed from 8000 to avoid conflicts with other services
        self.url = f"http://{self.host}:{self.port}"

        # UI variables
        self.status_var = tk.StringVar(value="● Pronto")
        self.status_color = "gray"

        # Create UI
        self.create_widgets()

        # Handle window close event
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self) -> None:
        """Create and layout all UI widgets."""
        # Title
        title = tk.Label(
            self.window,
            text="Convertitore PDF/Word → MediaWiki",
            font=("Arial", 14, "bold"),
            fg="#2c3e50",
        )
        title.pack(pady=20)

        # Buttons frame
        buttons_frame = tk.Frame(self.window)
        buttons_frame.pack(pady=10)

        # Start button
        self.btn_start = tk.Button(
            buttons_frame,
            text="🚀 Avvia Applicazione",
            command=self.start_server,
            width=25,
            height=2,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
        )
        self.btn_start.grid(row=0, column=0, padx=5, pady=5)

        # Stop button
        self.btn_stop = tk.Button(
            buttons_frame,
            text="⏹️ Ferma Applicazione",
            command=self.stop_server,
            width=25,
            height=2,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            state=tk.DISABLED,
        )
        self.btn_stop.grid(row=1, column=0, padx=5, pady=5)

        # Open browser button
        self.btn_open = tk.Button(
            buttons_frame,
            text="🌐 Apri nel Browser",
            command=self.open_browser,
            width=25,
            height=2,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            state=tk.DISABLED,
        )
        self.btn_open.grid(row=2, column=0, padx=5, pady=5)

        # Status frame
        status_frame = tk.Frame(self.window, bg="#ecf0f1", relief=tk.RIDGE, bd=2)
        status_frame.pack(pady=15, padx=20, fill=tk.X)

        status_label = tk.Label(
            status_frame, text="Status:", bg="#ecf0f1", font=("Arial", 10, "bold")
        )
        status_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        self.status_display = tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg="#ecf0f1",
            fg=self.status_color,
            font=("Arial", 10),
        )
        self.status_display.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        url_label = tk.Label(
            status_frame, text="URL:", bg="#ecf0f1", font=("Arial", 10, "bold")
        )
        url_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        url_display = tk.Label(
            status_frame, text=self.url, bg="#ecf0f1", fg="#3498db", font=("Arial", 10)
        )
        url_display.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Log output (small area)
        log_label = tk.Label(
            self.window, text="Log Output:", font=("Arial", 9), fg="#7f8c8d"
        )
        log_label.pack(pady=(10, 0))

        self.log_text = scrolledtext.ScrolledText(
            self.window,
            height=12,
            width=70,
            state=tk.DISABLED,
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Consolas", 9),
        )
        self.log_text.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)

    def log(self, message: str) -> None:
        """Add a message to the log output.

        Args:
            message: The message to log
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def update_status(self, status: str, color: str) -> None:
        """Update the status display.

        Args:
            status: Status text to display
            color: Color of the status text
        """
        self.status_var.set(status)
        self.status_display.config(fg=color)

    def start_server(self) -> None:
        """Start the FastAPI backend server in a separate thread."""
        if self.is_running:
            self.log("⚠️ Server già in esecuzione")
            return

        # Mark as running IMMEDIATELY to prevent double-click race condition
        self.is_running = True

        self.log("🚀 Avvio server in corso...")
        self.update_status("● Avvio in corso...", "orange")

        # Disable start button immediately
        self.btn_start.config(state=tk.DISABLED)

        # Start server in background thread
        thread = threading.Thread(target=self._start_server_thread, daemon=True)
        thread.start()

    def _start_server_thread(self) -> None:
        """Background thread to start the server process."""
        try:
            if self.is_frozen:
                # Running as PyInstaller executable - import and run uvicorn directly
                self._start_server_embedded()
            else:
                # Running as normal script - use subprocess
                self._start_server_subprocess()

        except Exception as e:
            error_msg = f"❌ Errore avvio server: {e}"
            self.window.after(0, self.log, error_msg)
            self.window.after(0, self.update_status, "● Errore", "red")
            self.is_running = False

    def _start_server_embedded(self) -> None:
        """Start the server embedded in the executable (PyInstaller mode)."""
        try:
            import asyncio
            import uvicorn

            # Add backend path to sys.path so imports work
            base_path = get_base_path()
            backend_path = base_path / "backend"

            self.window.after(0, self.log, f"📂 Base path: {base_path}")
            self.window.after(0, self.log, f"📂 Backend path: {backend_path}")
            self.window.after(
                0, self.log, f"📂 Backend exists: {backend_path.exists()}"
            )

            if str(backend_path) not in sys.path:
                sys.path.insert(0, str(backend_path))
                self.window.after(0, self.log, f"✅ Aggiunto {backend_path} a sys.path")

            self.window.after(
                0, self.log, "🔧 Modalità eseguibile - avvio server integrato..."
            )

            # Fix for PyInstaller GUI mode: redirect stdout/stderr to capture backend logs
            # IMPORTANT: Set this BEFORE importing app.main so we capture startup prints!
            import io

            # Create custom stream that logs to GUI
            class GUIStream:
                def write(self, text):
                    if text.strip():
                        self.window.after(0, self.log, f"[BACKEND] {text.strip()}")

                        # Detect when server is ready and update UI
                        if "Uvicorn running on" in text:
                            self.window.after(0, self._on_server_ready)

                def flush(self):
                    pass

                def isatty(self):
                    """Return False to indicate this is not a TTY."""
                    return False

                def fileno(self):
                    """Return -1 to indicate no file descriptor."""
                    return -1

            gui_stream = GUIStream()
            gui_stream.window = self.window
            gui_stream.log = self.log
            gui_stream._on_server_ready = self._on_server_ready

            if sys.stdout is None:
                sys.stdout = gui_stream
            if sys.stderr is None:
                sys.stderr = gui_stream

            self.window.after(0, self.log, "✅ GUIStream configurato")

            # Import the FastAPI app (now prints will be captured)
            self.window.after(0, self.log, "📦 Importando app.main...")
            from app.main import app

            self.window.after(0, self.log, "✅ app.main importato con successo")

            # Suppress uvicorn logging
            import logging

            logging.getLogger("uvicorn").setLevel(logging.WARNING)
            logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
            logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

            # Check if port is available
            import socket

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((self.host, self.port))
                sock.close()
                if result == 0:
                    self.window.after(0, self.log, f"❌ Porta {self.port} già in uso!")
                    self.window.after(
                        0,
                        self.log,
                        "💡 Chiudi le istanze precedenti dell'applicazione",
                    )
                    self.is_running = False
                    self.window.after(0, self.update_status, "● Errore", "red")
                    self.window.after(0, lambda: self.btn_start.config(state=tk.NORMAL))
                    return
                else:
                    self.window.after(0, self.log, f"✅ Porta {self.port} disponibile")
            except Exception as e:
                self.window.after(0, self.log, f"⚠️ Errore check porta: {e}")

            # Enable stop button
            self.window.after(0, lambda: self.btn_stop.config(state=tk.NORMAL))

            self.window.after(
                0, self.log, f"🚀 Avviando server su {self.host}:{self.port}..."
            )

            # SIMPLE APPROACH: Just use uvicorn.run() - it blocks until server stops
            try:
                # Note: uvicorn.run() will log "Uvicorn running on..." when ready
                uvicorn.run(
                    app,
                    host=self.host,
                    port=self.port,
                    log_level="info",  # Changed to info to see startup message
                    access_log=False,
                )
                self.window.after(0, self.log, "🛑 Server arrestato normalmente")

            except Exception as server_error:
                import traceback

                self.window.after(0, self.log, "❌ ERRORE DURANTE ESECUZIONE SERVER:")
                error_details = traceback.format_exc()
                for line in error_details.split("\n"):
                    if line.strip():
                        self.window.after(0, self.log, line)
                self.is_running = False
                self.window.after(0, self.update_status, "● Errore", "red")
                raise

        except Exception as e:
            import traceback

            error_details = traceback.format_exc()
            self.window.after(0, self.log, "❌ ERRORE DETTAGLIATO:")
            for line in error_details.split("\n"):
                if line.strip():
                    self.window.after(0, self.log, line)
            raise

    def _start_server_subprocess(self) -> None:
        """Start the server as a subprocess (normal Python mode)."""
        # Get path to backend directory
        backend_path = Path(__file__).parent / "backend"

        # Determine Python executable (check for venv first)
        venv_python = backend_path / ".venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            python_exe = str(venv_python)
        else:
            python_exe = sys.executable

        self.window.after(
            0, self.log, "🔧 Modalità sviluppo - avvio server subprocess..."
        )

        # Start uvicorn server
        self.server_process = subprocess.Popen(
            [
                python_exe,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                self.host,
                "--port",
                str(self.port),
            ],
            cwd=str(backend_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )

        self.is_running = True

        # Update UI in main thread
        self.window.after(0, self._on_server_started)

        # Read server output
        if self.server_process.stdout:
            for line in self.server_process.stdout:
                self.window.after(0, self.log, line.strip())

    def _on_server_started(self) -> None:
        """Update UI after server has started successfully."""
        self.log("✅ Server avviato con successo!")
        self.log(f"🌐 Applicazione disponibile su: {self.url}")
        self.update_status("● In esecuzione", "green")

        # Update button states
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_open.config(state=tk.NORMAL)

    def _on_server_ready(self) -> None:
        """Update UI when server is ready to accept connections."""
        self.log("✅ Server pronto ad accettare connessioni!")
        self.update_status("● In esecuzione", "green")

        # Enable "Open Browser" button
        self.btn_open.config(state=tk.NORMAL)

    def stop_server(self) -> None:
        """Stop the FastAPI backend server."""
        if not self.is_running:
            self.log("⚠️ Nessun server in esecuzione")
            return

        self.log("⏹️ Arresto server...")
        self.update_status("● Arresto in corso...", "orange")

        try:
            if self.is_frozen and self.uvicorn_server:
                # Stop embedded uvicorn server
                self.uvicorn_server.should_exit = True
                self.uvicorn_server = None
            elif self.server_process:
                # Terminate subprocess
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                self.server_process = None
        except subprocess.TimeoutExpired:
            # Force kill subprocess if not terminated
            if self.server_process:
                self.server_process.kill()
            self.log("⚠️ Server terminato forzatamente")
        except Exception as e:
            self.log(f"❌ Errore arresto server: {e}")

        self.is_running = False

        self.log("✅ Server arrestato")
        self.update_status("● Pronto", "gray")

        # Update button states
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_open.config(state=tk.DISABLED)

    def open_browser(self) -> None:
        """Open the application in the default web browser."""
        if not self.is_running:
            messagebox.showwarning(
                "Server non avviato",
                "Avvia prima il server con il pulsante '🚀 Avvia Applicazione'",
            )
            return

        self.log(f"🌐 Apertura browser su {self.url}...")
        try:
            webbrowser.open(self.url)
            self.log("✅ Browser aperto")
        except Exception as e:
            self.log(f"❌ Errore apertura browser: {e}")
            messagebox.showerror("Errore", f"Impossibile aprire il browser:\n{e}")

    def on_closing(self) -> None:
        """Handle window close event - stop server before closing."""
        if self.is_running:
            response = messagebox.askyesno(
                "Server in esecuzione",
                "Il server è ancora in esecuzione.\nVuoi fermarlo e chiudere l'applicazione?",
            )
            if response:
                self.stop_server()
                self.window.after(500, self.window.destroy)
        else:
            self.window.destroy()

    def run(self) -> None:
        """Start the GUI main loop."""
        self.window.mainloop()


def main() -> None:
    """Main entry point for the launcher application."""
    app = AppLauncher()
    app.run()


if __name__ == "__main__":
    main()
