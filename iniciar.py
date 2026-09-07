#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
Sistema SAC WEB - Iniciador Universal de Servidor (Multiplataforma)
==============================================================================
Script maestro agnóstico al Sistema Operativo (Windows, Linux, macOS).
Automatiza:
  1. Detección y auto-creación del entorno virtual (venv/.venv).
  2. Verificación e instalación de dependencias (requirements.txt).
  3. Auto-sanación y validación de variables de entorno (.env).
  4. Chequeo de integridad y aplicación de migraciones Django.
  5. Detección inteligente de puertos libres con auto-resolución de conflictos.
  6. Apertura automática del navegador web con sonda de disponibilidad (Readiness Probe).
  7. Gestión limpia de procesos y captura de señales (Ctrl+C / SIGINT / SIGTERM).

Autor: Script Master Engineer
Versión: 3.0.0
==============================================================================
"""

import argparse
import os
import platform
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path
from typing import List, Optional, Tuple

# =============================================================================
# CONSTANTES Y CONFIGURACIÓN GLOBAL
# =============================================================================
VERSION = "3.0.0"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
BASE_DIR = Path(__file__).resolve().parent

# =============================================================================
# SISTEMA DE LOGS Y COLORES ANSI COMPATIBLE MULTIPLATAFORMA
# =============================================================================
class Logger:
    """Manejo de salida formateada en stderr con soporte de color multiplataforma."""
    
    _colors_enabled = False

    @classmethod
    def init_colors(cls) -> None:
        """Inicializa soporte ANSI en Windows 10+ o verifica si está habilitado."""
        if os.environ.get("NO_COLOR") or not sys.stderr.isatty():
            cls._colors_enabled = False
            return

        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # Habilitar ENABLE_VIRTUAL_TERMINAL_PROCESSING (0x0004)
                handle = kernel32.GetStdHandle(-12)  # STD_ERROR_HANDLE
                mode = ctypes.c_ulong()
                if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                    mode.value |= 0x0004
                    kernel32.SetConsoleMode(handle, mode)
                    cls._colors_enabled = True
            except Exception:
                cls._colors_enabled = False
        else:
            cls._colors_enabled = True

    @classmethod
    def _colorize(cls, text: str, color_code: str) -> str:
        if cls._colors_enabled:
            return f"\033[{color_code}m{text}\033[0m"
        return text

    @classmethod
    def info(cls, msg: str) -> None:
        prefix = cls._colorize("[INFO]", "1;34")
        print(f"{prefix} {msg}", file=sys.stderr, flush=True)

    @classmethod
    def success(cls, msg: str) -> None:
        prefix = cls._colorize("[OK]", "1;32")
        print(f"{prefix} {msg}", file=sys.stderr, flush=True)

    @classmethod
    def warn(cls, msg: str) -> None:
        prefix = cls._colorize("[AVISO]", "1;33")
        print(f"{prefix} {msg}", file=sys.stderr, flush=True)

    @classmethod
    def error(cls, msg: str) -> None:
        prefix = cls._colorize("[ERROR]", "1;31")
        print(f"{prefix} {msg}", file=sys.stderr, flush=True)

    @classmethod
    def step(cls, title: str) -> None:
        bullet = cls._colorize("==>", "1;36")
        print(f"\n{bullet} {cls._colorize(title, '1;37')}", file=sys.stderr, flush=True)

    @classmethod
    def banner(cls) -> None:
        border = cls._colorize("================================================================", "1;36")
        title = cls._colorize("                 SISTEMA SAC WEB - SERVIDOR                     ", "1;37")
        print(f"\n{border}\n{title}\n{border}\n", file=sys.stderr, flush=True)


# =============================================================================
# GESTOR DE ENTORNO VIRTUAL Y DEPENDENCIAS
# =============================================================================
class EnvironmentManager:
    """Gestiona la detección, creación y re-ejecución dentro del entorno virtual."""

    @staticmethod
    def is_running_in_venv() -> bool:
        """Determina si el proceso actual corre dentro de un virtualenv."""
        return sys.prefix != getattr(sys, "base_prefix", sys.prefix)

    @staticmethod
    def get_venv_python_executable(venv_path: Path) -> Optional[Path]:
        """Obtiene la ruta canónica al ejecutable de Python dentro del virtualenv."""
        if platform.system() == "Windows":
            candidate = venv_path / "Scripts" / "python.exe"
            if candidate.is_file():
                return candidate
        else:
            candidate = venv_path / "bin" / "python"
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate
        return None

    @classmethod
    def find_or_create_venv(cls, custom_path: Optional[str] = None) -> Path:
        """
        Busca un venv existente en el proyecto o crea uno nuevo en ./venv.
        Retorna la ruta al ejecutable de Python dentro del venv.
        """
        if custom_path:
            p = Path(custom_path).resolve()
            py_bin = cls.get_venv_python_executable(p)
            if py_bin:
                return py_bin
            Logger.error(f"No se encontró un ejecutable de Python en el entorno virtual personalizado '{p}'.")
            sys.exit(1)

        # Candidatos habituales
        candidates = [
            BASE_DIR / "venv",
            BASE_DIR / ".venv",
            BASE_DIR.parent / "venv",
        ]

        for cand in candidates:
            if cand.is_dir():
                py_bin = cls.get_venv_python_executable(cand)
                if py_bin:
                    return py_bin

        # Si no existe, procedemos a crearlo en BASE_DIR / "venv"
        target_venv = BASE_DIR / "venv"
        Logger.step("Creando nuevo entorno virtual (venv)...")
        Logger.info(f"Ruta destino: {target_venv}")

        try:
            import venv
            builder = venv.EnvBuilder(with_pip=True)
            builder.create(str(target_venv))
        except Exception as err:
            Logger.error(f"Error al crear el entorno virtual con módulo nativo 'venv': {err}")
            # Intentar fallback con subprocess
            try:
                subprocess.run([sys.executable, "-m", "venv", str(target_venv)], check=True)
            except Exception as e:
                Logger.error(f"Fallo crítico al crear venv: {e}")
                sys.exit(1)

        py_bin = cls.get_venv_python_executable(target_venv)
        if not py_bin:
            Logger.error(f"No se pudo localizar el binario de Python tras crear {target_venv}.")
            sys.exit(1)

        Logger.success("Entorno virtual creado exitosamente.")
        return py_bin

    @classmethod
    def ensure_dependencies(cls, py_bin: Path, force_reinstall: bool = False) -> None:
        """Verifica que las dependencias de requirements.txt estén satisfechas."""
        requirements_file = BASE_DIR / "requirements.txt"
        if not requirements_file.is_file():
            Logger.warn("No se encontró 'requirements.txt'. Se omitirá la verificación de dependencias.")
            return

        # Si no es reinstalación forzada, hacemos un chequeo rápido de importación
        if not force_reinstall:
            check_code = "import django, dotenv, openpyxl; print('OK')"
            try:
                res = subprocess.run(
                    [str(py_bin), "-c", check_code],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5
                )
                if res.returncode == 0 and "OK" in res.stdout:
                    return  # Dependencias principales listas
            except Exception:
                pass  # Proceder con instalación de pip

        Logger.step("Instalando / actualizando dependencias desde requirements.txt...")
        try:
            # 1. Actualizar pip si es posible
            subprocess.run(
                [str(py_bin), "-m", "pip", "install", "--upgrade", "pip", "--quiet"],
                check=False
            )
            # 2. Instalar requirements.txt
            cmd = [str(py_bin), "-m", "pip", "install", "-r", str(requirements_file)]
            subprocess.run(cmd, check=True)
            Logger.success("Dependencias instaladas y actualizadas correctamente.")
        except subprocess.CalledProcessError as exc:
            Logger.error(f"Error durante la instalación de paquetes con pip: {exc}")
            sys.exit(1)

    @classmethod
    def ensure_node_dependencies(cls) -> None:
        """Verifica e instala dependencias de Node.js (Puppeteer) si package.json existe."""
        package_json = BASE_DIR / "package.json"
        if not package_json.is_file():
            return
        
        node_modules = BASE_DIR / "node_modules"
        puppeteer_dir = node_modules / "puppeteer"
        
        if puppeteer_dir.is_dir():
            return  # Puppeteer ya está instalado
        
        npm_bin = shutil.which("npm")
        if not npm_bin:
            Logger.warn("Node.js / npm no está instalado en el sistema. Los PDFs con Puppeteer requieren Node.js.")
            return
        
        Logger.step("Instalando dependencias de Node.js (Puppeteer para generación de PDFs)...")
        try:
            subprocess.run([npm_bin, "install"], cwd=str(BASE_DIR), check=True)
            Logger.success("Dependencias de Node.js instaladas correctamente.")
        except Exception as exc:
            Logger.warn(f"No se pudo completar npm install: {exc}")



# =============================================================================
# GESTOR DE CONFIGURACIÓN Y ARCHIVO .env
# =============================================================================
class ConfigManager:
    """Valida y autogenera el archivo .env si no existe."""

    @staticmethod
    def ensure_env_file() -> None:
        env_path = BASE_DIR / ".env"
        if env_path.is_file():
            return

        Logger.step("Configurando archivo de entorno (.env)...")
        example_path = BASE_DIR / ".env.example"
        
        # Generar clave secreta criptográficamente segura
        secret_key = f"django-insecure-{secrets.token_urlsafe(50)}"
        
        if example_path.is_file():
            try:
                content = example_path.read_text(encoding="utf-8")
                # Reemplazar placeholder si existe
                if "cambiame-por-una-clave-secreta" in content:
                    content = content.replace("cambiame-por-una-clave-secreta-y-segura-de-al-menos-50-caracteres", secret_key)
                else:
                    content = f"SECRET_KEY=\"{secret_key}\"\nDEBUG=True\nALLOWED_HOSTS=localhost,127.0.0.1\n\n" + content
                env_path.write_text(content, encoding="utf-8")
                Logger.success(f"Archivo .env creado a partir de .env.example con SECRET_KEY generada.")
                return
            except Exception as e:
                Logger.warn(f"No se pudo copiar de .env.example: {e}. Creando .env mínimo.")

        # Contenido por defecto para desarrollo
        default_env = (
            f"# SAC WEB - Configuración de Entorno Local\n"
            f"SECRET_KEY=\"{secret_key}\"\n"
            f"DEBUG=True\n"
            f"ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0\n"
        )
        env_path.write_text(default_env, encoding="utf-8")
        Logger.success("Archivo .env autogenerado con configuración de desarrollo segura.")


# =============================================================================
# GESTOR DE PUERTOS Y RED
# =============================================================================
class NetworkManager:
    """Verificación de disponibilidad de puertos TCP y resolución de conflictos."""

    @staticmethod
    def is_port_available(host: str, port: int) -> bool:
        """Comprueba si un puerto TCP está libre para enlace (bind)."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
                return True
            except OSError:
                return False

    @classmethod
    def find_free_port(cls, host: str, start_port: int, max_attempts: int = 50) -> int:
        """Encuentra el primer puerto libre a partir de start_port."""
        for p in range(start_port, start_port + max_attempts):
            if cls.is_port_available(host, p):
                return p
        return start_port


