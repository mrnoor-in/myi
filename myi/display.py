import time
from decimal import Decimal
from typing import Optional
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.align import Align
from rich import box

from .core import IncomeConfig, IncomeTracker


class MyiDisplay:
    """Beautiful terminal display for myi"""
    
    def __init__(self, config: IncomeConfig):
        self.config = config
        self.console = Console()
        self.tracker: Optional[IncomeTracker] = None
        self.live: Optional[Live] = None
    
    def _format_money(self, amount: Decimal) -> str:
        return f"{self.config.currency}{amount:,.4f}"
    
    def _create_header(self) -> Panel:
        title = Text("💰 MYI ", style="bold bright_yellow")
        title.append("Live Income Tracker", style="bright_white")
        subtitle = Text("Watching your wealth grow in real-time", style="dim italic")
        
        return Panel(
            Align.center(Group(title, subtitle)),
            box=box.DOUBLE,
            border_style="bright_cyan",
            padding=(1, 2)
        )
    
    def _create_stats_panel(self, accumulated: Decimal, elapsed: float) -> Panel:
        per_sec = self.config.per_second
        per_min = per_sec * 60
        per_hour = per_sec * 3600
        per_day = per_hour * 8
        
        main_counter = Text(self._format_money(accumulated), style="bold bright_green")
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Label", style="dim cyan", justify="right")
        table.add_column("Value", style="bright_white")
        table.add_column("Rate", style="dim", justify="right")
        
        table.add_row("⏱️  Session", f"{elapsed:.1f}s", "")
        table.add_row("⚡ Per Second", self._format_money(per_sec), "base rate")
        table.add_row("📊 Per Minute", self._format_money(per_min), f"+{self._format_money(per_min)}")
        table.add_row("🕐 Per Hour", self._format_money(per_hour), f"+{self._format_money(per_hour)}")
        table.add_row("📅 Work Day", self._format_money(per_day), f"+{self._format_money(per_day)}")
        
        content = Group(
            Align.center(Text("ACCUMULATED", style="bold underline bright_cyan")),
            Align.center(main_counter),
            Text(""),
            table
        )
        
        return Panel(
            content,
            title="[bright_yellow]Real-Time Earnings[/]",
            border_style="bright_green",
            box=box.ROUNDED
        )
    
    def _create_breakdown_panel(self) -> Panel:
        table = Table(box=None, show_header=False)
        table.add_column("Source", style="cyan")
        table.add_column("Annual", style="bright_white", justify="right")
        table.add_column("Per Sec", style="dim", justify="right")
        
        total_sec = self.config.per_second
        
        if self.config.annual_salary > 0:
            pct = (self.config.annual_salary / self.config.total_annual * 100) if self.config.total_annual > 0 else 0
            table.add_row("💼 Salary", f"{self.config.currency}{self.config.annual_salary:,.0f}", f"{pct:.1f}%")
        
        if self.config.side_income > 0:
            pct = (self.config.side_income / self.config.total_annual * 100) if self.config.total_annual > 0 else 0
            table.add_row("🚀 Side Income", f"{self.config.currency}{self.config.side_income:,.0f}", f"{pct:.1f}%")
            
        if self.config.passive_income > 0:
            pct = (self.config.passive_income / self.config.total_annual * 100) if self.config.total_annual > 0 else 0
            table.add_row("📈 Passive", f"{self.config.currency}{self.config.passive_income:,.0f}", f"{pct:.1f}%")
        
        table.add_row("", "", "")
        table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold bright_green]{self.config.currency}{self.config.total_annual:,.0f}[/]",
            f"[bold]{total_sec:.4f}/s[/]"
        )
        
        return Panel(
            table,
            title="[bright_cyan]Income Breakdown[/]",
            border_style="cyan",
            box=box.ROUNDED
        )
    
    def _create_footer(self) -> Text:
        controls = Text()
        controls.append("Controls: ", style="dim")
        controls.append("[Ctrl+C]", style="bold bright_yellow")
        controls.append(" Quit  ", style="dim")
        return controls
    
    def generate_layout(self, accumulated: Decimal = Decimal("0"), elapsed: float = 0) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="main"),
            Layout(name="footer", size=1)
        )
        layout["main"].split_row(
            Layout(name="stats", ratio=2),
            Layout(name="breakdown", ratio=1)
        )
        layout["header"].update(self._create_header())
        layout["stats"].update(self._create_stats_panel(accumulated, elapsed))
        layout["breakdown"].update(self._create_breakdown_panel())
        layout["footer"].update(Align.center(self._create_footer()))
        return layout
    
    def run_live(self):
        self.tracker = IncomeTracker(self.config)
        
        with Live(self.generate_layout(), refresh_per_second=10, screen=True) as live:
            self.live = live
            
            def update_display(acc, elapsed):
                live.update(self.generate_layout(acc, elapsed))
            
            self.tracker.on_update(update_display)
            self.tracker.start()
            
            try:
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass
            finally:
                self.tracker.stop()
                self._show_summary()
    
    def _show_summary(self):
        if self.tracker:
            final, elapsed = self.tracker.get_current()
            self.console.print()
            self.console.print(Panel(
                f"[bold green]Session Complete![/]\n\n"
                f"You earned [bold bright_green]{self._format_money(final)}[/] "
                f"in [cyan]{elapsed:.1f}[/] seconds\n"
                f"That's [bold]{self._format_money(final / Decimal(str(elapsed)) * 3600)}[/] per hour!",
                title="[bright_yellow]Summary[/]",
                border_style="green"
            ))
    
    def run_once(self):
        layout = self.generate_layout()
        self.console.print(layout)
