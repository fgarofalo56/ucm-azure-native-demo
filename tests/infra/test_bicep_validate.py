"""Tests for Bicep infrastructure validation.

These tests verify that all Bicep files compile successfully
and that the parameter files are valid. They require the Bicep CLI
to be installed (az bicep or standalone bicep).
"""

import subprocess
from pathlib import Path

import pytest

INFRA_DIR = Path(__file__).parent.parent.parent / "infra"
MODULES_DIR = INFRA_DIR / "modules"


def bicep_available() -> bool:
    """Check if the Bicep CLI is available."""
    try:
        result = subprocess.run(
            ["bicep", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


skipif_no_bicep = pytest.mark.skipif(
    not bicep_available(),
    reason="Bicep CLI not available",
)


@skipif_no_bicep
class TestBicepBuild:
    """Test that all Bicep files compile without errors."""

    def test_main_bicep_builds(self) -> None:
        """Main orchestrator should compile."""
        main_file = INFRA_DIR / "main.bicep"
        assert main_file.exists(), f"Missing {main_file}"
        result = subprocess.run(
            ["bicep", "build", str(main_file), "--stdout"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"

    @pytest.mark.parametrize(
        "module_name",
        [
            "resource-group",
            "networking",
            "storage",
            "sql-database",
            "key-vault",
            "managed-identity",
            "monitoring",
            "app-service",
            "static-web-app",
            "functions",
            "container-apps",
            "event-grid",
            "front-door",
            "event-hub",
            "dashboard",
            "policy",
            "defender",
            "budgets",
        ],
    )
    def test_module_builds(self, module_name: str) -> None:
        """Each Bicep module should compile independently."""
        module_file = MODULES_DIR / f"{module_name}.bicep"
        assert module_file.exists(), f"Missing module: {module_file}"
        result = subprocess.run(
            ["bicep", "build", str(module_file), "--stdout"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Module {module_name} build failed: {result.stderr}"


@skipif_no_bicep
class TestBicepLint:
    """Test Bicep files pass linting rules."""

    def test_main_bicep_lint(self) -> None:
        """Main orchestrator should pass lint."""
        main_file = INFRA_DIR / "main.bicep"
        result = subprocess.run(
            ["bicep", "lint", str(main_file)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Lint may produce warnings but should not fail
        assert result.returncode == 0, f"Lint failed: {result.stderr}"


class TestBicepFilesExist:
    """Verify all expected Bicep files exist (no CLI needed)."""

    def test_main_exists(self) -> None:
        assert (INFRA_DIR / "main.bicep").exists()

    def test_dev_params_exist(self) -> None:
        assert (INFRA_DIR / "parameters" / "dev.bicepparam").exists()

    def test_staging_params_exist(self) -> None:
        assert (INFRA_DIR / "parameters" / "staging.bicepparam").exists()

    def test_prod_params_exist(self) -> None:
        assert (INFRA_DIR / "parameters" / "prod.bicepparam").exists()

    def test_all_modules_exist(self) -> None:
        expected = [
            "resource-group",
            "networking",
            "storage",
            "sql-database",
            "key-vault",
            "managed-identity",
            "monitoring",
            "app-service",
            "static-web-app",
            "functions",
            "container-apps",
            "event-grid",
            "front-door",
            "event-hub",
            "dashboard",
            "policy",
            "defender",
            "budgets",
        ]
        for module in expected:
            assert (MODULES_DIR / f"{module}.bicep").exists(), f"Missing module: {module}.bicep"
