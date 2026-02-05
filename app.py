from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container, VerticalScroll
from textual.widgets import Header, Footer, DirectoryTree, Static, Label, Rule
from textual.binding import Binding
from pathlib import Path
import os

class FileManagerApp(App):
    """A Textual file manager application."""
    
    TITLE = "⚡ File Manager"
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    Header {
        background: $primary-darken-2;
        color: $text;
        text-style: bold;
    }
    
    Footer {
        background: $panel-darken-1;
        color: $text-muted;
    }
    
    #main-container {
        layout: horizontal;
        height: 1fr;
        padding: 0;
        margin: 0;
        background: $surface;
    }
    
    #left-pane {
        width: 40%;
        height: 100%;
        background: $panel;
        border-right: vkey $primary;
        padding: 0;
    }
    
    #right-pane {
        width: 60%;
        height: 100%;
        background: $surface;
        padding: 0;
    }
    
    #tree-header {
        height: 3;
        background: $primary-darken-1;
        color: $text;
        padding: 1 2;
        text-style: bold;
        content-align: center middle;
    }
    
    #tree-container {
        height: 1fr;
        background: $panel;
        padding: 1 2;
        border-bottom: solid $primary-darken-2;
    }
    
    DirectoryTree {
        height: 100%;
        background: $panel;
        scrollbar-gutter: stable;
        scrollbar-size: 1 1;
    }
    
    DirectoryTree > .directory-tree--folder {
        color: $accent;
        text-style: bold;
    }
    
    DirectoryTree > .directory-tree--file {
        color: $text;
    }
    
    DirectoryTree:focus {
        border: none;
    }
    
    #tree-footer {
        height: 3;
        background: $panel-darken-1;
        color: $text-muted;
        padding: 1 2;
        text-style: italic;
    }
    
    #preview-container {
        height: 100%;
        padding: 0;
        layout: vertical;
    }
    
    #preview-header {
        height: 3;
        background: $primary-darken-1;
        color: $text;
        padding: 1 2;
        text-style: bold;
        content-align: left middle;
    }
    
    #preview-content {
        height: 1fr;
        background: $surface;
        padding: 2 3;
        overflow-y: auto;
        color: $text;
        scrollbar-size: 1 1;
    }
    
    #preview-footer {
        height: 3;
        background: $panel-darken-1;
        color: $text-muted;
        padding: 1 2;
    }
    
    .file-icon {
        color: $success;
    }
    
    .dir-icon {
        color: $warning;
    }
    
    .info-label {
        color: $text-muted;
        text-style: italic;
    }
    
    .error-text {
        color: $error;
        text-style: bold;
    }
    
    .success-text {
        color: $success;
    }
    
    .warning-text {
        color: $warning;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", key_display="q"),
        Binding("r", "refresh", "Refresh", key_display="r"),
        Binding("h", "toggle_help", "Help", key_display="h"),
        Binding("?", "toggle_help", "Help", show=False),
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("escape", "clear_selection", "Clear", show=False),
    ]
    
    def __init__(self):
        super().__init__()
        self.current_path = Path.home()
        self.selected_file = None
        self.help_visible = False
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        with Horizontal(id="main-container"):
            # Left pane - Directory Tree
            with Vertical(id="left-pane"):
                yield Static("📂 File Browser", id="tree-header")
                with Container(id="tree-container"):
                    yield DirectoryTree(str(self.current_path), id="tree")
                yield Static(f"🏠 {self.current_path}", id="tree-footer")
            
            # Right pane - Preview
            with Vertical(id="right-pane"):
                with Container(id="preview-container"):
                    yield Static("👁️  Preview", id="preview-header")
                    yield Static(
                        self._get_welcome_text(),
                        id="preview-content"
                    )
                    yield Static("Ready", id="preview-footer")
        
        yield Footer()
    
    def _get_welcome_text(self) -> str:
        """Get welcome text for preview pane."""
        return """[bold cyan]Welcome to File Manager![/bold cyan]

[dim]Navigate the file tree on the left to preview files and folders.[/dim]

[bold yellow]Quick Start:[/bold yellow]
  • Use [green]↑/↓[/green] to navigate
  • Press [green]Enter[/green] to select
  • Press [green]h[/green] for help
  • Press [green]q[/green] to quit

[dim]Select a file or folder to see its contents here.[/dim]
        """
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection."""
        file_path = Path(event.path)
        self.selected_file = file_path
        self.update_preview(file_path)
        self.update_footer(file_path)
    
    def update_preview(self, file_path: Path) -> None:
        """Update the preview pane with file contents."""
        preview = self.query_one("#preview-content", Static)
        header = self.query_one("#preview-header", Static)
        
        if not file_path.exists():
            header.update("❌ Error")
            preview.update("[red bold]File not found[/red bold]")
            return
        
        if file_path.is_dir():
            # Show directory info
            try:
                items = list(file_path.iterdir())
                dirs = [i for i in items if i.is_dir()]
                files = [i for i in items if i.is_file()]
                
                header.update(f"📁 {file_path.name}/")
                
                content = f"[bold cyan]═══ Directory Contents ═══[/bold cyan]\n\n"
                content += f"[dim]Path:[/dim] [italic]{file_path}[/italic]\n"
                content += f"[dim]Total:[/dim] {len(items)} items ([yellow]{len(dirs)}[/yellow] folders, [green]{len(files)}[/green] files)\n\n"
                
                if dirs:
                    content += "[bold yellow]📁 Folders[/bold yellow]\n"
                    for item in sorted(dirs)[:20]:
                        content += f"  [yellow]▸[/yellow] {item.name}\n"
                    if len(dirs) > 20:
                        content += f"  [dim]... and {len(dirs) - 20} more[/dim]\n"
                    content += "\n"
                
                if files:
                    content += "[bold green]📄 Files[/bold green]\n"
                    for item in sorted(files)[:20]:
                        size = item.stat().st_size
                        size_str = self._format_size(size)
                        ext = item.suffix or "no ext"
                        content += f"  [green]•[/green] {item.name} [dim]({size_str})[/dim]\n"
                    if len(files) > 20:
                        content += f"  [dim]... and {len(files) - 20} more[/dim]\n"
                
                preview.update(content)
            except PermissionError:
                header.update("🔒 Permission Denied")
                preview.update("[red bold]Permission denied[/red bold]\n\n[dim]You don't have access to this directory[/dim]")
        else:
            # Show file preview
            try:
                stat = file_path.stat()
                size = stat.st_size
                
                header.update(f"📄 {file_path.name}")
                
                if size > 1_000_000:  # 1MB limit
                    preview.update(
                        f"[yellow bold]⚠️  File too large to preview[/yellow bold]\n\n"
                        f"[dim]Size:[/dim] {self._format_size(size)}\n"
                        f"[dim]Path:[/dim] [italic]{file_path}[/italic]\n\n"
                        f"[dim]Files larger than 1MB are not previewed for performance reasons.[/dim]"
                    )
                    return
                
                # Try to read as text
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(10000)  # First 10k chars
                    
                    preview_text = f"[bold cyan]═══ File Preview ═══[/bold cyan]\n\n"
                    preview_text += f"[dim]Size:[/dim] {self._format_size(size)}\n"
                    preview_text += f"[dim]Path:[/dim] [italic]{file_path}[/italic]\n"
                    preview_text += f"[dim]Type:[/dim] {file_path.suffix or 'no extension'}\n\n"
                    preview_text += "[bold]Content:[/bold]\n\n"
                    preview_text += content
                    
                    if len(content) >= 10000:
                        preview_text += "\n\n[dim italic]... (preview truncated)[/dim]"
                    
                    preview.update(preview_text)
                    
            except UnicodeDecodeError:
                preview.update(
                    f"[yellow bold]📦 Binary file[/yellow bold]\n\n"
                    f"[dim]Size:[/dim] {self._format_size(size)}\n"
                    f"[dim]Path:[/dim] [italic]{file_path}[/italic]\n"
                    f"[dim]Type:[/dim] {file_path.suffix or 'unknown'}\n\n"
                    f"[dim]Cannot preview binary files in text mode.[/dim]"
                )
            except Exception as e:
                header.update("❌ Error")
                preview.update(f"[red bold]Error reading file[/red bold]\n\n{str(e)}")
    
    def update_footer(self, file_path: Path) -> None:
        """Update footer with file path."""
        footer = self.query_one("#preview-footer", Static)
        tree_footer = self.query_one("#tree-footer", Static)
        
        if file_path.is_dir():
            try:
                items = list(file_path.iterdir())
                footer.update(f"📁 {len(items)} items")
                tree_footer.update(f"📂 {file_path}")
            except:
                footer.update("🔒 Access denied")
                tree_footer.update(f"📂 {file_path}")
        else:
            try:
                size = file_path.stat().st_size
                footer.update(f"📄 {self._format_size(size)}")
                tree_footer.update(f"📂 {file_path.parent}")
            except:
                footer.update("❌ Error")
                tree_footer.update(f"📂 {file_path.parent}")
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def action_refresh(self) -> None:
        """Refresh the directory tree."""
        tree = self.query_one(DirectoryTree)
        tree.reload()
    
    def action_toggle_help(self) -> None:
        """Show help information."""
        if self.help_visible:
            self.help_visible = False
            if self.selected_file is not None:
                self.update_preview(self.selected_file)
                self.update_footer(self.selected_file)
            else:
                self.action_clear_selection()
            return

        self.help_visible = True
        preview = self.query_one("#preview-content", Static)
        header = self.query_one("#preview-header", Static)
        footer = self.query_one("#preview-footer", Static)
        
        header.update("❓ Help & Keyboard Shortcuts")
        footer.update("Press h again to close help")
        
        help_text = """[bold cyan]╔═══════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║          FILE MANAGER - HELP & SHORTCUTS          ║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════════════════════╝[/bold cyan]

