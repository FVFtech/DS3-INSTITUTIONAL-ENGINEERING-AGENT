import typer
from rich.console import Console
from rich.table import Table
from .registry import load_sources
from .monitor import sync_sources, REPORT

app = typer.Typer(help="DS3 standards intelligence and engineering guardrails")
console = Console()

@app.command()
def sources() -> None:
    table = Table("ID", "Publisher", "Status", "DS3 impact", "Source")
    for s in load_sources():
        table.add_row(s["id"], s["publisher"], s["status"],
                      ", ".join(s["ds3_impact"]), s["title"])
    console.print(table)

@app.command()
def sync() -> None:
    result = sync_sources(load_sources())
    console.print(f"Checked {len(result['sources'])} sources; review events: {len(result['events'])}")
    console.print(f"Report: {REPORT}")

@app.command()
def report() -> None:
    if not REPORT.exists():
        console.print("No report yet. Run: ds3-agent sync")
        raise typer.Exit(1)
    console.print(REPORT.read_text(encoding="utf-8"))

@app.command("check-config")
def check_config() -> None:
    console.print(f"Configuration valid: {len(load_sources())} HTTPS sources, unique IDs.")


@app.command()
def evolve(target: str = typer.Argument(..., help="Allowlisted prompt target")) -> None:
    """Prepare an evolution candidate for human review; never activates it."""
    from .evolution import EvolutionBlocked, evolve_prompt
    try: candidate=evolve_prompt(target)
    except (EvolutionBlocked, ValueError) as exc:
        console.print(f"[red]Blocked:[/red] {exc}")
        raise typer.Exit(2) from exc
    console.print(f"Candidate written for human review only: {candidate}")
