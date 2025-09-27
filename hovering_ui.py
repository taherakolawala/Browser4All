import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import time
from typing import Optional, Callable
import asyncio
from language_utils import get_language_manager, get_text

class HoveringUI:
    """A transparent hovering UI that displays terminal output above the browser"""
    
    def __init__(self, width: int = 400, height: int = 300, opacity: float = 0.85, language: Optional[str] = None):
        self.width = width
        self.height = height
        self.opacity = opacity
        self.root: Optional[tk.Tk] = None
        self.text_widget: Optional[scrolledtext.ScrolledText] = None
        self.message_queue = queue.Queue()
        self.is_running = False
        self.ui_thread: Optional[threading.Thread] = None
        
        # Language support
        self.language_manager = get_language_manager()
        if language:
            self.language_manager.set_language(language)
        
    def start(self):
        """Start the hovering UI in a separate thread"""
        if self.is_running:
            return
            
        self.is_running = True
        self.ui_thread = threading.Thread(target=self._run_ui, daemon=True)
        self.ui_thread.start()
        
        # Give the UI time to initialize
        time.sleep(0.5)
    
    def stop(self):
        """Stop the hovering UI"""
        self.is_running = False
        if self.root:
            self.root.after(0, self.root.quit)
    
    def add_message(self, message: str, message_type: str = "info"):
        """Add a message to be displayed in the UI"""
        if self.is_running:
            self.message_queue.put((message, message_type, time.time()))
    
    def _run_ui(self):
        """Run the UI in the main thread"""
        self.root = tk.Tk()
        self._setup_window()
        self._create_widgets()
        self._start_message_processor()
        
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"UI Error: {e}")
        finally:
            self.is_running = False
    
    def _setup_window(self):
        """Configure the main window"""
        self.root.title(get_text("ui.title"))
        self.root.geometry(f"{self.width}x{self.height}")
        
        # Make window transparent and always on top
        self.root.attributes('-alpha', self.opacity)
        self.root.attributes('-topmost', True)
        
        # Remove window decorations for a cleaner look
        self.root.overrideredirect(True)
        
        # Position window in top-right corner
        screen_width = self.root.winfo_screenwidth()
        x = screen_width - self.width - 20
        y = 20
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
        # Make window draggable
        self._make_draggable()
        
        # Configure styling
        self.root.configure(bg='#1e1e1e')
    
    def _make_draggable(self):
        """Make the window draggable"""
        def start_move(event):
            self.root.x = event.x
            self.root.y = event.y
        
        def on_move(event):
            deltax = event.x - self.root.x
            deltay = event.y - self.root.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")
        
        self.root.bind('<Button-1>', start_move)
        self.root.bind('<B1-Motion>', on_move)
    
    def _create_widgets(self):
        """Create the UI widgets"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1e1e1e', relief='solid', bd=1)
        main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Header with title and controls
        header_frame = tk.Frame(main_frame, bg='#2d2d2d', height=30)
        header_frame.pack(fill='x', padx=1, pady=1)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text=get_text("ui.title"), 
            bg='#2d2d2d', 
            fg='white',
            font=('Segoe UI', 9, 'bold')
        )
        title_label.pack(side='left', padx=10, pady=5)
        
        # Close button
        close_btn = tk.Button(
            header_frame,
            text="×",
            bg='#ff4444',
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            bd=0,
            width=3,
            command=self.stop
        )
        close_btn.pack(side='right', padx=5, pady=2)
        
        # Minimize button
        minimize_btn = tk.Button(
            header_frame,
            text="–",
            bg='#666666',
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            bd=0,
            width=3,
            command=self._toggle_minimize
        )
        minimize_btn.pack(side='right', padx=2, pady=2)
        
        # Text display area
        text_frame = tk.Frame(main_frame, bg='#1e1e1e')
        text_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        self.text_widget = scrolledtext.ScrolledText(
            text_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=('Consolas', 9),
            wrap='word',
            bd=0,
            padx=10,
            pady=5
        )
        self.text_widget.pack(fill='both', expand=True)
        
        # Configure text tags for different message types
        self.text_widget.tag_configure('info', foreground='#ffffff')
        self.text_widget.tag_configure('success', foreground='#4ade80')
        self.text_widget.tag_configure('warning', foreground='#fbbf24')
        self.text_widget.tag_configure('error', foreground='#ef4444')
        self.text_widget.tag_configure('question', foreground='#60a5fa')
        self.text_widget.tag_configure('response', foreground='#a78bfa')
        self.text_widget.tag_configure('timestamp', foreground='#6b7280', font=('Consolas', 8))
        # New tags for agent activity
        self.text_widget.tag_configure('goal', foreground='#fbbf24', font=('Consolas', 9, 'bold'))  # Yellow bold for goals
        self.text_widget.tag_configure('action', foreground='#06d6a0', font=('Consolas', 9, 'bold'))  # Teal bold for actions
        self.text_widget.tag_configure('step', foreground='#8b5cf6', font=('Consolas', 9, 'bold'))  # Purple bold for steps
        
        self.is_minimized = False
        self.normal_height = self.height
    
    def _toggle_minimize(self):
        """Toggle between minimized and normal state"""
        if self.is_minimized:
            self.root.geometry(f"{self.width}x{self.normal_height}")
            self.is_minimized = False
        else:
            self.root.geometry(f"{self.width}x50")
            self.is_minimized = True
    
    def _start_message_processor(self):
        """Start processing messages from the queue"""
        self._process_messages()
    
    def _process_messages(self):
        """Process messages from the queue and display them"""
        try:
            while not self.message_queue.empty():
                message, msg_type, timestamp = self.message_queue.get_nowait()
                self._display_message(message, msg_type, timestamp)
        except queue.Empty:
            pass
        
        if self.is_running:
            self.root.after(100, self._process_messages)
    
    def _display_message(self, message: str, msg_type: str, timestamp: float):
        """Display a message in the text widget"""
        if not self.text_widget:
            return
        
        # Format timestamp
        time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
        
        # Insert timestamp
        self.text_widget.insert('end', f"[{time_str}] ", 'timestamp')
        
        # Special formatting for agent activity
        if msg_type in ['goal', 'action', 'step']:
            # Add some visual separation for important agent messages
            if msg_type == 'step':
                self.text_widget.insert('end', "═" * 50 + "\n", 'timestamp')
                self.text_widget.insert('end', f"[{time_str}] ", 'timestamp')
            
            # Insert message with appropriate styling
            self.text_widget.insert('end', f"{message}\n", msg_type)
            
            if msg_type == 'step':
                self.text_widget.insert('end', "═" * 50 + "\n", 'timestamp')
        else:
            # Insert message with appropriate styling
            self.text_widget.insert('end', f"{message}\n", msg_type)
        
        # Auto-scroll to bottom
        self.text_widget.see('end')
        
        # Limit text widget content to prevent memory issues
        lines = self.text_widget.get('1.0', 'end').count('\n')
        if lines > 1000:
            self.text_widget.delete('1.0', '100.0')

class UIMessageHandler:
    """Handler to capture and route print statements to the UI"""
    
    def __init__(self, ui: HoveringUI):
        self.ui = ui
        self.original_print = print
    
    def enhanced_print(self, *args, **kwargs):
        """Enhanced print function that also sends to UI"""
        # Call original print
        self.original_print(*args, **kwargs)
        
        # Extract message and determine type
        message = ' '.join(str(arg) for arg in args)
        msg_type = self._determine_message_type(message)
        
        # Send to UI
        self.ui.add_message(message, msg_type)
    
    def _determine_message_type(self, message: str) -> str:
        """Determine message type based on content"""
        message_lower = message.lower()
        
        # Check for agent activity patterns first (more specific)
        if '🎯 next goal:' in message_lower:
            return 'goal'
        elif '🦾 [action' in message_lower and ']' in message:
            return 'action'
        elif '📍 step' in message_lower:
            return 'step'
        elif any(emoji in message for emoji in ['🤔', '❓']):
            return 'question'
        elif any(emoji in message for emoji in ['✅', '🎯', '📝']):
            return 'success'
        elif any(emoji in message for emoji in ['⚠️', '🔊']):
            return 'warning'
        elif any(emoji in message for emoji in ['❌', '⏹️']):
            return 'error'
        elif 'received:' in message_lower or 'response:' in message_lower:
            return 'response'
        else:
            return 'info'

# Global UI instance
_ui_instance: Optional[HoveringUI] = None
_message_handler: Optional[UIMessageHandler] = None

def initialize_ui(width: int = 450, height: int = 350, opacity: float = 0.85, language: Optional[str] = None):
    """Initialize the hovering UI"""
    global _ui_instance, _message_handler
    
    if _ui_instance is None:
        _ui_instance = HoveringUI(width, height, opacity, language)
        _message_handler = UIMessageHandler(_ui_instance)
        
        # Replace the global print function
        import builtins
        builtins.print = _message_handler.enhanced_print
        
        # Start the UI
        _ui_instance.start()
        
        # Add welcome message
        _ui_instance.add_message(get_text("ui.starting"), "success")
    
    return _ui_instance

def shutdown_ui():
    """Shutdown the hovering UI"""
    global _ui_instance, _message_handler
    
    if _ui_instance:
        _ui_instance.add_message(get_text("ui.shutting_down"), "info")
        time.sleep(0.5)
        _ui_instance.stop()
        _ui_instance = None
    
    if _message_handler:
        # Restore original print function
        import builtins
        builtins.print = _message_handler.original_print
        _message_handler = None

def get_ui() -> Optional[HoveringUI]:
    """Get the current UI instance"""
    return _ui_instance

def add_ui_message(message: str, msg_type: str = "info"):
    """Add a message to the UI (if available)"""
    if _ui_instance:
        _ui_instance.add_message(message, msg_type)