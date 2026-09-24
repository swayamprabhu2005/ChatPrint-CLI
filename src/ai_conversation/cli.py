"""Command-line interface for AI Conversation CLI."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from ai_conversation import __app_name__, __version__
from ai_conversation.errors import AIConversationError
from ai_conversation.extraction.validator import validate_conversation
from ai_conversation.input.detector import InputFormat, detect_format
from ai_conversation.input.html_reader import read_html_file
from ai_conversation.input.mhtml_reader import read_mhtml_file
from ai_conversation.installer.verification import run_doctor_check
from ai_conversation.pdf.renderer import render_conversation_to_pdf
from ai_conversation.providers import detect_best_provider, get_provider
from ai_conversation.utils.files import resolve_output_pdf_path

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

console = Console()
err_console = Console(stderr=True)


def _get_status_icon(ok: bool) -> str:
    encoding = (getattr(sys.stdout, "encoding", "") or "").lower()
    if "utf" in encoding:
        return "[green]✓[/green]" if ok else "[red]✗[/red]"
    return "[green][OK][/green]" if ok else "[red][FAIL][/red]"


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    version=__version__,
    prog_name=__app_name__,
    message="%(prog)s %(version)s",
)
def cli():
    """Convert locally saved AI conversation webpages into clean, readable PDFs."""


@cli.command()
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "-o",
    "--output",
    "output_dir",
    type=click.Path(file_okay=False, path_type=Path),
    help="Target directory for generated PDF.",
)
@click.option(
    "--output-file",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Explicit destination PDF file path.",
)
@click.option(
    "-s",
    "--source",
    default="auto",
    type=click.Choice(["auto", "gemini", "chatgpt"], case_sensitive=False),
    help="AI conversation source provider (default: auto).",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Overwrite existing output PDF file if it already exists.",
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Show verbose technical debug diagnostic output.",
)
def convert(
    input_path: Path,
    output_dir: Path | None,
    output_file: Path | None,
    source: str,
    force: bool,
    debug: bool,
):
    """Convert a saved .mhtml, .mht, .html, or .htm conversation webpage to PDF."""
    try:
        console.print("[bold cyan]AI Conversation CLI[/bold cyan]")
        console.print("[dim]────────────────────────────────────────[/dim]")

        # 1. Format Detection & Reading
        fmt = detect_format(input_path)
        console.print(f"[bold]Input:[/bold] {input_path.name}")
        console.print(f"[bold]Format:[/bold] {fmt.value.upper()}")

        console.print("[dim][1/4] Reading saved webpage...[/dim]")
        if fmt == InputFormat.MHTML:
            doc = read_mhtml_file(input_path)
        else:
            doc = read_html_file(input_path)

        # 2. Source Provider Detection
        console.print("[dim][2/4] Detecting conversation source...[/dim]")
        soup = doc.soup
        if source.lower() == "auto":
            provider, confidence = detect_best_provider(soup, doc.raw_html, doc.metadata)
        else:
            provider = get_provider(source)
            confidence = provider.detect_confidence(soup, doc.raw_html, doc.metadata)

        console.print(f"[bold]Source:[/bold] {provider.display_name}")

        # 3. Conversation Extraction
        console.print("[dim][3/4] Extracting conversation & cleaning UI...[/dim]")
        conversation = provider.extract(
            soup=soup,
            resources=doc.resources,
            original_filename=input_path.name,
        )

        warnings = validate_conversation(conversation, confidence=confidence)
        if warnings:
            for w in warnings:
                console.print(f"[yellow]Warning:[/yellow] {w}")

        if debug:
            console.print(f"[cyan][Debug][/cyan] Extracted turns: {len(conversation.messages)}")
            console.print(f"[cyan][Debug][/cyan] User messages: {conversation.user_messages_count}")
            console.print(f"[cyan][Debug][/cyan] Assistant messages: {conversation.assistant_messages_count}")
            console.print(f"[cyan][Debug][/cyan] Confidence: {confidence:.2f}")

        # 4. PDF Generation
        console.print("[dim][4/4] Generating PDF...[/dim]")
        dest_pdf = resolve_output_pdf_path(
            input_file=input_path,
            output_dir=output_dir,
            output_file=output_file,
            force=force,
        )

        final_path = render_conversation_to_pdf(conversation, dest_pdf)

        success_icon = _get_status_icon(True)
        console.print(f"\n[bold green]{success_icon} PDF generated successfully[/bold green]\n")
        console.print("[bold]Output:[/bold]")
        console.print(f"[green]{final_path.resolve()}[/green]\n")
        sys.exit(0)

    except AIConversationError as e:
        err_console.print(f"\n[bold red]Error:[/bold red] {e.message}")
        if e.suggestion:
            err_console.print(f"[yellow]Suggested action:[/yellow] {e.suggestion}")
        if debug:
            err_console.print_exception()
        sys.exit(1)
    except Exception as e:
        err_console.print(f"\n[bold red]Unexpected Error:[/bold red] {e}")
        if debug:
            err_console.print_exception()
        sys.exit(2)


@cli.command()
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "-s",
    "--source",
    default="auto",
    type=click.Choice(["auto", "gemini", "chatgpt"], case_sensitive=False),
    help="AI conversation source provider (default: auto).",
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Show verbose technical debug diagnostic output.",
)
def inspect(input_path: Path, source: str, debug: bool):
    """Inspect and analyze a saved conversation without generating a PDF."""
    try:
        console.print("[bold cyan]AI Conversation Inspection[/bold cyan]")
        console.print("[dim]────────────────────────────────────────[/dim]")

        fmt = detect_format(input_path)
        if fmt == InputFormat.MHTML:
            doc = read_mhtml_file(input_path)
        else:
            doc = read_html_file(input_path)

        soup = doc.soup
        if source.lower() == "auto":
            provider, confidence = detect_best_provider(soup, doc.raw_html, doc.metadata)
        else:
            provider = get_provider(source)
            confidence = provider.detect_confidence(soup, doc.raw_html, doc.metadata)

        conversation = provider.extract(
            soup=soup,
            resources=doc.resources,
            original_filename=input_path.name,
        )

        table = Table(show_header=False, box=None)
        table.add_column("Property", style="bold")
        table.add_column("Value")

        table.add_row("Input file:", str(input_path.resolve()))
        table.add_row("Format:", fmt.value.upper())
        table.add_row("Title:", conversation.title)
        table.add_row("Detected provider:", provider.display_name)
        table.add_row("Confidence:", f"{int(confidence * 100)}%")
        table.add_row("Total messages:", str(conversation.total_messages_count))
        table.add_row("User messages:", str(conversation.user_messages_count))
        table.add_row("Assistant messages:", str(conversation.assistant_messages_count))
        table.add_row("Embedded resources:", str(len(doc.resources)))

        console.print(table)

        warnings = validate_conversation(conversation, confidence=confidence)
        if warnings:
            console.print("\n[bold yellow]Warnings:[/bold yellow]")
            for w in warnings:
                console.print(f"  • {w}")

        sys.exit(0)

    except AIConversationError as e:
        err_console.print(f"\n[bold red]Error:[/bold red] {e.message}")
        if e.suggestion:
            err_console.print(f"[yellow]Suggested action:[/yellow] {e.suggestion}")
        if debug:
            err_console.print_exception()
        sys.exit(1)
    except Exception as e:
        err_console.print(f"\n[bold red]Unexpected Error:[/bold red] {e}")
        if debug:
            err_console.print_exception()
        sys.exit(2)


@cli.command()
@click.option("-v", "--verbose", is_flag=True, help="Display verbose diagnostic details.")
def doctor(verbose: bool):
    """Run comprehensive system health checks for AI Conversation CLI."""
    console.print("[bold cyan]AI Conversation CLI Doctor[/bold cyan]\n")

    report = run_doctor_check()
    for check in report.checks:
        icon = _get_status_icon(check.status)
        console.print(f"{icon} {check.name}: {check.message}")
        if verbose and check.details:
            console.print(f"    [dim]{check.details}[/dim]")

    console.print()
    if report.all_ok:
        console.print("[bold green]System ready.[/bold green]")
        sys.exit(0)
    else:
        console.print("[bold yellow]System has warnings or issues.[/bold yellow]")
        sys.exit(1)


def main():
    """Main CLI entry point function."""
    cli()


if __name__ == "__main__":
    main()
