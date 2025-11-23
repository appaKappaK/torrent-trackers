import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import logging
import time
from models.tracker_models import Tracker
from typing import Callable, Any, List
from controllers.main_controller import MainController
from views.history_view import HistoryView

logger = logging.getLogger(__name__)

class MainView:
    def __init__(self, root, controller: MainController):
        self.root = root
        self.controller = controller
        self.controller.set_view(self)
        
        # Load preferences from config
        self.is_dark_mode = self.controller.config.get("gui.dark_mode", False)
        self.auto_scroll = self.controller.config.get("gui.auto_scroll", True)
        
        # Cache for efficient theming
        self._label_widgets: List[tk.Label] = []
        
        self.setup_gui()
        self.setup_bindings()
        self.apply_theme()
    
    def show_error(self, message: str):
        """Show error message - used by controller"""
        messagebox.showerror("Error", message)
    
    def safe_gui_update(self, func: Callable, *args, **kwargs):
        """Enhanced safe GUI update"""
        def update():
            try:
                func(*args, **kwargs)
            except tk.TclError as e:
                logger.debug(f"GUI update skipped (widget destroyed): {e}")
            except Exception as e:
                logger.error(f"GUI update failed: {e}")
        try:
            self.root.after(0, update)
        except Exception as e:
            logger.error(f"Could not schedule GUI update: {e}")
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Set menu colors based on current theme
        bg_color = "#1a1a1a" if self.is_dark_mode else "#f5f5f5"
        fg_color = "#e8e8e8" if self.is_dark_mode else "#333333"
        active_bg = "#505050" if self.is_dark_mode else "#e0e0e0"
        
        # Configure main menu bar
        menubar.configure(
            background=bg_color,
            foreground=fg_color,
            activebackground=active_bg,
            activeforeground=fg_color,
            relief="flat",
            bd=0
        )
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0,
                        bg=bg_color,
                        fg=fg_color,
                        activebackground=active_bg,
                        activeforeground=fg_color)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Trackers", command=self.on_load_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0,
                        bg=bg_color,
                        fg=fg_color,
                        activebackground=active_bg,
                        activeforeground=fg_color)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        
        # Auto-scroll variable needs to be tracked
        self.auto_scroll_var = tk.BooleanVar(value=self.auto_scroll)
        view_menu.add_checkbutton(
            label="Auto-scroll Results", 
            variable=self.auto_scroll_var,
            command=self.toggle_auto_scroll
        )
        
        # Tools menu - SIMPLIFIED to just Clear All
        tools_menu = tk.Menu(menubar, tearoff=0,
                            bg=bg_color,
                            fg=fg_color,
                            activebackground=active_bg,
                            activeforeground=fg_color)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clear All", command=self.on_clear_all)
        # REMOVED: Find Duplicates and Validate Trackers (they're in the tabs)

    def toggle_auto_scroll(self):
        """Toggle auto-scroll feature"""
        self.auto_scroll = not self.auto_scroll
        self.controller.config.set("gui.auto_scroll", self.auto_scroll)

    def setup_gui(self):
        """Setup the GUI components with label caching"""
        self.root.title("Tracker Manager Pro")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)  # Set minimum window size
        
        self.create_menu_bar()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Setup tabs
        self.setup_duplicate_tab()
        self.setup_validation_tab()
        self.setup_results_tab()
        self.setup_history_tab()

        # Collect all labels for efficient theming
        self._collect_labels(self.root)

    def _collect_labels(self, parent):
        """Collect all Label widgets for efficient theming"""
        try:
            for child in parent.winfo_children():
                if child.winfo_class() == 'Label':
                    self._label_widgets.append(child)
                if child.winfo_children():
                    self._collect_labels(child)
        except Exception as e:
            logger.debug(f"Could not collect labels from {parent}: {e}")

    def update_status(self, message: str):
        """Update status bar message"""
        # Since we removed the status label, just log it
        logger.info(f"Status: {message}")
        
    def setup_history_tab(self):
        """Setup history and analytics tab"""
        self.history_view = HistoryView(self.notebook, self.controller)
        self.notebook.add(self.history_view.tab, text="4. History & Analytics")

    def debug_widgets(self, parent, level=0):
        """Debug method to see all widgets"""
        indent = "  " * level
        try:
            for child in parent.winfo_children():
                print(f"{indent}{child.winfo_class()}: {child}")
                if child.winfo_children():
                    self.debug_widgets(child, level + 1)
        except:
            pass

    def toggle_theme(self):
        """Toggle between light and dark mode and save preference"""
        self.is_dark_mode = not self.is_dark_mode
        
        # Save to config
        self.controller.config.set("gui.dark_mode", self.is_dark_mode)
        
        # Update toolbar button text with state management
        if hasattr(self, 'theme_btn') and self.theme_btn.winfo_exists():
            new_text = "☀️ Light Mode" if self.is_dark_mode else "🌙 Dark Mode"
            self.theme_btn.config(text=new_text)
        
        self.apply_theme()
        self.update_status(f"Theme changed to {'Dark' if self.is_dark_mode else 'Light'} mode")

    def apply_theme(self):
        """Apply the current theme - optimized version"""
        if self.is_dark_mode:
            bg_color, fg_color, text_bg, text_fg = "#1a1a1a", "#e8e8e8", "#2a2a2a", "#ffffff"
        else:
            bg_color, fg_color, text_bg, text_fg = "#f5f5f5", "#333333", "#ffffff", "#000000"
        
        self.apply_colors(bg_color, fg_color, text_bg, text_fg)

    def apply_menu_theme(self, bg_color, fg_color):
        """Apply theme to the menu bar"""
        try:
            menubar = self.root.cget("menu")
            if menubar:
                # Configure the main menu bar
                try:
                    menubar.configure(
                        background=bg_color,
                        foreground=fg_color,
                        activebackground="#505050" if self.is_dark_mode else "#e0e0e0",
                        activeforeground=fg_color,
                        relief="flat",  # ADD THIS
                        bd=0  # ADD THIS - remove border
                    )
                except:
                    pass  # Some systems don't allow menu theming
                
                # Configure all submenus (File, View, Tools)
                for i in range(menubar.index("end") + 1):
                    try:
                        menu_name = menubar.entrycget(i, "menu")
                        if menu_name:
                            submenu = menubar.nametowidget(menu_name)
                            submenu.configure(
                                background=bg_color,
                                foreground=fg_color,
                                activebackground="#505050" if self.is_dark_mode else "#e0e0e0",
                                activeforeground=fg_color,
                                selectcolor=fg_color,
                                relief="flat",  # ADD THIS
                                bd=0  # ADD THIS - remove border
                            )
                    except:
                        continue  # Skip if we can't configure this menu
                        
        except Exception as e:
            logger.debug(f"Menu theming failed: {e}")

    def apply_colors(self, bg_color, fg_color, text_bg, text_fg):
        """Apply colors to all widgets - optimized"""
        # Apply to root window
        self.root.configure(bg=bg_color)
        
        # Apply to menu bar
        self.apply_menu_theme(bg_color, fg_color)
        
        # Apply ttk styles first (global)
        self.apply_ttk_styles(bg_color, fg_color)
        
        # Apply to specific widgets (optimized)
        self.apply_to_specific_widgets(bg_color, fg_color, text_bg, text_fg)

    def apply_to_specific_widgets(self, bg_color, fg_color, text_bg, text_fg):
        """Apply colors to specific widgets without recursion"""
        # Text widgets
        text_widgets = [
            self.input_text, self.unique_text, self.working_text,
            self.dead_text, self.preview_text
        ]
        
        for widget in text_widgets:
            if widget and widget.winfo_exists():
                try:
                    widget.configure(
                        background=text_bg,
                        foreground=text_fg,
                        insertbackground=fg_color,
                        selectbackground="#555555" if self.is_dark_mode else "#e0e0e0",
                        selectforeground=text_fg
                    )
                except Exception as e:
                    logger.debug(f"Could not theme widget: {e}")
        
        # Labels and other specific widgets
        label_attributes = [
            'stats_label', 'progress_label', 'timer_label', 'interface_status',
            'wan_ip_label', 'wan_ip_value'
        ]
        
        for attr_name in label_attributes:
            if hasattr(self, attr_name):
                label_widget = getattr(self, attr_name)
                if label_widget and label_widget.winfo_exists():
                    try:
                        label_widget.configure(bg=bg_color, fg=fg_color)
                    except Exception as e:
                        logger.debug(f"Could not theme label {attr_name}: {e}")
        
        # Apply theme to ALL labels using cached list
        self.apply_theme_to_all_labels(bg_color, fg_color)
        
        # History view theming
        if hasattr(self, 'history_view'):
            try:
                self.history_view.apply_theme(bg_color, fg_color, text_bg, text_fg)
            except Exception as e:
                logger.debug(f"Could not theme history view: {e}")

    def apply_ttk_styles(self, bg_color, fg_color):
        """Apply styles to ttk widgets"""
        style = ttk.Style()
        
        if self.is_dark_mode:
            # Dark theme ttk styles
            style.configure("TFrame", background=bg_color)
            style.configure("TLabel", background=bg_color, foreground=fg_color)
            style.configure("TLabelframe", background=bg_color, foreground=fg_color)
            
            style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color)

            # Button styles
            style.configure("TButton", 
                        background="#404040", 
                        foreground=fg_color,
                        focuscolor=bg_color)
            style.map("TButton",
                    background=[('active', '#505050'), ('pressed', '#606060')],
                    foreground=[('active', fg_color), ('pressed', fg_color)])
            
            # Notebook styles
            style.configure("TNotebook", background=bg_color)
            style.configure("TNotebook.Tab", 
                        background="#404040", 
                        foreground=fg_color,
                        focuscolor=bg_color,
                        padding=[10, 2])
            style.map("TNotebook.Tab",
                    background=[('selected', '#505050'), ('active', '#484848')],
                    foreground=[('selected', fg_color), ('active', fg_color)])
            
            # Progress bar
            style.configure("Horizontal.TProgressbar", 
                        background="#0078d7",
                        troughcolor=bg_color,
                        bordercolor=bg_color,
                        darkcolor="#0078d7",
                        lightcolor="#0078d7")
        else:
            # Light theme ttk styles
            style.configure("TFrame", background=bg_color)
            style.configure("TLabel", background=bg_color, foreground=fg_color)
            style.configure("TLabelframe", background=bg_color, foreground=fg_color)
            
            style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color)  

            # Button styles
            style.configure("TButton", 
                        background=bg_color, 
                        foreground=fg_color)
            style.map("TButton",
                    background=[('active', '#e0e0e0'), ('pressed', '#d0d0d0')],
                    foreground=[('active', fg_color), ('pressed', fg_color)])
            
            # Notebook styles
            style.configure("TNotebook", background=bg_color)
            style.configure("TNotebook.Tab", 
                        background=bg_color, 
                        foreground=fg_color)
            style.map("TNotebook.Tab",
                    background=[('selected', '#e0e0e0'), ('active', '#f0f0f0')],
                    foreground=[('selected', fg_color), ('active', fg_color)])
            
            # Progress bar
            style.configure("Horizontal.TProgressbar", 
                        background="#0078d7",
                        troughcolor=bg_color)
    
    def apply_theme_to_all_labels(self, bg_color, fg_color):
        """Apply theme to all cached labels - optimized"""
        for label in self._label_widgets:
            try:
                if label.winfo_exists():
                    label.configure(bg=bg_color, fg=fg_color)
            except Exception as e:
                logger.debug(f"Could not theme label: {e}")

    def setup_duplicate_tab(self):
        """Setup duplicate detection tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="1. Find Duplicates")
        
        # Input area
        input_frame = ttk.LabelFrame(tab, text="Input Trackers", padding=10)
        input_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        tk.Label(input_frame, text="Paste your tracker list below:").pack(anchor='w', pady=(0, 5))
        self.input_text = scrolledtext.ScrolledText(input_frame, height=12)
        self.input_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Find Duplicates", 
                  command=self.on_find_duplicates).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Clear", 
                  command=self.on_clear).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Load from File", 
                  command=self.on_load_file).pack(side='left')
        ttk.Button(btn_frame, text="Sample Data", 
                  command=self.load_sample_data).pack(side='left', padx=(10, 0))
        
        # Results area
        results_frame = ttk.LabelFrame(tab, text="Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        tk.Label(results_frame, text="Unique trackers found:").pack(anchor='w', pady=(0, 5))
        self.unique_text = scrolledtext.ScrolledText(results_frame, height=8)
        self.unique_text.pack(fill='both', expand=True)
        
        # Stats
        self.stats_label = tk.Label(results_frame, text="Total: 0 | Unique: 0 | Duplicates: 0")
        self.stats_label.pack(anchor='w', pady=5)

    def load_sample_data(self):
        """Load sample tracker data for testing"""
        sample_trackers = """udp://tracker.opentrackr.org:1337/announce
