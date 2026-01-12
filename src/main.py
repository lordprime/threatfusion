"""
ThreatFusion CLI
Main command-line interface for threat intelligence enrichment
"""
import click
import time
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

from src.config import config
from src.validators import IndicatorValidator
from src.models import IndicatorType
from src.agents.virustotal import VirusTotalAgent
from src.agents.shodan import ShodanAgent
from src.agents.censys import CensysAgent
from src.agents.otx import OTXAgent
from src.agents.abuseipdb import AbuseIPDBAgent
from src.fusion.orchestrator import EnrichmentOrchestrator
from src.fusion.scorer import RiskScorer
from src.reporting.generator import ReportGenerator

console = Console()


def initialize_agents():
    """Initialize all configured threat intelligence agents"""
    agents = []
    api_config = config.api_config
    
    if api_config.vt_api_key:
        agents.append(VirusTotalAgent(api_config.vt_api_key))
    
    if api_config.shodan_api_key:
        agents.append(ShodanAgent(api_config.shodan_api_key))
    
    if api_config.censys_api_id and api_config.censys_api_secret:
        agents.append(CensysAgent(api_config.censys_api_id, api_config.censys_api_secret))
    
    if api_config.otx_api_key:
        agents.append(OTXAgent(api_config.otx_api_key))
    
    if api_config.abuseipdb_api_key:
        agents.append(AbuseIPDBAgent(api_config.abuseipdb_api_key))
    
    if not agents:
        console.print("[red]❌ No API keys configured! Please set up .env file.[/red]")
        console.print("[yellow]Run: cp .env.example .env and add your API keys[/yellow]")
        raise click.Abort()
    
    return agents


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    ThreatFusion - Automated Threat Intelligence Aggregator
    
    Quickly enrich malware hashes, IPs, and domains with intelligence
    from multiple sources including VirusTotal, Shodan, Censys, OTX, and more.
    """
    pass


@cli.command()
@click.argument('indicator')
@click.option('--output', '-o', type=click.Choice(['text', 'json', 'html']), default='text', help='Output format')
@click.option('--save', '-s', type=click.Path(), help='Save report to file')
@click.option('--timeout', '-t', type=int, default=30, help='Query timeout in seconds')
def enrich(indicator: str, output: str, save: str, timeout: int):
    """
    Enrich a threat indicator with intelligence from multiple sources
    
    Examples:
    
      threatfusion enrich d131dd02c5e6eec4693d61a8d9ca3759
      
      threatfusion enrich 8.8.8.8 --output json
      
      threatfusion enrich malware.com --save report.html
    """
    
    # Validate indicator
    try:
        validated = IndicatorValidator.validate(indicator)
    except ValueError as e:
        console.print(f"[red]❌ Invalid indicator: {e}[/red]")
        raise click.Abort()
    
    # Warn if private IP
    if validated.is_private:
        console.print(f"[yellow]⚠️  Warning: {indicator} is a private/non-routable IP address[/yellow]")
        console.print("[yellow]   External threat intelligence sources may not have data[/yellow]\n")
    
    # Display indicator info
    console.print(Panel(
        f"[bold cyan]Indicator:[/bold cyan] {indicator}\n"
        f"[bold cyan]Type:[/bold cyan] {validated.type.value}",
        title="🔍 ThreatFusion Analysis",
        border_style="cyan"
    ))
    
    # Initialize agents
    try:
        agents = initialize_agents()
    except click.Abort:
        return
    
    console.print(f"\n[bold green]✓[/bold green] Initialized {len(agents)} agents: {', '.join(a.name for a in agents)}\n")
    
    # Create orchestrator
    orchestrator = EnrichmentOrchestrator(agents, max_workers=config.app_config.max_workers)
    
    # Execute enrichment with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Querying {len(agents)} sources...", total=None)
        
        start_time = time.time()
        results = orchestrator.enrich_parallel(indicator, validated.type, timeout=timeout)
        execution_time = time.time() - start_time
        
        progress.update(task, completed=True)
    
    # Calculate risk score
    risk_score = RiskScorer.calculate_risk(results)
    
    # Generate report based on format
    if output == 'text':
        report = ReportGenerator.generate_text(indicator, results, risk_score, execution_time)
        console.print(report)
    
    elif output == 'json':
        report = ReportGenerator.generate_json(indicator, results, risk_score, execution_time)
        console.print(report)
    
    elif output == 'html':
        report = ReportGenerator.generate_html(indicator, results, risk_score, execution_time)
        
        if save:
            Path(save).write_text(report, encoding='utf-8')
            console.print(f"\n[green]✓ Report saved to: {save}[/green]")
        else:
            # Auto-save HTML
            filename = f"threatfusion_report_{indicator.replace(':', '_').replace('/', '_')}.html"
            Path(filename).write_text(report, encoding='utf-8')
            console.print(f"\n[green]✓ HTML report saved to: {filename}[/green]")
    
    # Save to file if specified
    if save and output != 'html':
        Path(save).write_text(report, encoding='utf-8')
        console.print(f"\n[green]✓ Report saved to: {save}[/green]")


@cli.command()
def config_check():
    """Check API configuration and show which services are available"""
    
    console.print(Panel(
        "[bold cyan]ThreatFusion Configuration Check[/bold cyan]",
        border_style="cyan"
    ))
    
    # Check API keys
    validation = config.validate_api_keys()
    
    table = Table(title="\nAPI Services Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details")
    
    for service, configured in validation.items():
        status = "✓ Configured" if configured else "✗ Not Configured"
        status_style = "green" if configured else "red"
        
        table.add_row(
            service.upper(),
            f"[{status_style}]{status}[/{status_style}]",
            "Ready" if configured else "Add API key to .env"
        )
    
    console.print(table)
    
    configured_count = sum(1 for v in validation.values() if v)
    console.print(f"\n[bold]Summary:[/bold] {configured_count}/{len(validation)} services configured")
    
    if configured_count == 0:
        console.print("\n[yellow]⚠️  No API keys configured. Copy .env.example to .env and add your keys.[/yellow]")


@cli.command()
def version():
    """Show ThreatFusion version and system info"""
    import sys
    
    console.print(Panel(
        f"[bold cyan]ThreatFusion v0.1.0[/bold cyan]\n\n"
        f"Python: {sys.version.split()[0]}\n"
        f"Platform: {sys.platform}",
        title="ℹ️  Version Info",
        border_style="cyan"
    ))


if __name__ == '__main__':
    cli()
