import time

from rich import print
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel

word = "Hello World"


layout = Layout()

layout.split_column(
    Layout(Panel('Header', title='skribbl4me'), name="header", size=5),
    Layout(name="body", ratio=1),
    Layout(name="footer", size=5),
)

layout['body'].split(
    Layout(Panel('Hello')),
    Layout(Panel('World')),
)
    



with Live(screen=True, refresh_per_second=4) as live:
    for _ in range(40):
        word += '!'
        time.sleep(0.5)
        layout['header'].update(Panel(word, title='skribbl4me'))
        live.update(layout)