http://tracker.openbittorrent.com:80/announce
udp://9.rarbg.to:2710/announce
udp://tracker.opentrackr.org:1337/announce
http://tracker.openbittorrent.com:80/announce
udp://open.stealth.si:80/announce"""
        
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', sample_trackers)
        self.update_status("Sample data loaded")

    def setup_validation_tab(self):
        """Setup validation tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="2. Validate Trackers")
        
        # Network Interface section (Linux only)
        if self.controller.is_linux_system():
            interface_frame = ttk.LabelFrame(tab, text="Network Interface (Linux Only)", padding=10)
            interface_frame.pack(fill='x', padx=5, pady=5)
            
            # Interface selection
            ttk.Label(interface_frame, text="Bind to interface:").pack(anchor='w', pady=(0, 5))
            
            interface_select_frame = ttk.Frame(interface_frame)
            interface_select_frame.pack(fill='x', pady=5)
            
            self.interface_var = tk.StringVar(value="Auto (default)")
            interfaces = self.controller.get_network_interfaces()
            interface_names = ["Auto (default)"] + [f"{i['name']} ({i['ip']}) - {i['type']}" for i in interfaces]
            
            self.interface_combo = ttk.Combobox(interface_select_frame, 
                                              textvariable=self.interface_var,
                                              values=interface_names,
                                              state="readonly",
                                              width=40)
            self.interface_combo.pack(side='left', padx=(0, 10))
            
            ttk.Button(interface_select_frame, text="Refresh Interfaces", 
                      command=self.refresh_interfaces).pack(side='left')
            
            # WAN IP display frame
            wan_ip_frame = ttk.Frame(interface_frame)
            wan_ip_frame.pack(fill='x', pady=(10, 0))
            
            # WAN IP display
            wan_ip_display_frame = ttk.LabelFrame(wan_ip_frame, text="WAN IP Verification", padding=5)
            wan_ip_display_frame.pack(fill='x', pady=5)
            
            wan_ip_content = ttk.Frame(wan_ip_display_frame)
            wan_ip_content.pack(fill='x', padx=5, pady=2)
            
            self.wan_ip_label = tk.Label(wan_ip_content, text="Current WAN IP:", font=("Arial", 9))
            self.wan_ip_label.pack(side='left')
            
            self.wan_ip_value = tk.Label(wan_ip_content, text="Unknown", font=("Arial", 9, "bold"), fg="blue")
            self.wan_ip_value.pack(side='left', padx=(5, 10))
            
            ttk.Button(wan_ip_content, text="Check IP", 
                      command=self.check_wan_ip).pack(side='left', padx=(0, 5))
            
            ttk.Button(wan_ip_content, text="Test Interface", 
                      command=self.test_interface).pack(side='left')
            
            # Interface status
            self.interface_status = tk.Label(interface_frame, text="Interface: Default", 
                                           font=("Arial", 9), fg="gray")
            self.interface_status.pack(anchor='w', pady=(5, 0))
            
            # Update status when interface is selected
            def on_interface_selected(event):
                selected = self.interface_var.get()
                if selected != "Auto (default)":
                    interface_name = selected.split(' ')[0]
                    self.interface_status.config(
                        text=f"Interface: {interface_name} ✅", 
                        fg="green"
                    )
                    # Auto-check WAN IP when interface changes
                    self.root.after(500, self.check_wan_ip)
                else:
                    self.interface_status.config(
                        text="Interface: Default", 
                        fg="gray"
                    )
                    self.check_wan_ip()
            
            if hasattr(self, 'interface_combo'):
                self.interface_combo.bind('<<ComboboxSelected>>', on_interface_selected)
        
        # Control section
        control_frame = ttk.LabelFrame(tab, text="Validation Control", padding=10)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(control_frame, text="Click to validate all unique trackers:").pack(anchor='w', pady=(0, 10))
        
        # Progress and control frame
        progress_frame = ttk.Frame(control_frame)
        progress_frame.pack(fill='x', pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill='x', side='left', expand=True, padx=(0, 10))
        
        self.progress_label = tk.Label(progress_frame, text="0/0")
        self.progress_label.pack(side='left', padx=(0, 10))
        
        self.validate_btn = ttk.Button(progress_frame, text="Validate Trackers", 
                                      command=self.on_start_validation)
        self.validate_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = ttk.Button(progress_frame, text="Stop", 
                                  command=self.on_stop_validation,
                                  state='disabled')
        self.stop_btn.pack(side='left')
        
        self.timer_label = tk.Label(control_frame, text="Elapsed: 0s")
        self.timer_label.pack(anchor='w', pady=(5, 0))
        
        # Results area
        results_frame = ttk.LabelFrame(tab, text="Validation Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        tk.Label(results_frame, text="Working Trackers:").grid(row=0, column=0, sticky='w')
        tk.Label(results_frame, text="Dead Trackers:").grid(row=0, column=1, sticky='w')
        
        self.working_text = scrolledtext.ScrolledText(results_frame, height=8)
        self.working_text.grid(row=1, column=0, sticky='nsew', padx=(0, 5))
        
        self.dead_text = scrolledtext.ScrolledText(results_frame, height=8)
        self.dead_text.grid(row=1, column=1, sticky='nsew', padx=(5, 0))
        
        results_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(1, weight=1)
        results_frame.rowconfigure(1, weight=1)

    def check_wan_ip(self):
        """Check and display the current WAN IP"""
        if hasattr(self, 'interface_var'):
            interface_name = None
            if self.interface_var.get() != "Auto (default)":
                interface_name = self.interface_var.get().split(' ')[0]
            
            self.controller.set_validation_interface(interface_name)
            external_ip = self.controller.validator.get_external_ip()
            
            self.wan_ip_value.config(text=external_ip)
            if "failed" in external_ip.lower():
                self.wan_ip_value.config(fg="red")
            else:
                self.wan_ip_value.config(fg="green")
            
            self.update_status(f"WAN IP: {external_ip}")

    def test_interface(self):
        """Test the currently selected interface"""
        if hasattr(self, 'interface_var'):
            interface_name = None
            if self.interface_var.get() != "Auto (default)":
                interface_name = self.interface_var.get().split(' ')[0]
            
            self.controller.set_validation_interface(interface_name)
            
            try:
                # Quick test to httpbin.org to see our IP
                import requests
                with requests.Session() as session:
                    if interface_name:
                        session = self.controller.validator.interface_binder.bind_to_interface(session, interface_name)
                        interface_info = f" via {interface_name}"
                    else:
                        interface_info = " (default)"
                    
                    response = session.get('https://httpbin.org/ip', timeout=10)
                    ip_data = response.json()
                    external_ip = ip_data.get('origin', 'Unknown')
                    
                    messagebox.showinfo("Interface Test", 
                                      f"Interface: {interface_name or 'Default'}\n"
                                      f"External IP: {external_ip}\n"
                                      f"Status: ✅ Working")
                    self.update_status(f"Interface test: {external_ip}{interface_info}")
                    
                    # Update WAN IP display
                    self.wan_ip_value.config(text=external_ip, fg="green")
            except Exception as e:
                messagebox.showerror("Interface Test Failed", f"Error: {e}")
                self.update_status("Interface test failed")
                self.wan_ip_value.config(text=f"Test failed: {e}", fg="red")

    def refresh_interfaces(self):
        """Refresh network interfaces list"""
        if hasattr(self, 'interface_combo'):
            interfaces = self.controller.get_network_interfaces()
            interface_names = ["Auto (default)"] + [f"{i['name']} ({i['ip']}) - {i['type']}" for i in interfaces]
            self.interface_combo['values'] = interface_names
            self.update_status("Network interfaces refreshed")

    def setup_results_tab(self):
        """Setup results tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="3. Export Results")
        
        # Export controls
        export_frame = ttk.LabelFrame(tab, text="Export Options", padding=10)
        export_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(export_frame, text="Export your validated trackers:").pack(anchor='w', pady=(0, 10))
        
        btn_frame = ttk.Frame(export_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Export Working Trackers as TXT",
                  command=self.on_export_txt).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Export All Results as JSON",
                  command=self.on_export_json).pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="Copy Working to Clipboard",
                  command=self.on_copy_clipboard).pack(side='left')
        
        # Preview area
        preview_frame = ttk.LabelFrame(tab, text="Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        tk.Label(preview_frame, text="Preview:").pack(anchor='w', pady=(0, 5))
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=15)
        self.preview_text.pack(fill='both', expand=True)
    
    def setup_bindings(self):
        """Setup event bindings and keyboard shortcuts"""
        # Ctrl+Q to quit
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
        # Ctrl+D to find duplicates
        self.root.bind('<Control-d>', lambda e: self.on_find_duplicates())
        
        # Ctrl+V to validate
        self.root.bind('<Control-v>', lambda e: self.on_start_validation())
        
        # Ctrl+T to toggle theme
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())
        
        # Escape to stop validation
        self.root.bind('<Escape>', lambda e: self.on_stop_validation() if hasattr(self, 'stop_btn') and self.stop_btn['state'] == 'normal' else None)
        
        # F1 for help
        self.root.bind('<F1>', lambda e: self.show_help())

    def show_help(self):
        """Show quick help dialog"""
        help_text = """Tracker Manager Pro - Quick Help

Shortcuts:
• Ctrl+D: Find duplicates
• Ctrl+V: Validate trackers  
• Ctrl+T: Toggle theme
• Ctrl+Q: Quit application
• Escape: Stop validation
• F1: Show this help

Tips:
• Use 'Sample Data' to test the application
• Check the History tab for reliability statistics
• Export results in multiple formats
• On Linux: Use network interface binding for VPN validation
• Use WAN IP verification to confirm interface binding"""

        messagebox.showinfo("Quick Help", help_text)
    
    def update_progress(self, percent, current, total):
        """Update progress bar and label with bounds checking"""
        try:
            if hasattr(self, 'progress'):
                # Ensure percent is within valid range
                safe_percent = max(0, min(100, percent))
                self.progress['value'] = safe_percent
                
            if hasattr(self, 'progress_label'):
                self.progress_label.config(text=f"{current}/{total}")
                
            self.update_status(f"Validating... {current}/{total} ({safe_percent:.1f}%)")
        except Exception as e:
            logger.debug(f"Progress update failed: {e}")

    def append_tracker_result(self, tracker):
        """Append a single tracker result to the appropriate text area"""
        try:
            text_widget = self.working_text if tracker.alive else self.dead_text
            status_icon = "✅" if tracker.alive else "❌"
            response_time = f" ({tracker.response_time:.2f}s)" if tracker.response_time else ""
            
            # Add interface info if bound
            interface_info = ""
            if hasattr(self.controller.validator, 'bound_interface') and self.controller.validator.bound_interface:
                interface_info = f" [via {self.controller.validator.bound_interface}]"
            
            text_widget.insert(tk.END, f"{status_icon} {tracker.url}{response_time}{interface_info}\n")
            
            # Only auto-scroll if enabled
            if self.auto_scroll:
                text_widget.see(tk.END)
                
        except Exception as e:
            logger.debug(f"Could not append tracker result: {e}")
            
    # Event handlers
    def on_find_duplicates(self):
        try:
            text = self.input_text.get('1.0', tk.END).strip()
            if not text:
                messagebox.showwarning("Warning", "Please enter some tracker URLs first!")
                return
                
            self.update_status("Finding duplicates...")
            stats = self.controller.find_duplicates(text)
            
            self.unique_text.delete('1.0', tk.END)
            unique_urls = self.controller.trackers.unique_urls
            self.unique_text.insert('1.0', '\n'.join(unique_urls))
            
            self.stats_label.config(
                text=f"Total: {stats['total']} | Unique: {stats['unique']} | Duplicates: {stats['duplicates']}"
            )
            
            self.notebook.select(1)  # Switch to validation tab
            self.update_status(f"Found {stats['unique']} unique trackers out of {stats['total']} total")
            messagebox.showinfo("Success", f"Found {stats['unique']} unique trackers out of {stats['total']} total.")
            
        except ValueError as e:
            messagebox.showwarning("Warning", str(e))
            self.update_status("Error finding duplicates")
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.update_status("Error finding duplicates")
    
    def on_clear(self):
        """Clear current tab data"""
        self.input_text.delete('1.0', tk.END)
        self.unique_text.delete('1.0', tk.END)
        self.stats_label.config(text="Total: 0 | Unique: 0 | Duplicates: 0")
        self.controller.trackers.clear()
        self.update_status("Data cleared")
    
    def on_clear_all(self):
        """Clear all data across tabs"""
        self.on_clear()
        self.working_text.delete('1.0', tk.END)
        self.dead_text.delete('1.0', tk.END)
        self.preview_text.delete('1.0', tk.END)
        self.progress['value'] = 0
        self.progress_label.config(text="0/0")
        self.timer_label.config(text="Elapsed: 0s")
        self.update_status("All data cleared")
    
    def on_load_file(self):
        file_path = filedialog.askopenfilename(
            title="Load Tracker List",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_text.delete('1.0', tk.END)
                self.input_text.insert('1.0', content)
                self.update_status(f"Loaded trackers from {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file: {e}")
                self.update_status("Error loading file")
    
    def on_start_validation(self):
        try:
            if not self.controller.trackers.unique_urls:
                messagebox.showwarning("Warning", "No trackers to validate! Find duplicates first.")
                return
                
            # Set network interface before validation (Linux only)
            if hasattr(self, 'interface_var') and self.interface_var.get() != "Auto (default)":
                interface_name = self.interface_var.get().split(' ')[0]  # Extract interface name
                self.controller.set_validation_interface(interface_name)
                self.update_status(f"Validation using interface: {interface_name}")
            else:
                self.controller.set_validation_interface(None)
                self.update_status("Validation using default interface")
                
            self.controller.start_validation()
            self.validate_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.working_text.delete('1.0', tk.END)
            self.dead_text.delete('1.0', tk.END)
            self.start_time = time.time()
            self.update_status("Validation started...")
            self.update_timer()
            
        except ValueError as e:
            messagebox.showwarning("Warning", str(e))
        except Exception as e:
            logger.error(f"Error starting validation: {e}")
            messagebox.showerror("Error", f"Failed to start validation: {e}")
            self.update_status("Error starting validation")
    
    def on_stop_validation(self):
        self.controller.stop_validation()
        self.validate_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.update_status("Validation stopped by user")
    
    def on_validation_complete(self, working_count: int, total_count: int, elapsed: float):
        """Called when validation completes"""
        self.validate_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        success_rate = (working_count / total_count * 100) if total_count > 0 else 0
        message = f"Validation finished! Working: {working_count}/{total_count} ({success_rate:.1f}%) - Time: {elapsed:.2f}s"
        
        messagebox.showinfo("Complete", message)
        self.update_status(message)
        self.update_preview()
        self.notebook.select(2)  # Switch to results tab
    
    def update_timer(self):
        """Update elapsed time display"""
        if hasattr(self, 'validate_btn') and self.validate_btn['state'] == 'disabled':
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Elapsed: {elapsed}s")
            self.root.after(1000, self.update_timer)
    
    def update_preview(self):
        """Update results preview"""
        try:
            working_text = self.controller.export_working_trackers()
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', working_text)
        except Exception as e:
            logger.error(f"Error updating preview: {e}")
    
    def on_export_txt(self):
        try:
            content = self.controller.export_working_trackers()
            if not content.strip():
                messagebox.showwarning("Warning", "No working trackers to export!")
                return
                
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Working Trackers"
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                trackers_count = len(content.splitlines())
                messagebox.showinfo("Success", f"Exported {trackers_count} trackers to {file_path}")
                self.update_status(f"Exported {trackers_count} trackers to TXT")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
            self.update_status("Export failed")
    
    def on_export_json(self):
        try:
            data = self.controller.export_all_results()
            if not data.get('results'):
                messagebox.showwarning("Warning", "No validation results to export!")
                return
                
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export All Results"
            )
            if file_path:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Success", f"Exported complete results to {file_path}")
                self.update_status("Exported complete results to JSON")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
            self.update_status("Export failed")
    
    def on_copy_clipboard(self):
        try:
            content = self.controller.copy_to_clipboard()
            if not content.strip():
                messagebox.showwarning("Warning", "No working trackers to copy!")
                return
                
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            trackers_count = len(content.splitlines())
            messagebox.showinfo("Success", f"Copied {trackers_count} trackers to clipboard!")
            self.update_status(f"Copied {trackers_count} trackers to clipboard")
        except ValueError as e:
            messagebox.showwarning("Warning", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Copy failed: {e}")
            self.update_status("Copy to clipboard failed")