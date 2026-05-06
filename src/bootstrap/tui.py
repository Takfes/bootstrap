"""Optional Textual TUI for the bootstrap CLI.

Install with: pip install 'bootstrap[tui]'

Public API:
  run_tui_new(project_name, components, state) -> (context, components) | None
  run_tui_add(components, state) -> list[str] | None
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, SelectionList, Static
from textual.widgets.selection_list import Selection

from .components import ComponentSpec
from .detector import ProjectState


# ---------------------------------------------------------------------------
# Context form screen (used in 'new' mode)
# ---------------------------------------------------------------------------

class ContextFormScreen(Screen[dict[str, str] | None]):
    """Collect template variables via a form before component selection."""

    CSS = """
    ContextFormScreen {
        align: center middle;
    }
    #form-panel {
        width: 72;
        height: auto;
        border: solid $primary;
        padding: 1 2;
        background: $surface;
    }
    #form-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    .field-label {
        margin-top: 1;
        color: $text-muted;
    }
    #btn-row {
        margin-top: 2;
        height: auto;
        align: right middle;
    }
    Button { margin-left: 1; }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, project_name: str, state: ProjectState | None = None) -> None:
        self._project_name = project_name
        self._state = state
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="form-panel"):
            yield Label(f"New project: {self._project_name}", id="form-title")

            yield Label("GitHub org / username", classes="field-label")
            yield Input(
                value=(self._state.github_org if self._state and self._state.github_org else ""),
                placeholder="e.g. myorg",
                id="github_org",
            )

            yield Label("Author name", classes="field-label")
            yield Input(placeholder="Jane Doe", id="author")

            yield Label("Author email", classes="field-label")
            yield Input(placeholder="jane@example.com", id="author_email")

            yield Label("One-line description (optional)", classes="field-label")
            yield Input(placeholder="A great tool", id="description")

            yield Label("Minimum Python version", classes="field-label")
            yield Input(value="3.11", placeholder="3.11", id="python_version")

            with Horizontal(id="btn-row"):
                yield Button("Cancel", variant="error", id="cancel")
                yield Button("Next →", variant="primary", id="next")
        yield Footer()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "next":
            python_version = self.query_one("#python_version", Input).value.strip() or "3.11"
            context = {
                "project_name": self._project_name,
                "package_name": self._project_name.lower().replace("-", "_").replace(" ", "_"),
                "repo_name": self._project_name.lower().replace("_", "-").replace(" ", "-"),
                "github_org": self.query_one("#github_org", Input).value.strip(),
                "author": self.query_one("#author", Input).value.strip(),
                "author_email": self.query_one("#author_email", Input).value.strip(),
                "description": self.query_one("#description", Input).value.strip(),
                "python_version": python_version,
                "python_version_nodot": python_version.replace(".", ""),
            }
            self.dismiss(context)


# ---------------------------------------------------------------------------
# Component selection screen (used in both 'new' and 'add' modes)
# ---------------------------------------------------------------------------

class ComponentSelectScreen(Screen[list[str] | None]):
    """Interactive component checklist."""

    BINDINGS = [
        ("ctrl+a", "select_all", "Select all"),
        ("ctrl+n", "select_none", "Clear all"),
        ("escape", "cancel", "Cancel"),
    ]

    CSS = """
    ComponentSelectScreen {
        align: center middle;
    }
    #select-panel {
        width: 90;
        height: 80%;
        border: solid $primary;
        padding: 1 2;
        background: $surface;
    }
    #select-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 0;
    }
    #hint {
        color: $text-muted;
        margin-bottom: 1;
    }
    SelectionList {
        height: 1fr;
        border: solid $panel;
    }
    #btn-row {
        margin-top: 1;
        height: auto;
        align: right middle;
    }
    Button { margin-left: 1; }
    """

    def __init__(
        self,
        components: list[ComponentSpec],
        installed: set[str] | None = None,
        title: str = "Select components to install",
    ) -> None:
        self._components = components
        self._installed = installed or set()
        self._title = title
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="select-panel"):
            yield Label(self._title, id="select-title")
            yield Static(
                "Space/click to toggle  •  Ctrl+A select all  •  Ctrl+N clear  •  Esc cancel",
                id="hint",
            )

            selections: list[Selection] = []
            for spec in self._components:
                installed_badge = " [installed]" if spec.name in self._installed else ""
                deps = f" ← needs: {', '.join(spec.requires)}" if spec.requires else ""
                label = f"{spec.name:<15}{installed_badge}  {spec.description}{deps}"
                selections.append(Selection(label, spec.name))

            yield SelectionList(*selections, id="component-list")

            with Horizontal(id="btn-row"):
                yield Button("Cancel", variant="error", id="cancel")
                yield Button("Install selected", variant="primary", id="install")
        yield Footer()

    def action_select_all(self) -> None:
        sl = self.query_one(SelectionList)
        for spec in self._components:
            sl.select(spec.name)

    def action_select_none(self) -> None:
        self.query_one(SelectionList).deselect_all()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "install":
            sl = self.query_one(SelectionList)
            self.dismiss(list(sl.selected))


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

class BootstrapApp(App):
    """Textual bootstrap app — orchestrates form and selection screens."""

    TITLE = "bootstrap"
    SUB_TITLE = "Python project scaffolding"

    def __init__(
        self,
        mode: str,
        components: list[ComponentSpec],
        state: ProjectState,
        project_name: str = "",
    ) -> None:
        self._mode = mode
        self._components = components
        self._state = state
        self._project_name = project_name
        self._context: dict[str, str] | None = None
        super().__init__()

    def on_mount(self) -> None:
        if self._mode == "new":
            self.push_screen(
                ContextFormScreen(self._project_name, self._state),
                self._on_context_done,
            )
        else:
            self.push_screen(
                ComponentSelectScreen(
                    self._components,
                    self._state.installed_components,
                    title="Select components to add",
                ),
                self._on_components_done_add,
            )

    def _on_context_done(self, context: dict[str, str] | None) -> None:
        if context is None:
            self.exit(None)
            return
        self._context = context
        self.push_screen(
            ComponentSelectScreen(
                self._components,
                self._state.installed_components,
                title="Select components to install",
            ),
            self._on_components_done_new,
        )

    def _on_components_done_new(self, selected: list[str] | None) -> None:
        if selected is None or self._context is None:
            self.exit(None)
        else:
            self.exit((self._context, selected))

    def _on_components_done_add(self, selected: list[str] | None) -> None:
        self.exit(selected)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_tui_new(
    project_name: str,
    components: list[ComponentSpec],
    state: ProjectState,
) -> tuple[dict[str, str], list[str]] | None:
    """Run the TUI for 'bootstrap new'.

    Returns:
        (context_dict, selected_component_names) on confirm, None on cancel.
    """
    app = BootstrapApp(
        mode="new",
        components=components,
        state=state,
        project_name=project_name,
    )
    return app.run()


def run_tui_add(
    components: list[ComponentSpec],
    state: ProjectState,
) -> list[str] | None:
    """Run the TUI for 'bootstrap add'.

    Returns:
        List of selected component names on confirm, None on cancel.
    """
    app = BootstrapApp(mode="add", components=components, state=state)
    return app.run()
