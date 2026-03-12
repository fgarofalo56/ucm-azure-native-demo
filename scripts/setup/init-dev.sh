#!/usr/bin/env bash
# Local development environment setup script
set -euo pipefail

echo "=== AssuranceNet Development Environment Setup ==="

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Python 3.11+ required"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js 20+ required"; exit 1; }
command -v az >/dev/null 2>&1 || { echo "Azure CLI required"; exit 1; }

# Backend setup
echo ""
echo "--- Setting up Python backend ---"
cd src/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
echo "Backend setup complete. Edit src/backend/.env with your Azure credentials."

# Frontend setup
echo ""
echo "--- Setting up React frontend ---"
cd ../frontend
npm install
echo "Frontend setup complete."

# Return to root
cd ../..

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To run the backend:  cd src/backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "To run the frontend: cd src/frontend && npm run dev"
echo ""
echo "To seed FSIS demo data (after backend is running):"
echo "  ./scripts/setup/seed-data.sh"
echo ""
echo "Demo data includes real FSIS documents from https://www.fsis.usda.gov/science-data:"
echo "  - Annual Sampling Plans (PDF)"
echo "  - National Residue Program reports (PDF)"
echo "  - MPI Establishment Directories (CSV)"
echo "  - Sampling Summary Reports (PDF)"
echo ""
echo "Remember to:"
echo "  1. Configure src/backend/.env with Azure credentials"
echo "  2. Run 'az login' for Azure authentication"
echo "  3. Set up Entra ID app registrations for auth"
echo ""
echo "Documentation: docs/guides/ (user guide, deployment, developer, operations, troubleshooting)"
