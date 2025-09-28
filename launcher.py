import tkinter as tk
from tkinter import ttk
import subprocess
import os
import sys
from pathlib import Path

class Browser4AllLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 Browser4All Launcher")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Language options based on supported languages from your codebase
        self.languages = {
            'Auto-detect': 'auto',
            'English': 'en',
            'Español': 'es', 
            'Français': 'fr',
            'Deutsch': 'de',
            '中文': 'zh'
        }
        
        self.setup_ui()
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🤖 Browser4All Launcher", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Language selection
        lang_label = ttk.Label(main_frame, text="Select Language:")
        lang_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.language_var = tk.StringVar(value="Auto-detect")
        self.language_combo = ttk.Combobox(
            main_frame,
            textvariable=self.language_var,
            values=list(self.languages.keys()),
            state="readonly",
            width=25
        )
        self.language_combo.grid(row=2, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Run button
        self.run_button = ttk.Button(
            main_frame,
            text="🚀 Launch Browser4All",
            command=self.launch_program,
            style="Accent.TButton"
        )
        self.run_button.grid(row=3, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to launch", foreground="green")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Style configuration
        style = ttk.Style()
        if 'Accent.TButton' not in style.theme_names():
            style.configure('Accent.TButton', font=('Arial', 12, 'bold'))
    
    def launch_program(self):
        """Launch the Browser4All program with selected language"""
        try:
            # Update status
            self.status_label.config(text="Launching Browser4All...", foreground="orange")
            self.run_button.config(state="disabled")
            self.root.update()
            
            # Get selected language
            selected_lang_name = self.language_var.get()
            selected_lang_code = self.languages[selected_lang_name]
            
            # Define the target directory
            target_dir = r"C:\Users\taher\browser4all\Browser4All"
            
            # Check if directory exists
            if not os.path.exists(target_dir):
                self.status_label.config(
                    text="❌ Browser4All directory not found!", 
                    foreground="red"
                )
                self.run_button.config(state="normal")
                return
            
            # Check if main.py exists
            main_py_path = os.path.join(target_dir, "main.py")
            if not os.path.exists(main_py_path):
                self.status_label.config(
                    text="❌ main.py not found in Browser4All directory!", 
                    foreground="red"
                )
                self.run_button.config(state="normal")
                return
            
            # Prepare command based on language selection
            if selected_lang_code == 'auto':
                # No language argument for auto-detect
                cmd = ['python', 'main.py']
            else:
                # Add language argument
                cmd = ['python', 'main.py', '--language', selected_lang_code]
            
            # Launch in PowerShell with the correct directory
            powershell_cmd = f'cd "{target_dir}"; {" ".join(cmd)}'
            
            # Open new PowerShell window and run the command
            subprocess.Popen([
                'powershell', 
                '-NoExit',  # Keep window open after execution
                '-Command', 
                powershell_cmd
            ], cwd=target_dir)
            
            # Update status
            self.status_label.config(
                text=f"✅ Launched with language: {selected_lang_name}", 
                foreground="green"
            )
            
            # Optional: Close launcher after successful launch
            # Uncomment the next two lines if you want the launcher to close
            # self.root.after(2000, self.root.quit)  # Close after 2 seconds
            
        except Exception as e:
            self.status_label.config(
                text=f"❌ Launch failed: {str(e)}", 
                foreground="red"
            )
        finally:
            # Re-enable button
            self.run_button.config(state="normal")
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()

def main():
    """Main entry point"""
    launcher = Browser4AllLauncher()
    launcher.run()

if __name__ == "__main__":
    main()