[bold yellow]🎯 Navigation[/bold yellow]
  [green]↑ / ↓[/green]         Move up/down in file tree
  [green]← / →[/green]         Collapse/expand folders
  [green]Enter[/green]         Select file or folder
  [green]Home[/green]          Jump to top of list
  [green]End[/green]           Jump to bottom of list
  [green]Page Up/Down[/green]  Scroll faster

[bold yellow]⚡ Commands[/bold yellow]
  [green]q[/green]             Quit application
  [green]r[/green]             Refresh directory tree
  [green]h[/green] or [green]?[/green]       Toggle this help screen
  [green]Ctrl+C[/green]        Force quit
  [green]Esc[/green]           Clear selection

[bold yellow]👁️  Preview Pane[/bold yellow]
  • Displays file contents (text files)
  • Shows directory contents (folders)
  • File size and path information
  • Automatic text/binary detection
  • 1MB file size limit for performance

[bold yellow]📊 Status Information[/bold yellow]
  • Top bar: Current file/folder name
  • Bottom bar: File size or item count
  • Tree footer: Current directory path

[bold yellow]🎨 Features[/bold yellow]
  • Dual-pane layout for easy navigation
  • Syntax highlighting (coming soon)
  • File operations (coming soon)
  • Search and filter (coming soon)
  • Bookmarks (coming soon)

[bold yellow]💡 Tips[/bold yellow]
  • Use keyboard for fastest navigation
  • Preview updates automatically on selection
  • Large files show size instead of content
  • Binary files are detected automatically

[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]
[dim]Press [bold]h[/bold] to close this help screen[/dim]
        """
        preview.update(help_text)
    
    def action_clear_selection(self) -> None:
        """Clear current selection."""
        preview = self.query_one("#preview-content", Static)
        header = self.query_one("#preview-header", Static)
        footer = self.query_one("#preview-footer", Static)
        tree_footer = self.query_one("#tree-footer", Static)
        
        header.update("👁️  Preview")
        footer.update("Ready")
        tree_footer.update(f"🏠 {self.current_path}")
        preview.update(self._get_welcome_text())
        self.selected_file = None
