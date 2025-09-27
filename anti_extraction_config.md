# Browser-Use Agent Configuration Guide
# How to prevent automatic data extraction and make agent ask for user input

## Key Solutions:

### 1. Exclude Data Extraction Actions
```python
tools = Tools(exclude_actions=[
    'extract_structured_data',
    'extract_content', 
    'extract_text',
    'get_structured_content'
])
```

### 2. Use Custom System Message
Override the system message to explicitly tell the agent NOT to extract data automatically:

```python
ANTI_EXTRACTION_PROMPT = """
CRITICAL: Do NOT automatically extract data unless explicitly requested.
Focus on navigation and interaction only.
After completing navigation, ask the user what they want to do next.
"""

agent = Agent(
    override_system_message=ANTI_EXTRACTION_PROMPT,  # OR extend_system_message
    # ... other params
)
```

### 3. Limit Actions Per Step
```python
agent = Agent(
    max_actions_per_step=3,  # Prevent too many automatic actions
    # ... other params
)
```

### 4. Use Flash Mode (Experimental)
Flash mode is faster and less likely to over-extract:
```python
agent = Agent(
    flash_mode=True,  # Disables thinking and evaluation steps
    # ... other params
)
```

### 5. Create Custom Completion Actions
Force the agent to ask for next steps by creating custom tools that require user input.

### 6. Browser Configuration
```python
browser = Browser(
    wait_between_actions=1.0,  # Slower, more deliberate actions
    highlight_elements=True,   # Visual feedback
    keep_alive=False          # Don't keep browser running
)
```

### 7. Use Specific Task Instructions
Instead of: "Find information about cars"
Use: "Navigate to cars.com and show me the homepage, then ask what I want to do"

## Root Cause:
The default browser-use agent is designed to be autonomous and complete tasks fully.
To make it interactive, you need to:
1. Exclude extraction actions
2. Override system prompts
3. Add custom "ask user" actions
4. Use specific task wording

## Testing Your Setup:
Try these test cases to verify the agent asks instead of auto-extracting:
- "Go to reddit.com" (should navigate and ask what to do next)
- "Find cat videos" (should ask where to look and what to do with results)
- "Check weather" (should ask for location and what weather info is needed)