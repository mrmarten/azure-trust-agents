import asyncio
import os
import sys
import importlib.util
from pathlib import Path
from typing import Annotated
from azure.identity.aio import AzureCliCredential
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import ConnectionType
from pydantic import Field
from dotenv import load_dotenv

load_dotenv(override=True)

def validate_environment():
    """Validate that required environment variables are set."""
    required_vars = {
        "AI_FOUNDRY_PROJECT_ENDPOINT": "The Azure AI Foundry project endpoint URL",
        "MODEL_DEPLOYMENT_NAME": "The name of the deployed model (e.g., gpt-4.1-mini)"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing_vars.append(f"  - {var}: {description}")
    
    if missing_vars:
        print("\n" + "="*70)
        print("❌ ERROR: Required environment variables are not set")
        print("="*70)
        print("\nMissing variables:")
        for var in missing_vars:
            print(var)
        
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_sample = Path(__file__).parent.parent.parent / ".env.sample"
        
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
        sys.exit(1)

# Validate environment before proceeding
validate_environment()

# Configuration
project_endpoint = os.environ.get("AI_FOUNDRY_PROJECT_ENDPOINT")
model_deployment_name = os.environ.get("MODEL_DEPLOYMENT_NAME")
sc_connection_id = os.environ.get("AZURE_AI_CONNECTION_ID")

async def main():
    try:
        async with AzureCliCredential() as credential:
            async with AIProjectClient(
                endpoint=project_endpoint,
                credential=credential
            ) as project_client:

                # Get Azure AI Search connection ID
                ai_search_conn_id = ""
                async for connection in project_client.connections.list():
                    if connection.type == ConnectionType.AZURE_AI_SEARCH:
                        ai_search_conn_id = connection.id
                        break

                if not ai_search_conn_id:
                    raise ValueError("Azure AI Search connection not found in project")

                # Create persistent agent
                created_agent = await project_client.agents.create_agent(
                    model=model_deployment_name,
                    name="RiskAnalyserAgent",
                    instructions="""You are a Risk Analyser Agent evaluating financial transactions for potential fraud.
                    Given a normalized transaction and customer profile, your task is to:
                    - Apply fraud detection logic using rule-based checks and regulatory compliance data
                    - Assign a fraud risk score from 0 to 100
                    - Generate human-readable reasoning behind the score (e.g., "Transaction from unusual country", "High amount", "Previous fraud history")

                You have access to the following tools:
                - Azure AI Search: Search regulations and policies for compliance checking and fraud detection rules

                Please also consider these risk factors:
                {
                "high_risk_countries": ["NG", "IR", "RU", "KP"],
                "high_amount_threshold_usd": 10000,
                "suspicious_account_age_days": 30,
                "low_device_trust_threshold": 0.5
                }

                    Use the Azure AI Search to look up relevant regulations, compliance rules, and fraud detection patterns that apply to the transaction.

                    Output should be:
                    - risk_score: integer (0-100)
                    - risk_level: [Low, Medium, High]
                    - reason: a brief explainable summary with references to relevant regulations or policies found via search""",
                    tools=[{"type": "azure_ai_search"}],
                    tool_resources={
                        "azure_ai_search": {
                            "indexes": [{
                                "index_connection_id": ai_search_conn_id,
                                "index_name": "regulations-policies",
                                "query_type": "simple"
                            }]
                        }
                    }
                )
                
                # Wrap agent with tools for usage
                agent = ChatAgent(
                    chat_client=AzureAIAgentClient(
                        project_client=project_client,
                        agent_id=created_agent.id
                    ),
                    store=True
                )

                # Test the agent with a simple query
                print("\n🧪 Testing the agent with a sample query...")
                try:
                    result = await agent.run("Hello, tell me about the main KYC regulations I should consider for fraud detection?")
                    print(f"✅ Agent response: {result.text}")
                except Exception as test_error:
                    print(f"⚠️  Agent test failed (but agent was still created): {test_error}")

                return agent
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        print("Make sure you have run 'az login' and have proper Azure credentials configured.")
        return None

if __name__ == "__main__":
    asyncio.run(main())