# =============================================================================
# SONDA DE DISPONIBILIDAD Y APERTURA DE NAVEGADOR (READINESS PROBE)
# =============================================================================
class BrowserLauncher:
    """Abre el navegador web predeterminado una vez que el servidor esté activo."""

    @staticmethod
    def launch_when_ready(url: str, timeout: float = 12.0) -> None:
        def _worker():
            start_time = time.time()
            opened = False
            
            # Polling con socket rápido
            parsed_host = "127.0.0.1"
            parsed_port = 8000
            try:
                from urllib.parse import urlparse
                u = urlparse(url)
                parsed_host = u.hostname or "127.0.0.1"
                parsed_port = u.port or 8000
            except Exception:
                pass

            while time.time() - start_time < timeout:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.5)
                    result = s.connect_ex((parsed_host, parsed_port))
                    s.close()
                    if result == 0:
                        # Servidor aceptando conexiones TCP
                        time.sleep(0.3)
                        webbrowser.open(url)
                        opened = True
                        break
                except Exception:
                    pass
                time.sleep(0.4)

            if not opened:
                # Fallback de gracia
                try:
                    webbrowser.open(url)
                except Exception:
                    pass

        t = threading.Thread(target=_worker, daemon=True)
        t.start()


# =============================================================================
# GESTOR DE BASE DE DATOS Y SERVIDOR DJANGO
# =============================================================================
class DjangoManager:
    """Ejecuta migraciones, chequeos y el servidor runserver."""

    def __init__(self, python_bin: Path):
        self.py_bin = str(python_bin)
        self.manage_py = str(BASE_DIR / "manage.py")

    def run_check(self) -> bool:
        """Ejecuta manage.py check para asegurar consistencia del proyecto."""
        Logger.step("Ejecutando chequeo de integridad de Django (manage.py check)...")
        try:
            res = subprocess.run(
                [self.py_bin, self.manage_py, "check"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            Logger.success("Chequeo del sistema aprobado sin errores.")
            return True
        except subprocess.CalledProcessError as e:
            Logger.error("Falló el chequeo de Django:")
            print(e.stdout, file=sys.stderr)
            return False

    def run_migrations(self) -> bool:
        """Ejecuta manage.py migrate --noinput para aplicar migraciones pendientes."""
        Logger.step("Verificando y aplicando migraciones de base de datos...")
        try:
            subprocess.run(
                [self.py_bin, self.manage_py, "migrate", "--noinput"],
                check=True
            )
            Logger.success("Base de datos sincronizada y al día.")
            return True
        except subprocess.CalledProcessError as e:
            Logger.error(f"Error al ejecutar migraciones: {e}")
            return False

    def start_server(self, host: str, port: int, open_browser: bool = True) -> int:
        """Inicia el servidor de desarrollo runserver con manejo limpio de señales."""
        target_url = f"http://{host}:{port}"
        
        Logger.banner()
        Logger.info(f"Sistema Operativo  : {platform.system()} ({platform.release()})")
        Logger.info(f"Intérprete Python  : {self.py_bin}")
        Logger.info(f"Directorio Raíz    : {BASE_DIR}")
        Logger.info(f"URL del Sistema    : {target_url}")
        Logger.info("Presiona [Ctrl+C] en cualquier momento para detener el servidor de forma segura.\n")

        if open_browser:
            BrowserLauncher.launch_when_ready(target_url)

        cmd = [self.py_bin, self.manage_py, "runserver", f"{host}:{port}"]

        # Manejador de señal limpia
        try:
            proc = subprocess.Popen(cmd, cwd=str(BASE_DIR))

            def _handle_signal(signum, frame):
                Logger.info("\nDeteniendo el servidor SAC WEB...")
                proc.terminate()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    proc.kill()
                Logger.success("Servidor detenido limpiamente.")
                sys.exit(0)

            signal.signal(signal.SIGINT, _handle_signal)
            if hasattr(signal, "SIGTERM"):
                signal.signal(signal.SIGTERM, _handle_signal)

            return proc.wait()
        except KeyboardInterrupt:
            Logger.info("\nDetención solicitada por el usuario.")
            return 0
        except Exception as err:
            Logger.error(f"Fallo al ejecutar el servidor: {err}")
            return 1


# =============================================================================
# ENTRADA PRINCIPAL Y CLI
# =============================================================================
def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="iniciar.py",
        description="Iniciador maestro unificado y resiliente del Sistema SAC Web.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python iniciar.py
  python iniciar.py --port 8080 --host 0.0.0.0
  python iniciar.py --no-browser
  python iniciar.py --no-migrate
  python iniciar.py --dry-run
        """
    )
    parser.add_argument("-H", "--host", default=DEFAULT_HOST, help=f"Dirección IP de escucha (Por defecto: {DEFAULT_HOST})")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT, help=f"Puerto TCP de escucha (Por defecto: {DEFAULT_PORT})")
    parser.add_argument("-v", "--venv", help="Ruta personalizada a la carpeta del entorno virtual")
    parser.add_argument("--no-browser", action="store_true", help="No abrir automáticamente el navegador web")
    parser.add_argument("--no-migrate", action="store_true", help="Omitir la ejecución automática de migraciones")
    parser.add_argument("--strict-port", action="store_true", help="Fallar si el puerto está ocupado en lugar de buscar el siguiente disponible")
    parser.add_argument("--reinstall", action="store_true", help="Forzar reinstalación de requerimientos con pip")
    parser.add_argument("-c", "--check", action="store_true", help="Ejecutar chequeos de integridad de Django")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Validar entorno, rutas y puertos sin iniciar el servidor")
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {VERSION}")

    return parser.parse_args()


def main() -> None:
    Logger.init_colors()
    args = parse_arguments()

    # 1. Validar existencia de manage.py
    if not (BASE_DIR / "manage.py").is_file():
        Logger.error(f"No se encontró 'manage.py' en el directorio '{BASE_DIR}'.")
        sys.exit(1)

    # 2. Asegurar archivo .env antes de cualquier operación Django
    ConfigManager.ensure_env_file()

    # 3. Gestión del Entorno Virtual (Venv Bootstrap)
    if not EnvironmentManager.is_running_in_venv():
        target_py = EnvironmentManager.find_or_create_venv(args.venv)
        EnvironmentManager.ensure_dependencies(target_py, force_reinstall=args.reinstall)

        # Si no estamos dentro del venv, nos re-ejecutamos con el Python del venv
        cmd = [str(target_py), str(Path(__file__).resolve())] + sys.argv[1:]
        try:
            exit_code = subprocess.call(cmd, cwd=str(BASE_DIR))
            sys.exit(exit_code)
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        # Ya estamos dentro del venv
        current_py = Path(sys.executable)
        EnvironmentManager.ensure_dependencies(current_py, force_reinstall=args.reinstall)
        EnvironmentManager.ensure_node_dependencies()

    # 4. Gestión de Puertos y Resolución de Conflictos
    host = args.host
    port = args.port

    if not NetworkManager.is_port_available(host, port):
        if args.strict_port:
            Logger.error(f"El puerto {host}:{port} ya está en uso y se especificó --strict-port.")
            sys.exit(1)
        else:
            free_port = NetworkManager.find_free_port(host, port + 1)
            Logger.warn(f"El puerto {port} está ocupado por otro proceso. Se utilizará automáticamente el puerto libre {free_port}.")
            port = free_port

    django_mgr = DjangoManager(Path(sys.executable))

    # 5. Ejecutar Chequeos de Integridad
    if args.check:
        if not django_mgr.run_check():
            sys.exit(1)

    # 6. Ejecutar Migraciones
    if not args.no_migrate:
        if not django_mgr.run_migrations():
            Logger.warn("Continuando inicio a pesar de advertencia en migraciones.")

    # 7. Modo Dry-Run
    if args.dry_run:
        Logger.success("[DRY-RUN] Entorno validado con éxito. El servidor está 100% listo para operar.")
        Logger.info(f"Host configurado : {host}")
        Logger.info(f"Puerto verificado: {port}")
        sys.exit(0)

    # 8. Iniciar Servidor
    open_browser = not args.no_browser
    exit_code = django_mgr.start_server(host=host, port=port, open_browser=open_browser)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
