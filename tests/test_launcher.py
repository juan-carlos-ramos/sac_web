#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suite de Pruebas Automatizadas para el Iniciador Maestro iniciar.py
"""

import os
import socket
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Importar módulos de iniciar.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from iniciar import (
    BASE_DIR,
    VERSION,
    ConfigManager,
    DjangoManager,
    EnvironmentManager,
    NetworkManager,
    parse_arguments,
)


class TestLauncher(unittest.TestCase):

    def test_version_and_paths(self):
        """Verifica que la versión y el directorio base estén correctamente definidos."""
        self.assertEqual(VERSION, "3.0.0")
        self.assertTrue(BASE_DIR.is_dir())
        self.assertTrue((BASE_DIR / "manage.py").is_file())

    def test_cli_argument_defaults(self):
        """Verifica valores por defecto de la CLI."""
        with patch.object(sys, 'argv', ['iniciar.py']):
            args = parse_arguments()
            self.assertEqual(args.host, "127.0.0.1")
            self.assertEqual(args.port, 8000)
            self.assertFalse(args.no_browser)
            self.assertFalse(args.no_migrate)
            self.assertFalse(args.dry_run)
            self.assertFalse(args.strict_port)

    def test_cli_custom_arguments(self):
        """Verifica procesamiento de banderas personalizadas."""
        custom_argv = [
            'iniciar.py',
            '--host', '0.0.0.0',
            '--port', '9000',
            '--no-browser',
            '--no-migrate',
            '--strict-port',
            '--dry-run'
        ]
        with patch.object(sys, 'argv', custom_argv):
            args = parse_arguments()
            self.assertEqual(args.host, "0.0.0.0")
            self.assertEqual(args.port, 9000)
            self.assertTrue(args.no_browser)
            self.assertTrue(args.no_migrate)
            self.assertTrue(args.strict_port)
            self.assertTrue(args.dry_run)

    def test_network_port_detection(self):
        """Verifica la detección de puertos libres y ocupados."""
        # Enlazar temporalmente un socket para simular puerto ocupado
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('127.0.0.1', 0))
            _, occupied_port = sock.getsockname()

            # El puerto ocupado no debe estar disponible
            self.assertFalse(NetworkManager.is_port_available('127.0.0.1', occupied_port))

            # find_free_port debe retornar un puerto libre diferente al ocupado si partimos de él
            free_port = NetworkManager.find_free_port('127.0.0.1', occupied_port + 1)
            self.assertNotEqual(free_port, occupied_port)
            self.assertTrue(NetworkManager.is_port_available('127.0.0.1', free_port))

        # Una vez cerrado el bloque with, el puerto vuelve a quedar disponible
        self.assertTrue(NetworkManager.is_port_available('127.0.0.1', occupied_port))

    def test_env_file_verification(self):
        """Verifica que el archivo .env sea validado o generado con SECRET_KEY."""
        ConfigManager.ensure_env_file()
        env_file = BASE_DIR / ".env"
        self.assertTrue(env_file.is_file())
        content = env_file.read_text(encoding='utf-8')
        self.assertIn("SECRET_KEY", content)

    def test_venv_detection(self):
        """Verifica la detección del entorno virtual existente."""
        venv_py = EnvironmentManager.get_venv_python_executable(BASE_DIR / "venv")
        self.assertIsNotNone(venv_py)
        self.assertTrue(venv_py.is_file())

    def test_django_check(self):
        """Verifica que el chequeo de integridad de Django se ejecute con éxito."""
        py_bin = EnvironmentManager.get_venv_python_executable(BASE_DIR / "venv")
        django_mgr = DjangoManager(py_bin)
        self.assertTrue(django_mgr.run_check())


if __name__ == "__main__":
    unittest.main()
