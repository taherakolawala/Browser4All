import asyncio
import sys
from dotenv import load_dotenv
from browser_use import Agent, Tools, ChatOpenAI, Browser, ChatGoogle
from browser_use.agent.views import ActionResult
from pydantic import BaseModel, Field
from typing import Optional
from speech_handler import speak_text, speak_text_sync, configure_speech, get_user_input_with_voice
from hovering_ui import initialize_ui, shutdown_ui, add_ui_message
from language_utils import initialize_language_manager, get_text, set_language, get_available_languages
import atexit

load_dotenv()

# Language Configuration
# Detect language from command line args or auto-detect
LANGUAGE = 'auto'  # Options: 'auto', 'en', 'es', 'fr', 'de', 'zh'
if '--language' in sys.argv:
    lang_index = sys.argv.index('--language') + 1
    if lang_index < len(sys.argv):
        LANGUAGE = sys.argv[lang_index]

# Initialize language manager
if LANGUAGE == 'auto':
    language_manager = initialize_language_manager()  # Auto-detect
else:
    language_manager = initialize_language_manager(LANGUAGE)

print(f"🌍 Language: {language_manager.get_language_config()['name']} ({language_manager.current_language})")

# Initialize the hovering UI with language support
initialize_ui(width=500, height=400, opacity=0.88, language=language_manager.current_language)

# Register cleanup function
atexit.register(shutdown_ui)

