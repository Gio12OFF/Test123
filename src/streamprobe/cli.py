from __future__ import annotations

import asyncio
import json
from typing import Annotated

import typer

from streamprobe import __version__
from streamprobe.analyzer import StreamAnalyzer
from streamprobe.exceptions import StreamProbeError
from streamprobe.formatters import human_report

app = typer.Typer(
    name="streamprobe",
    help="Inspect and monitor HLS/DASH video streams.",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"streamprobe {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=version_callback, is_eager=True, help="Show version."),
    ] = None,
) -> None:
    """StreamProbe command line interface."""


@app.command()
def inspect(
    url: Annotated[str, typer.Argument(help="HLS .m3u8 or DASH .mpd URL")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Print machine-readable JSON.")
    ] = False,
    samples: Annotated[
        int, typer.Option("--samples", min=0, max=20, help="Segments to probe.")
    ] = 3,
    timeout: Annotated[
        float, typer.Option("--timeout", min=0.1, help="Request timeout in seconds.")
    ] = 10.0,
    allow_private: Annotated[
        bool, typer.Option(help="Allow localhost/private network targets.")
    ] = False,
) -> None:
    """Inspect one stream and print its health report."""
    try:
        report = asyncio.run(
            StreamAnalyzer(
                timeout=timeout, segment_samples=samples, allow_private=allow_private
            ).analyze(url)
        )
    except StreamProbeError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    typer.echo(
        json.dumps(report.model_dump(mode="json"), indent=2)
        if json_output
        else human_report(report)
    )


@app.command()
def serve(
    host: Annotated[str, typer.Option(help="Bind address.")] = "127.0.0.1",
    port: Annotated[int, typer.Option(min=1, max=65535, help="Bind port.")] = 8000,
) -> None:
    """Run the REST API and web dashboard (install streamprobe[api])."""
    try:
        import uvicorn
    except ImportError as exc:
        typer.echo("Install API dependencies with: pip install 'streamprobe[api]'", err=True)
        raise typer.Exit(code=2) from exc
    uvicorn.run("streamprobe.api:app", host=host, port=port)


if __name__ == "__main__":
    app()
