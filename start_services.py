"""
Orquestador de microservicios - lee el Procfile y levanta cada servicio
mostrando sus logs en tiempo real con colores por servicio.

Uso:
    python start_services.py              # levanta todos
    python start_services.py auth branch  # levanta solo los indicados
"""
import subprocess
import sys
import os
import threading
import signal
from datetime import datetime

# Colores ANSI para cada servicio
COLORS = [
    "\033[36m",  # cyan
    "\033[32m",  # green
    "\033[33m",  # yellow
    "\033[35m",  # magenta
    "\033[34m",  # blue
    "\033[91m",  # bright red
    "\033[96m",  # bright cyan
]
RESET = "\033[0m"
BOLD  = "\033[1m"

processes: list[subprocess.Popen] = []


def parse_procfile(path: str) -> dict[str, str]:
    services = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, _, command = line.partition(":")
            services[name.strip()] = command.strip()
    return services


def stream_output(proc: subprocess.Popen, prefix: str, color: str) -> None:
    for raw in proc.stdout:
        line = raw.decode("utf-8", errors="replace").rstrip()
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"{BOLD}{color}{ts} {prefix:<14}{RESET} | {line}", flush=True)


def shutdown(signum=None, frame=None) -> None:
    print(f"\n{BOLD}Deteniendo todos los servicios...{RESET}")
    for p in processes:
        if p.poll() is None:
            p.terminate()
    for p in processes:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
    sys.exit(0)


def main() -> None:
    root = os.path.dirname(os.path.abspath(__file__))
    procfile = os.path.join(root, "Procfile")

    if not os.path.exists(procfile):
        print("ERROR: No se encontró el Procfile en la raíz del proyecto.")
        sys.exit(1)

    all_services = parse_procfile(procfile)

    # Filtrar por argumentos si se pasan nombres concretos
    requested = sys.argv[1:]
    if requested:
        selected = {k: v for k, v in all_services.items() if k in requested}
        missing = set(requested) - set(selected)
        if missing:
            print(f"ERROR: Servicios no encontrados en Procfile: {', '.join(missing)}")
            sys.exit(1)
    else:
        selected = all_services

    if not selected:
        print("No hay servicios que levantar.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"{BOLD}Levantando {len(selected)} servicio(s): {', '.join(selected)}{RESET}\n")

    threads = []
    for i, (name, command) in enumerate(selected.items()):
        color = COLORS[i % len(COLORS)]
        # Ejecutar con shell=True para soportar "cd x && python run.py"
        proc = subprocess.Popen(
            command,
            shell=True,
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        processes.append(proc)
        t = threading.Thread(target=stream_output, args=(proc, name, color), daemon=True)
        t.start()
        threads.append(t)

    # Esperar a que todos los procesos terminen
    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