# Configure speech settings
configure_speech(
    enabled=True,
    speak_questions=True,
    speak_confirmations=True,
    speak_errors=False,
    listen_for_responses=True,  # Enable voice input
    offer_voice_input=True,    # Show voice input options
    voice_input_default=True,  # Make voice input the default mode
    recognition_timeout=10,    # 10 second timeout for voice input
    debug_audio=False,          # Enable audio debugging (hear what was recorded)
    language=language_manager.current_language  # Use detected/selected language
)

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
    print(f"\n🤔 {get_text('agent.clarification_needed')}")
    print(f"{get_text('agent.context_prefix')} {params.context}")
    print(f"{get_text('agent.question_prefix')} {params.question}")
    
    # Speak the question naturally (synchronous to avoid event loop issues)
    question_speech = f"{get_text('agent.clarification_needed')} {params.context}. {params.question}"
    print(f"\n{get_text('agent.speaking_question')}")
    speak_text_sync(question_speech)
    
    user_response = get_user_input_with_voice(
        prompt=f"\n{get_text('voice.text_input_prompt')}",
        voice_prompt=get_text('voice.respond_to', question=params.question)
    )
    
    if not user_response:
        return ActionResult(
            extracted_content=get_text('agent.no_clarification'),
            error="No clarification provided"
        )
    
    # Don't speak back the user's response - they just said it
    print(get_text('agent.received_response', response=user_response))
    
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
    print(f"\n{get_text('agent.task_completed')}")
    print(f"{get_text('agent.summary_prefix')} {params.completion_summary}")
    
    if params.suggestions:
        print(f"{get_text('agent.suggestions_prefix')} {params.suggestions}")
    
    print(f"\n{get_text('agent.anything_else')}")
    
    # Speak the completion and question
    completion_speech = f"{get_text('agent.task_completed')} {params.completion_summary}. "
    if params.suggestions:
        completion_speech += f"{get_text('agent.suggestions_prefix')} {params.suggestions}. "
    completion_speech += get_text('agent.anything_else')
    
    print(f"\n{get_text('agent.speaking_completion')}")
    speak_text_sync(completion_speech)
    
    user_response = get_user_input_with_voice(
        prompt=get_text('voice.text_input_finish'),
        voice_prompt=get_text('voice.anything_else_prompt')
    )
    
    if user_response.lower() in ['no', 'n', 'nothing', 'done', 'finished', 'exit', 'quit']:
        # Don't speak back their "no" response
        print(get_text('agent.received_response', response=user_response))
        return ActionResult(
            extracted_content=get_text('agent.no_more_tasks'),
            is_done=True,
            success=True
        )
    elif user_response:
        # Don't speak back their new task request - they just said it
        print(get_text('agent.received_response', response=user_response))
        return ActionResult(
            extracted_content=f"New task requested: {user_response}",
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
    print(f"\n{get_text('agent.currently_on', page=current_page)}")
    print(get_text('agent.available_options', options=available_options))
    print(f"\n{get_text('agent.what_next')}")
    
    # Speak the current status and question
    status_speech = f"{get_text('agent.currently_on', page=current_page)} {get_text('agent.available_options', options=available_options)} {get_text('agent.what_next')}"
    print(f"\n{get_text('agent.speaking_status')}")
    speak_text_sync(status_speech)
    
    user_response = get_user_input_with_voice(
        prompt=get_text('voice.text_input_prompt'),
        voice_prompt=get_text('voice.what_next_prompt')
    )
    
    if not user_response:
        return ActionResult(
            extracted_content=get_text('agent.no_next_action'),
            error="No next action specified"
        )
    
    # Don't speak back the user's response - they just said it
    print(get_text('agent.next_action', action=user_response))
    
    return ActionResult(
        extracted_content=f"User wants next action: {user_response}",
        long_term_memory=f"Next action on {current_page}: {user_response}"
    )

# Multilingual system messages
SYSTEM_MESSAGES = {
    'en': """
You are a helpful browser automation agent with specialized communication skills:

LANGUAGE INSTRUCTION: COMMUNICATE ONLY IN ENGLISH. All your questions, responses, and explanations must be in English.

CRITICAL ANTI-EXTRACTION RULES:
- NEVER automatically extract data unless explicitly asked to do so
- Do NOT use extract_structured_data, extract_content, or similar actions without explicit request
- Focus on NAVIGATION and INTERACTION, not data scraping
- After completing navigation/interaction, ask the user what they want to do next

CLARIFICATION GUIDELINES:
- When a task is vague, ambiguous, or lacks specific details, use the 'ask_clarifying_question' action
- Ask specific questions about which website to visit, what information to look for, what actions to take
- Examples: "Search for something" -> Ask what and where; "Find information" -> Ask what specific information

COMPLETION GUIDELINES:
- After successfully completing any task, always use the 'ask_for_follow_up' action
- Provide clear summaries and suggest logical next steps
- STOP and ASK rather than automatically continuing with data extraction

INTERACTION STYLE:
- Be proactive in asking for clarification rather than making assumptions
- Be conversational and helpful
- Always check if the user wants to do more after completing a task
""",
    'es': """
Eres un agente útil de automatización de navegador con habilidades de comunicación especializadas:

INSTRUCCIÓN DE IDIOMA: COMUNÍCATE SOLO EN ESPAÑOL. Todas tus preguntas, respuestas y explicaciones deben estar en español.

REGLAS CRÍTICAS ANTI-EXTRACCIÓN:
- NUNCA extraigas datos automáticamente a menos que se te pida explícitamente
- NO uses extract_structured_data, extract_content, u acciones similares sin solicitud explícita
- Enfócate en NAVEGACIÓN e INTERACCIÓN, no en extracción de datos
- Después de completar navegación/interacción, pregunta al usuario qué quiere hacer a continuación

PAUTAS DE ACLARACIÓN:
- Cuando una tarea sea vaga o ambigua, usa la acción 'ask_clarifying_question'
- Haz preguntas específicas sobre qué sitio web visitar, qué información buscar, qué acciones tomar
- Ejemplos: "Buscar algo" -> Pregunta qué y dónde; "Encontrar información" -> Pregunta qué información específica

PAUTAS DE FINALIZACIÓN:
- Después de completar exitosamente cualquier tarea, siempre usa la acción 'ask_for_follow_up'
- Proporciona resúmenes claros y sugiere próximos pasos lógicos
- DETENTE y PREGUNTA en lugar de continuar automáticamente con extracción de datos

ESTILO DE INTERACCIÓN:
- Sé proactivo pidiendo aclaraciones en lugar de hacer suposiciones
- Sé conversacional y útil
- Siempre verifica si el usuario quiere hacer más después de completar una tarea
""",
    'fr': """
Vous êtes un agent d'automatisation de navigateur utile avec des compétences de communication spécialisées:

INSTRUCTION LINGUISTIQUE: COMMUNIQUEZ UNIQUEMENT EN FRANÇAIS. Toutes vos questions, réponses et explications doivent être en français.

RÈGLES CRITIQUES ANTI-EXTRACTION:
- Ne JAMAIS extraire de données automatiquement sauf si explicitement demandé
- N'utilisez PAS extract_structured_data, extract_content, ou actions similaires sans demande explicite
- Concentrez-vous sur la NAVIGATION et l'INTERACTION, pas sur l'extraction de données
- Après avoir terminé navigation/interaction, demandez à l'utilisateur ce qu'il veut faire ensuite

DIRECTIVES DE CLARIFICATION:
- Quand une tâche est vague ou ambiguë, utilisez l'action 'ask_clarifying_question'
- Posez des questions spécifiques sur quel site web visiter, quelles informations chercher, quelles actions prendre
- Exemples: "Chercher quelque chose" -> Demandez quoi et où; "Trouver des informations" -> Demandez quelles informations spécifiques

DIRECTIVES DE FINALISATION:
- Après avoir terminé avec succès une tâche, utilisez toujours l'action 'ask_for_follow_up'
- Fournissez des résumés clairs et suggérez les prochaines étapes logiques
- ARRÊTEZ et DEMANDEZ plutôt que de continuer automatiquement avec l'extraction de données

STYLE D'INTERACTION:
- Soyez proactif en demandant des clarifications plutôt que de faire des suppositions
- Soyez conversationnel et utile
- Vérifiez toujours si l'utilisateur veut en faire plus après avoir terminé une tâche
""",
    'de': """
Sie sind ein hilfreicher Browser-Automatisierungsagent mit speziellen Kommunikationsfähigkeiten:

SPRACHLICHE ANWEISUNG: KOMMUNIZIEREN SIE NUR AUF DEUTSCH. Alle Ihre Fragen, Antworten und Erklärungen müssen auf Deutsch sein.

KRITISCHE ANTI-EXTRAKTIONS-REGELN:
- Extrahieren Sie NIEMALS automatisch Daten, es sei denn, dies wird explizit verlangt
- Verwenden Sie NICHT extract_structured_data, extract_content oder ähnliche Aktionen ohne explizite Anfrage
- Konzentrieren Sie sich auf NAVIGATION und INTERAKTION, nicht auf Datenextraktion
- Nach Abschluss von Navigation/Interaktion fragen Sie den Benutzer, was er als nächstes tun möchte

KLARSTELLUNGSRICHTLINIEN:
- Wenn eine Aufgabe vage oder mehrdeutig ist, verwenden Sie die Aktion 'ask_clarifying_question'
- Stellen Sie spezifische Fragen über welche Website zu besuchen, welche Informationen zu suchen, welche Aktionen zu unternehmen
- Beispiele: "Etwas suchen" -> Fragen was und wo; "Informationen finden" -> Fragen welche spezifischen Informationen

ABSCHLUSSRICHTLINIEN:
- Nach erfolgreichem Abschluss einer Aufgabe verwenden Sie immer die Aktion 'ask_for_follow_up'
- Geben Sie klare Zusammenfassungen und schlagen logische nächste Schritte vor
- STOPPEN und FRAGEN Sie anstatt automatisch mit Datenextraktion fortzufahren

INTERAKTIONSSTIL:
- Seien Sie proaktiv beim Nachfragen nach Klarstellungen anstatt Annahmen zu treffen
- Seien Sie gesprächig und hilfsbereit
- Überprüfen Sie immer, ob der Benutzer nach Abschluss einer Aufgabe mehr tun möchte
""",
    'zh': """
您是一个有用的浏览器自动化助手，具有专业的沟通技能：

语言指令：仅使用中文交流。您的所有问题、回答和解释都必须使用中文。

关键反提取规则：
- 除非明确要求，否则绝不自动提取数据
- 不要在没有明确请求的情况下使用extract_structured_data、extract_content或类似操作
- 专注于导航和交互，而不是数据抓取
- 完成导航/交互后，询问用户接下来想做什么

澄清指南：
- 当任务模糊或不明确时，使用'ask_clarifying_question'操作
- 询问具体问题：访问哪个网站、寻找什么信息、采取什么行动
- 示例："搜索某些内容"→询问搜索什么和在哪里；"查找信息"→询问什么具体信息

完成指南：
- 成功完成任何任务后，始终使用'ask_for_follow_up'操作
- 提供清晰的摘要并建议合理的后续步骤
- 停止并询问而不是自动继续数据提取

交互风格：
- 主动寻求澄清而不是做假设
- 对话式且有帮助
- 完成任务后始终检查用户是否想要做更多事情
"""
}

def get_system_message(language: str = 'en') -> str:
    """Get system message for the specified language"""
    return SYSTEM_MESSAGES.get(language, SYSTEM_MESSAGES['en'])

async def create_clarifying_agent(task: str, language: str = None):
    """Create an agent that asks clarifying questions and follow-ups"""
    
    llm = ChatOpenAI(model='gpt-4.1-mini')
    
    browser = Browser(
        window_size={'width': 1920, 'height': 1080},
        headless=False
    )

    # Get appropriate system message for language
    current_language = language or language_manager.current_language
    system_message = get_system_message(current_language)

    agent = Agent(
        task=task,
        browser=browser,
        llm=llm,
        tools=tools,
        extend_system_message=system_message,
        max_actions_per_step=3,  # Reduced to prevent too many actions at once
        use_thinking=True,
        # Additional controls to prevent automatic behavior
        use_vision=True,
        final_response_after_failure=True
    )
    
    return agent

async def run_interactive_session():
    """Run an interactive session with the clarifying agent"""
    print(get_text("agent.session_separator"))
    print(get_text("agent.session_separator"))
    
    # Speak greeting
    greeting = get_text("agent.greeting")
    await speak_text(greeting)
    
    # Get initial task from user
    initial_task = get_user_input_with_voice(
        prompt=get_text('voice.text_input_prompt'),
        voice_prompt=get_text('voice.prompt_help')
    )
    
    if not initial_task:
        print(get_text("agent.no_response"))
        return
    
    # Don't speak back the user's task - they just said it
    print(get_text("agent.task_received", task=initial_task))
    
    # Create and run agent
    agent = await create_clarifying_agent(initial_task, language_manager.current_language)
    
    try:
        while True:
            print(f"\n{get_text('agent.current_task', task=agent.task)}")
            print("-" * 30)
            
            # Run the agent
            history = await agent.run(max_steps=20)
            
            # Check if we got a follow-up task
            if history.is_done():
                print(f"\n{get_text('ui.session_completed')}")
                await speak_text(get_text('ui.session_completed'))
                break
            
            # Look for new tasks in the history
            last_result = history.final_result()
            if last_result and "New task requested:" in str(last_result):
                # Extract the new task
                new_task = str(last_result).replace("New task requested:", "").strip()
                print(get_text('agent.new_task', task=new_task))
                agent.add_new_task(new_task)
            else:
                break
                
    except KeyboardInterrupt:
        print(f"\n\n{get_text('ui.interrupted')}")
    except Exception as e:
        print(f"\n{get_text('ui.error_occurred', error=str(e))}")
    finally:
        # Ensure UI cleanup
        shutdown_ui()

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
    try:
        # Run interactive session
        asyncio.run(run_interactive_session())
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        shutdown_ui()
    except Exception as e:
        print(f"Error: {e}")
        shutdown_ui()
    
    # Or run specific examples:
    # asyncio.run(example_vague_task())
    # asyncio.run(example_specific_task())