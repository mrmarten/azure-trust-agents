"""
Environment variable validation utility for Azure Trust Agents.

This module provides validation for required environment variables and 
helpful error messages to guide users through the setup process.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict


def validate_environment(required_vars: Dict[str, str], repo_root: Path = None) -> None:
    """
    Validate that required environment variables are set.
    
    Args:
        required_vars: Dictionary mapping variable names to their descriptions
        repo_root: Optional path to repository root (auto-detected if not provided)
    
    Raises:
        SystemExit: If any required variables are missing
    """
    if repo_root is None:
        # Auto-detect repository root (3 levels up from this file)
        repo_root = Path(__file__).parent.parent.parent
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing_vars.append(f"  - {var}: {description}")
    
    if missing_vars:
        _print_error_message(missing_vars, repo_root)
        sys.exit(1)


def _print_error_message(missing_vars: List[str], repo_root: Path) -> None:
    """Print a helpful error message about missing environment variables."""
    print("\n" + "="*70)
    print("❌ ERROR: Required environment variables are not set")
    print("="*70)
    print("\nMissing variables:")
    for var in missing_vars:
        print(var)
    
    env_file = repo_root / ".env"
    env_sample = repo_root / ".env.sample"
    
    print("\n" + "-"*70)
    print("📋 SETUP INSTRUCTIONS:")
    print("-"*70)
    
    if not env_file.exists():
        print(f"\n1. The .env file does not exist at: {env_file}")
        print("\n2. To create it, you have two options:")
        print("\n   Option A (Recommended): Run the automated setup script")
        print("   -------------------------------------------------------")
        print("   cd challenge-0")
        print("   ./get-keys.sh --resource-group YOUR_RESOURCE_GROUP_NAME")
        print("\n   This will automatically fetch keys from Azure and create the .env file.")
        
        if env_sample.exists():
            print("\n   Option B (Manual): Copy and edit the sample file")
            print("   --------------------------------------------------")
            print(f"   cp {env_sample} {env_file}")
            print(f"   # Then edit {env_file} and fill in your Azure resource values")
    else:
        print(f"\n1. The .env file exists at: {env_file}")
        print("\n2. However, it's missing required variables. Please add them:")
        print("\n   You can:")
        print("   - Re-run: cd challenge-0 && ./get-keys.sh --resource-group YOUR_RESOURCE_GROUP_NAME")
        print("   - Or manually add the missing variables to your .env file")
    
    print("\n" + "-"*70)
    print("📖 For more information, see: challenge-0/readme.md")
    print("="*70 + "\n")


# Common environment variable sets for different use cases
COMMON_ENV_VARS = {
    "AI_FOUNDRY_PROJECT_ENDPOINT": "The Azure AI Foundry project endpoint URL",
    "MODEL_DEPLOYMENT_NAME": "The name of the deployed model (e.g., gpt-4.1-mini)"
}

COSMOS_ENV_VARS = {
    "COSMOS_ENDPOINT": "The Azure Cosmos DB endpoint URL",
    "COSMOS_KEY": "The Azure Cosmos DB primary key"
}


def validate_agent_environment() -> None:
    """Validate environment variables required for AI Foundry agents."""
    validate_environment(COMMON_ENV_VARS)


def validate_customer_data_agent_environment() -> None:
    """Validate environment variables required for Customer Data Agent."""
    validate_environment({**COMMON_ENV_VARS, **COSMOS_ENV_VARS})


def validate_workflow_environment() -> None:
    """Validate environment variables required for workflows."""
    validate_environment({**COMMON_ENV_VARS, **COSMOS_ENV_VARS})
