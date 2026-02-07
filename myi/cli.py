import click
import json
from decimal import Decimal
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from .core import IncomeConfig
from .display import MyiDisplay

console = Console()
CONFIG_PATH = Path.home() / ".myi" / "config.json"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def get_default_config() -> IncomeConfig:
    saved = load_config()
    return IncomeConfig(
        annual_salary=Decimal(str(saved.get("salary", 50000))),
        currency=saved.get("currency", "$"),
        side_income=Decimal(str(saved.get("side", 0))),
        passive_income=Decimal(str(saved.get("passive", 0)))
    )


@click.group(invoke_without_command=True)
@click.option("--salary", "-s", type=float, help="Annual salary")
@click.option("--currency", "-c", default="$", help="Currency symbol")
@click.option("--side", type=float, default=0, help="Side income annually")
@click.option("--passive", "-p", type=float, default=0, help="Passive income annually")
@click.option("--once", "-o", is_flag=True, help="Show once and exit")
@click.pass_context
def cli(ctx, salary, currency, side, passive, once):
    """
    💰 MYI - Watch your income grow in real-time!
    
    Examples:
        myi                    # Use saved config or defaults
        myi -s 100000          # Set $100k salary
        myi -s 80000 --side 20000 -p 5000
        myi config             # Interactive configuration
    """
    if ctx.invoked_subcommand is None:
        config = get_default_config()
        
        if salary is not None:
            config.annual_salary = Decimal(str(salary))
        if currency != "$":
            config.currency = currency
        if side != 0:
            config.side_income = Decimal(str(side))
        if passive != 0:
            config.passive_income = Decimal(str(passive))
        
        if any([salary is not None, currency != "$", side != 0, passive != 0]):
            save_config({
                "salary": float(config.annual_salary),
                "currency": config.currency,
                "side": float(config.side_income),
                "passive": float(config.passive_income)
            })
        
        display = MyiDisplay(config)
        
        if once:
            display.run_once()
        else:
            display.run_live()


@cli.command()
@click.option("--salary", prompt="Annual Salary", type=float)
@click.option("--currency", prompt="Currency Symbol", default="$")
@click.option("--side", prompt="Side Income (annual)", default=0.0)
@click.option("--passive", prompt("Passive Income (annual)", default=0.0)
def config(salary, currency, side, passive):
    """Interactive configuration setup"""
    config_data = {
        "salary": salary,
        "currency": currency,
        "side": side,
        "passive": passive
    }
    save_config(config_data)
    
    total = salary + side + passive
    per_sec = total / (8 * 3600 * 250)
    
    console.print(Panel(
        f"[bold green]Configuration saved![/]\n\n"
        f"Total Annual Income: [bright_cyan]{currency}{total:,.2f}[/]\n"
        f"Estimated per second: [bright_green]{currency}{per_sec:.4f}[/]",
        title="[bright_yellow]Myi Config[/]",
        border_style="green"
    ))


@cli.command()
def demo():
    """Run with demo data"""
    config = IncomeConfig(
        annual_salary=Decimal("180000"),
        side_income=Decimal("25000"),
        passive_income=Decimal("5000"),
        currency="$"
    )
    display = MyiDisplay(config)
    console.print("[dim]Running demo mode...[/]")
    display.run_live()


@cli.command()
def reset():
    """Reset configuration to defaults"""
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()
    console.print("[green]Configuration reset to defaults![/]")


if __name__ == "__main__":
    cli()
