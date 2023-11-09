#!/usr/bin/env python
# encoding: utf8

"""
A simple CLI for the automata package.

To run as a script: `python -m automata.cli`
"""


import click
import time
import sys

from .core import CellularAutomata


DEFAULT_BASE = 2
DEFAULT_INITIAL_CONDITIONS = '1'
DEFAULT_FRAME_WIDTH = 101
DEFAULT_FRAME_STEPS = 50
DEFAULT_BOUNDARY_CONDITION = 'zero'

DEFAULT_RUN_DELAY = 0.1
DEFAULT_DISPLAY_FORMAT = 'png'


def _print_over(s: str, backup: bool = True, delay: float = DEFAULT_RUN_DELAY) -> None:
    if backup:
        print('', end='\r')
        print("\033[F" * (s.count('\n')+2))
    print(s)
    sys.stdout.flush()
    time.sleep(delay)


def automaton_options(f):
    """
    Decorator to hold common options for reuse.
    """
    options = [
        click.option('--rule', '-r', type=int,
                     required=True,
                     help="The rule number for the cellular automaton."),
        click.option('--initial_conditions', '-i', type=str,
                     default='1',
                     help=f"The initial condition of the cellular automaton as a string of digits "
                          f"(default={DEFAULT_INITIAL_CONDITIONS})."),
        click.option('--base', '-b', type=int,
                     default=2,
                     help=f"The base to be used for the cellular automaton "
                          f"(default={DEFAULT_BASE})."),
        click.option('--frame_width', '-w', type=int,
                     default=101,
                     help=f"The width of the cellular automaton frame "
                          f"default={DEFAULT_FRAME_WIDTH})."),
        click.option('--frame_steps', '-s', type=int,
                     default=50,
                     help=f"The number of steps to simulate the cellular automaton for "
                          f"(default={DEFAULT_FRAME_STEPS})."),
        click.option('--boundary_condition', '-c', type=click.Choice(['zero', 'periodic', 'one']),
                     default='zero',
                     help=f"The type of boundary condition to apply "
                          f"(default='{DEFAULT_BOUNDARY_CONDITION}').")
    ]
    for option in reversed(options):
        f = option(f)
    return f


@click.group(context_settings=dict(help_option_names=['-h', '--help']),
             help='A simple CLI for displaying cellular automata.')
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command(help="Displays the automaton as text.")
@automaton_options
def show(rule: int, initial_conditions: str, base: int,
         frame_width: int, frame_steps: int, boundary_condition: str) -> None:
    automaton = CellularAutomata(rule, initial_conditions, base, frame_width, frame_steps, boundary_condition)
    print(automaton)


# noinspection PyProtectedMember
@cli.command(help="Displays an automaton run as text, step by step.")
@automaton_options
@click.option('--delay', '-D', type=float, default=DEFAULT_RUN_DELAY,
              help=f"Delay between steps in seconds (default={DEFAULT_RUN_DELAY}).")
def run(rule: int, initial_conditions: str, base: int,
        frame_width: int, frame_steps: int, boundary_condition: str,
        delay: float) -> None:
    automaton = CellularAutomata(rule, initial_conditions, base, frame_width, frame_steps, boundary_condition)
    print()
    for row_str in [''.join(row) for row in automaton._lattice]:
        _print_over(row_str, delay=delay)


# noinspection PyProtectedMember
@cli.command(help="Draws the cellular automaton and saves it as an image file.")
@automaton_options
@click.option('--output_format', '-F', type=click.Choice(['png', 'jpg', 'svg']), default='png',
              help=f"The output format for the image file (default='{DEFAULT_DISPLAY_FORMAT}').")
def draw(rule: int, initial_conditions: str, base: int,
         frame_width: int, frame_steps: int, boundary_condition: str,
         output_format: str) -> None:
    automaton = CellularAutomata(rule, initial_conditions, base, frame_width, frame_steps, boundary_condition)
    filename = (f'automaton-{rule}-{initial_conditions}-{base}-'
                f'{frame_width}-{frame_steps}-{boundary_condition}.{output_format}')

    if output_format == 'png':
        img_data = automaton._repr_png_()
    elif output_format == 'jpg':
        img_data = automaton._repr_jpeg_()
    elif output_format == 'svg':
        img_data = automaton._repr_svg_()

    with open(filename, 'wb') as file:
        file.write(img_data)
        print(f'Automaton saved to {filename}')


if __name__ == '__main__':
    cli()
