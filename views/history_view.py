import tkinter as tk
from tkinter import ttk, scrolledtext
import logging
from typing import List
from models.database_models import TrackerHistory

logger = logging.getLogger(__name__)

class HistoryView:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.setup_gui()
    
    def setup_gui(self):
        """Setup history tab GUI"""
        self.tab = ttk.Frame(self.parent)
        
        # Controls frame
        controls_frame = ttk.Frame(self.tab)
        controls_frame.pack(fill='x', pady=5)
        
        ttk.Button(controls_frame, text="Refresh", 
                  command=self.refresh_history).pack(side='left', padx=(0, 10))
        
        ttk.Button(controls_frame, text="Show Reliable Trackers",
                  command=self.show_reliable).pack(side='left', padx=(0, 10))
        
        ttk.Button(controls_frame, text="Show Favorites",
                  command=self.show_favorites).pack(side='left')
        
        # History table
        columns = ('URL', 'Status', 'Response Time', 'Last Checked', 'Success Rate')
        self.tree = ttk.Treeview(self.tab, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        self.tree.column('URL', width=300)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(self.tab, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Double-click to add to favorites
        self.tree.bind('<Double-1>', self.on_double_click)
        
        self.refresh_history()
    
    def apply_theme(self, bg_color, fg_color, text_bg, text_fg):
        """Apply theme to history tab widgets"""
        try:
            # Style the treeview
            style = ttk.Style()
            style.configure("Treeview", 
                          background=text_bg,
                          foreground=fg_color,
                          fieldbackground=text_bg)
            style.configure("Treeview.Heading",
                          background=bg_color,
                          foreground=fg_color)
            style.map('Treeview', 
                     background=[('selected', '#555555')],
                     foreground=[('selected', text_fg)])
            
            # Apply to the tab frame
            self.tab.configure(style='TFrame')
            
            # Refresh to show new colors
            self.refresh_history()
            
        except Exception as e:
            logger.debug(f"Could not theme history view: {e}")
    
    def refresh_history(self):
        """Refresh history display"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        history = self.controller.get_tracker_history(limit=50)
        for tracker in history:
            success_rate = (tracker.success_count / tracker.check_count * 100) if tracker.check_count > 0 else 0
            status = "✅ Working" if tracker.alive else "❌ Dead"
            
            self.tree.insert('', 'end', values=(
                tracker.url,
                status,
                f"{tracker.response_time:.2f}s" if tracker.response_time else "N/A",
                tracker.last_checked[:19] if tracker.last_checked else "Never",
                f"{success_rate:.1f}%"
            ))
    
    def show_reliable(self):
        """Show reliable trackers"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        reliable = self.controller.get_reliable_trackers(min_success_rate=0.7, min_checks=2)
        for tracker in reliable:
            success_rate = (tracker.success_count / tracker.check_count * 100)
            
            self.tree.insert('', 'end', values=(
                tracker.url,
                "✅ Working",
                f"{tracker.response_time:.2f}s" if tracker.response_time else "N/A",
                tracker.last_checked[:19] if tracker.last_checked else "Never",
                f"{success_rate:.1f}%"
            ))
    
    def show_favorites(self):
        """Show favorite trackers"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        favorites = self.controller.get_favorites()
        for tracker in favorites:
            success_rate = (tracker.success_count / tracker.check_count * 100) if tracker.check_count > 0 else 0
            
            self.tree.insert('', 'end', values=(
                tracker.url,
                "✅ Working" if tracker.alive else "❌ Dead",
                f"{tracker.response_time:.2f}s" if tracker.response_time else "N/A",
                tracker.last_checked[:19] if tracker.last_checked else "Never",
                f"{success_rate:.1f}%"
            ))
    
    def on_double_click(self, event):
        """Add double-clicked tracker to favorites"""
        selection = self.tree.selection()
        if not selection:
            return
        try:
            item = selection[0]
            values = self.tree.item(item, 'values')
            if values and len(values) > 0:
                url = values[0]
                self.controller.add_to_favorites(url, "Added from history")
                tk.messagebox.showinfo("Favorite Added", f"Added {url} to favorites!")
        except (IndexError, tk.TclError) as e:
            logger.debug(f"Could not add favorite: {e}")