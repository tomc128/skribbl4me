import time

from rich import bar, box, print
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.pretty import Pretty
from rich.progress import Progress
from rich.table import Table

current_hint = '_____'
current_guess_progress = Progress(expand=True, get_time=lambda: 10)
wait_to_guess_task = current_guess_progress.add_task('[yellow]Waiting to guess...', total=100)
current_guess_progress.update(wait_to_guess_task, advance=10)

players = [
    ('Player 1', 0),
    ('Player 2', 100),
    ('Player 3', 800),
    ('Player 4', 1000),
    ('Player 5', 300),
    ('Player 6 (You)', 400),
]


player_table = Table(show_header=False, box=None)
player_table.add_column('Place', justify='left')
player_table.add_column('Name', justify='left')
player_table.add_column('Score', justify='right')

for i, (name, score) in enumerate(sorted(players, key=lambda x: x[1], reverse=True)):
    player_table.add_row(f'{i+1}.', name, str(score))


with open('default_words.txt') as f:
    guessed_words = [next(f).strip() for _ in range(10)]


console = Console()


layout = Layout()

layout.split_row(
    Layout(name='left', size=30),
    Layout(name='right', ratio=1),
)

layout['right'].split_column(
    Layout(Panel(Align(current_hint, align='center', vertical='middle'), title='Current Hint'), name='top', size=5),
    Layout(Panel(Pretty(guessed_words), title='Guessed Words'), name='guessed_words', ratio=1),
    Layout(Panel(current_guess_progress, padding=0, box=box.SIMPLE), name='status', size=3),
    Layout(Panel('console'), name='console', ratio=1),
)

layout['left'].split_column(
    Layout(Panel('Round 1/3\n30s remaining\nDrawer: Player 1', title='Game Stats'), name='game_stats', size=5),
    Layout(Panel(player_table, title='Players'), name='players'),
)



    



# with Live(screen=True, refresh_per_second=4) as live:
#     live.update(layout)

    # for _ in range(40):
    #     word += '!'
    #     time.sleep(0.5)
    #     layout['header'].update(Panel(word, title='skribbl4me'))
    #     live.update(layout)

print(layout)