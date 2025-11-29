"""
Nutrition Agent System - Main Orchestrator

This is the main entry point for the multi-agent nutrition consultation system.
It orchestrates the workflow between all specialized agents.

Workflow:
1. Interview Agent → Gathers user information
2. Analysis Agent → Calculates KBJU requirements
3. Compatibility Agent → Finds matching recipes
4. Recipe Generator → Creates personalized meal plans
"""

import asyncio
from typing import Dict
from dotenv import load_dotenv

# Load environment variables FIRST, before other imports
# This ensures GOOGLE_API_KEY is available when modules are imported
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import the unified consultation agent
from agents.unified_consultation_agent import unified_consultation_agent


class NutritionOrchestrator:
    """
    Main orchestrator for the nutrition consultation system.

    This class provides a simple interface to the unified consultation agent,
    which automatically runs through the entire workflow.
    """

    def __init__(self):
        """Initialize the orchestrator with the unified agent."""
        # Create shared session service
        self.session_service = InMemorySessionService()
        self.app_name = "nutrition-agent"

        # Create a single runner with the unified consultation agent
        # This agent has all tools and runs the complete workflow automatically
        self.runner = Runner(
            agent=unified_consultation_agent,
            app_name=self.app_name,
            session_service=self.session_service
        )


    async def run_full_consultation(self, user_id: str) -> Dict:
        """
        Run a complete nutrition consultation workflow (automated mode).

        NOTE: This mode is not fully interactive. For best results, use interactive mode.
        In automated mode, agents will use their default prompts to gather information.

        Args:
            user_id: Unique user identifier

        Returns:
            Dictionary containing consultation results
        """
        print(f"\n{'='*60}")
        print("⚠️  AUTOMATED MODE - LIMITED FUNCTIONALITY")
        print(f"{'='*60}")
        print("\nNOTE: Automated mode is not fully implemented.")
        print("For full agent-to-agent communication, please use Interactive Mode (option 2).")
        print(f"\n{'='*60}\n")

        return {
            "status": "not_implemented",
            "message": "Please use Interactive Mode (option 2) for full functionality"
        }

    async def run_interactive_mode(self, user_id: str):
        """
        Run in interactive mode where user can chat with the orchestrator.

        The root orchestrator automatically manages the workflow and delegates
        to sub-agents as needed. No manual stage switching required!

        Args:
            user_id: User identifier
        """
        # Create a single shared session
        shared_session_id = f"consultation_{user_id}"

        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=shared_session_id
        )

        print(f"\n{'='*60}")
        print("🥗 NUTRITION CONSULTATION SYSTEM")
        print(f"{'='*60}")
        print(f"User: {user_id} | Session: {session.id}")
        print(f"\n{'='*60}")
        print("The AI consultant will guide you through:")
        print("  1️⃣  Interview - Collect your information")
        print("  2️⃣  Analysis - Calculate nutrition targets")
        print("  3️⃣  Compatibility - Find matching recipes")
        print("  4️⃣  Meal Plan - Generate personalized plan")
        print(f"\n💡 The agent automatically moves between stages!")
        print(f"{'='*60}\n")
        print("Commands:")
        print("  'exit' - End consultation")
        print("  'status' - Check session data")
        print(f"\n{'='*60}")
        print("ℹ️  Note: 'Warning' messages from the ADK library are normal")
        print("    and can be safely ignored. They're just informational.")
        print(f"{'='*60}\n")

        while True:
            user_input = input(f"\nYou: ")

            if user_input.lower() == 'exit':
                print("\n👋 Thank you for using the Nutrition Consultation System. Goodbye!\n")
                break
            elif user_input.lower() == 'status':
                # Show session state data
                current_session = await self.session_service.get_session(
                    app_name=self.app_name,
                    session_id=session.id
                )
                print(f"\n📊 Session State:")
                print(f"   Keys stored: {list(current_session.state.keys())}")
                if "user_profile" in current_session.state:
                    print(f"   ✅ User profile collected")
                if "kbju_calculation" in current_session.state:
                    print(f"   ✅ KBJU calculated")
                print()
                continue

            # Send message to the root orchestrator
            message = types.Content(
                role="user",
                parts=[types.Part(text=user_input)]
            )

            print()
            try:
                async for event in self.runner.run_async(
                    user_id=user_id,
                    session_id=session.id,
                    new_message=message
                ):
                    # Safety check: ensure event exists and has content
                    if not event:
                        continue
                    if not hasattr(event, 'content') or event.content is None:
                        continue
                    if not hasattr(event.content, 'parts') or event.content.parts is None:
                        continue

                    # Process all parts - use try-except for extra safety
                    try:
                        for part in event.content.parts:
                            # Display text responses from the agent
                            if part.text and part.text != "None" and part.text.strip():
                                # Clean up any duplicate quoted text
                                text = part.text.strip()
                                # Remove quotes around standalone sentences at the end
                                if '\n"' in text or '"\n' in text:
                                    # Remove quoted duplicate text
                                    lines = text.split('\n')
                                    cleaned_lines = [line for line in lines if not (line.startswith('"') and line.endswith('"'))]
                                    text = '\n'.join(cleaned_lines).strip()

                                print(f"\n🤖 Consultant: {text}\n")

                            # Display when agent calls a tool
                            elif part.function_call:
                                func_name = part.function_call.name
                                # Clean up tool names for display
                                tool_name = func_name.replace('_', ' ').title()
                                print(f"\n   🔧 Using tool: {tool_name}", end='', flush=True)

                            # Display tool responses
                            elif part.function_response:
                                func_name = part.function_response.name
                                response_data = part.function_response.response

                                # Handle tool responses
                                if isinstance(response_data, dict):
                                    # Check if it's a standard tool response (has 'status')
                                    if 'status' in response_data:
                                        status = response_data.get('status', 'unknown')
                                        if status == 'success':
                                            print(f" → ✅")
                                            # Show summary if available
                                            if 'summary' in response_data:
                                                print(f"      💡 {response_data['summary']}")
                                        elif status == 'error':
                                            error_msg = response_data.get('error_message', 'Unknown error')
                                            print(f" → ❌")
                                            print(f"      Error: {error_msg}")
                                    else:
                                        # Other dict format - just show it completed
                                        print(f" → ✅")

                    except Exception as inner_e:
                        # Error processing a specific event part
                        print(f"⚠️  Skipped malformed event part: {inner_e}")
                        continue

            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                print("The orchestrator will try to continue. You can keep chatting or type 'exit' to quit.")
            print()


async def main():
    """Main entry point for the nutrition agent system."""
    # Initialize orchestrator
    orchestrator = NutritionOrchestrator()

    print("\n" + "="*60)
    print("🥗 NUTRITION AGENT SYSTEM")
    print("="*60 + "\n")

    print("Select mode:")
    print("1. Automated mode (not implemented - use interactive mode)")
    print("2. Interactive mode (RECOMMENDED)")
    print("\nInteractive mode features:")
    print("  ✅ Automatic workflow progression")
    print("  ✅ Chat naturally with the orchestrator")
    print("  ✅ No manual stage switching needed")
    print("  ✅ See all agent activities in real-time")
    choice = input("\nEnter choice (1 or 2): ")

    user_id = "demo_user_001"

    if choice == "1":
        # Run full automated workflow
        results = await orchestrator.run_full_consultation(user_id)
        print(f"\nStatus: {results['status']}")
        if 'message' in results:
            print(f"Message: {results['message']}")

    elif choice == "2":
        # Run interactive mode
        await orchestrator.run_interactive_mode(user_id)

    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    # Run the orchestrator
    asyncio.run(main())