import asyncio
from dotenv import load_dotenv
from browser_use import Agent, Tools, ChatOpenAI
from browser_use.agent.views import ActionResult
from pydantic import BaseModel, Field
from typing import Optional

load_dotenv()

# Create custom tools for interaction - EXCLUDE ALL automatic data extraction actions
tools = Tools(exclude_actions=[
    'extract_structured_data', 
    'extract_content',
    'extract_text', 
    'get_structured_content'
])

class ClarifyingQuestion(BaseModel):
    """Parameters for asking clarifying questions"""
    question: str = Field(..., description="The clarifying question to ask the user")
    context: str = Field(..., description="Why this clarification is needed")

class FollowUpCheck(BaseModel):
    """Parameters for checking if user wants to do more tasks"""
    completion_summary: str = Field(..., description="Summary of what was completed")
    suggestions: Optional[str] = Field(None, description="Optional suggestions for next steps")

@tools.action(
    description="Ask the user a clarifying question when the task is vague or ambiguous. Use this when you need more specific information to complete the task effectively.",
    param_model=ClarifyingQuestion
)
def ask_clarifying_question(params: ClarifyingQuestion) -> ActionResult:
    """Ask user for clarification when task is unclear"""
    print(f"\n🤔 I need some clarification:")
    print(f"Context: {params.context}")
    print(f"Question: {params.question}")
    
    user_response = input("\nYour response: ").strip()
    
    if not user_response:
        return ActionResult(
            extracted_content="User provided no response to clarifying question",
            error="No clarification provided"
        )
    
    return ActionResult(
        extracted_content=f"User clarification: {user_response}",
        long_term_memory=f"Clarification received: {params.question} -> {user_response}"
    )

@tools.action(
    description="Ask the user if they want to perform any additional tasks after completing the current one. Use this when a task has been successfully completed.",
    param_model=FollowUpCheck
)
def ask_for_follow_up(params: FollowUpCheck) -> ActionResult:
    """Ask user if they want to do more tasks after completion"""
    print(f"\n✅ Task completed successfully!")
    print(f"Summary: {params.completion_summary}")
    
    if params.suggestions:
        print(f"Suggestions: {params.suggestions}")
    
    print(f"\n❓ Is there anything else you'd like me to help you with?")
    user_response = input("Your response (or 'no' to finish): ").strip()
    
    if user_response.lower() in ['no', 'n', 'nothing', 'done', 'finished', 'exit', 'quit']:
        return ActionResult(
            extracted_content="User indicated no more tasks needed",
            is_done=True,
            success=True
        )
    elif user_response:
        return ActionResult(
            extracted_content=f"New task requested: {user_response}",
            long_term_memory=f"Follow-up task: {user_response}"
        )
    else:
        return ActionResult(
            extracted_content="User provided no response to follow-up question",
            is_done=True,
            success=True
        )

@tools.action(
    description="Ask what to do next when you've navigated to a page but the next action is unclear",
)
def ask_next_action(current_page: str, available_options: str) -> ActionResult:
    """Ask user what to do next on the current page"""
    print(f"\n📍 I'm currently on: {current_page}")
    print(f"Available options: {available_options}")
    print(f"\n❓ What would you like me to do next?")
    
    user_response = input("Your response: ").strip()
    
    if not user_response:
        return ActionResult(
            extracted_content="User provided no response for next action",
            error="No next action specified"
        )
    
    return ActionResult(
        extracted_content=f"User wants next action: {user_response}",
        long_term_memory=f"Next action on {current_page}: {user_response}"
    )

# Enhanced system message for better interaction
ENHANCED_SYSTEM_MESSAGE = """
You are a helpful browser automation agent with specialized communication skills:

CRITICAL ANTI-EXTRACTION RULES:
- NEVER automatically extract data unless explicitly asked to do so
- Do NOT use extract_structured_data, extract_content, or similar actions without explicit request
- Focus on NAVIGATION and INTERACTION, not data scraping
- After completing navigation/interaction, ask the user what they want to do next

CLARIFICATION GUIDELINES:
- When a task is vague, ambiguous, or lacks specific details, use the 'ask_clarifying_question' action
- Ask specific questions about:
  * Which website to visit if not specified
  * What specific information to look for
  * What actions to take with found information
  * How to handle multiple options or results
- Examples of vague tasks that need clarification:
  * "Search for something" -> Ask what to search for and where
  * "Find information" -> Ask what specific information and from which source
  * "Check prices" -> Ask for which products and on which websites
  * "Search for cat videos" -> Ask which platform (YouTube, TikTok, etc.) and what to do after finding them

COMPLETION GUIDELINES:
- After successfully completing any task, always use the 'ask_for_follow_up' action
- Provide a clear summary of what was accomplished
- Suggest logical next steps when appropriate
- DO NOT automatically extract detailed data unless specifically requested
- Focus on navigation and basic interactions, then ask what the user wants to do next
- Examples of good completion summaries:
  * "I navigated to Apple's website and found the iPhone section - would you like me to extract pricing information?"
  * "I successfully logged into your account and see the messages page - what would you like me to do with the messages?"

INTERACTION STYLE:
- Be proactive in asking for clarification rather than making assumptions
- Be conversational and helpful
- Provide context for why you need clarification
- Always check if the user wants to do more after completing a task
- When you reach a page (like YouTube search results), ask what specific action to take next
- STOP and ASK rather than automatically continuing with data extraction
"""

async def create_clarifying_agent(task: str):
    """Create an agent that asks clarifying questions and follow-ups"""
    
    llm = ChatOpenAI(model="gpt-4.1-mini")
    
    agent = Agent(
        task=task,
        llm=llm,
        tools=tools,
        extend_system_message=ENHANCED_SYSTEM_MESSAGE,
        max_actions_per_step=3,  # Reduced to prevent too many actions at once
        use_thinking=True,
        # Additional controls to prevent automatic behavior
        use_vision=True,
        final_response_after_failure=True
    )
    
    return agent

async def run_interactive_session():
    """Run an interactive session with the clarifying agent"""
    print("🚀 Browser Agent with Clarifying Questions")
    print("=" * 50)
    
    # Get initial task from user
    initial_task = input("What would you like me to help you with? ").strip()
    
    if not initial_task:
        print("Please provide a task to get started.")
        return
    
    # Create and run agent
    agent = await create_clarifying_agent(initial_task)
    
    try:
        while True:
            print(f"\n🎯 Current task: {agent.task}")
            print("-" * 30)
            
            # Run the agent
            history = await agent.run(max_steps=20)
            
            # Check if we got a follow-up task
            if history.is_done():
                print("\n👋 Session completed. Goodbye!")
                break
            
            # Look for new tasks in the history
            last_result = history.final_result()
            if last_result and "New task requested:" in str(last_result):
                # Extract the new task
                new_task = str(last_result).replace("New task requested:", "").strip()
                print(f"\n🔄 Starting new task: {new_task}")
                agent.add_new_task(new_task)
            else:
                break
                
    except KeyboardInterrupt:
        print("\n\n⏹️ Session interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

# Example usage functions
async def example_vague_task():
    """Example with a vague task that should trigger clarifying questions"""
    agent = await create_clarifying_agent("Find some information online")
    await agent.run()

async def example_specific_task():
    """Example with a specific task that should complete and ask for follow-up"""
    agent = await create_clarifying_agent("Go to google.com and search for 'browser automation python' then take a screenshot")
    await agent.run()

if __name__ == "__main__":
    # Run interactive session
    asyncio.run(run_interactive_session())
    
    # Or run specific examples:
    # asyncio.run(example_vague_task())
    # asyncio.run(example_specific_task())