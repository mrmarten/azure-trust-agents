# Environment Variable Validation Improvements

## Summary

This document describes the improvements made to environment variable validation across the Azure Trust Agents repository. These changes address the issue where users receive cryptic error messages when environment variables are not properly configured.

## Problem Statement

**Before**: Users running the agents without a properly configured `.env` file received unhelpful error messages like:
```
❌ Error creating Compliance Report Agent: (ResourceNotFound) The project does not exist.
Code: ResourceNotFound
Message: The project does not exist.
```

This error was confusing because:
- It doesn't indicate that environment variables are missing
- It doesn't explain how to fix the problem
- It doesn't reference the setup documentation

## Solution

### 1. Created Shared Validation Module

Created `challenge-1/agents/env_validator.py` that provides:

- **Centralized validation logic** for all Python scripts
- **Clear, helpful error messages** that guide users to the solution
- **Two setup options**:
  - **Option A (Recommended)**: Automated setup script (`get-keys.sh`)
  - **Option B (Manual)**: Copy and edit `.env.sample`
- **Pre-defined validation functions** for common use cases:
  - `validate_agent_environment()` - For basic AI Foundry agents
  - `validate_customer_data_agent_environment()` - For agents using Cosmos DB
  - `validate_workflow_environment()` - For workflow orchestrations
  - `validate_environment()` - Generic validation with custom variables

### 2. Updated Error Messages

**After**: Users now see comprehensive error messages:

```
======================================================================
❌ ERROR: Required environment variables are not set
======================================================================

Missing variables:
  - AI_FOUNDRY_PROJECT_ENDPOINT: The Azure AI Foundry project endpoint URL
  - MODEL_DEPLOYMENT_NAME: The name of the deployed model (e.g., gpt-4.1-mini)

----------------------------------------------------------------------
📋 SETUP INSTRUCTIONS:
----------------------------------------------------------------------

1. The .env file does not exist at: /path/to/.env

2. To create it, you have two options:

   Option A (Recommended): Run the automated setup script
   -------------------------------------------------------
   cd challenge-0
   ./get-keys.sh --resource-group YOUR_RESOURCE_GROUP_NAME

   This will automatically fetch keys from Azure and create the .env file.

   Option B (Manual): Copy and edit the sample file
   --------------------------------------------------
   cp .env.sample .env
   # Then edit .env and fill in your Azure resource values

----------------------------------------------------------------------
📖 For more information, see: challenge-0/readme.md
======================================================================
```

## Files Modified

### Challenge 1 - Core Agents and Workflows
- ✅ `challenge-1/agents/compliance_report_agent.py`
- ✅ `challenge-1/agents/customer_data_agent.py`
- ✅ `challenge-1/agents/risk_analyser_agent.py`
- ✅ `challenge-1/workflow/sequential_workflow.py`
- ✅ `challenge-1/agents/env_validator.py` (new shared module)

### Challenge 2 - MCP Integration
- ✅ `challenge-2/agents/fraud_alert_foundry_agent.py`
- ✅ `challenge-2/agents/solution/fraud_alert_foundry_agent.py`
- ✅ `challenge-2/agents/sequential_workflow_chal2.py`

### Challenge 3 - Observability
- ✅ `challenge-3/workflow_observability.py`

## Benefits

### For Users
1. **Clear guidance** on what's wrong and how to fix it
2. **Reduced setup time** with direct links to setup documentation
3. **Better onboarding experience** for hackathon participants
4. **Consistent error messages** across all scripts

### For Maintainers
1. **Centralized validation logic** makes updates easier
2. **Reduced code duplication** across multiple files
3. **Easier to add new environment variables** as needed
4. **Consistent error handling** across the entire repository

## Testing

All modified files have been tested with missing environment variables to ensure:
- Error messages are displayed correctly
- Users are guided to the appropriate setup documentation
- Validation occurs before attempting to connect to Azure services

## Future Enhancements

Potential improvements for future iterations:
1. Add validation for optional environment variables with warnings
2. Create a validation CLI tool that checks all environment variables at once
3. Add environment variable documentation to each agent's docstring
4. Consider adding runtime validation that re-checks variables after initial load

## Usage Examples

### Using the shared validation module

```python
from env_validator import validate_agent_environment

# For basic agents
validate_agent_environment()

# For custom validation
from env_validator import validate_environment
validate_environment({
    "CUSTOM_VAR": "Description of what this variable does",
    "ANOTHER_VAR": "Another description"
})
```

### Testing validation

To test the validation with missing environment variables:
```bash
# Ensure .env doesn't exist
rm .env

# Run any agent
python challenge-1/agents/compliance_report_agent.py

# You should see the helpful error message
```

## Conclusion

These improvements significantly enhance the user experience by providing clear, actionable error messages when environment variables are missing or misconfigured. The centralized validation module also improves code maintainability and consistency across the repository.
