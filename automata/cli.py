#!/usr/bin/env python
# encoding: utf8

"""
A simple CLI for the automata package.

To run as a script: `python -m automata.clip`
"""

import click
from .core import CellularAutomata


@click.group()
def cli():
    pass


@cli.command()
@click.option('--rule', type=int, required=True)
@click.option('--initial_conditions', type=str, default='1')
@click.option('--base', type=int, default=2)
@click.option('--frame_width', type=int, default=101)
@click.option('--frame_steps', type=int, default=50)
@click.option('--boundary_condition', type=click.Choice(['zero', 'periodic', 'one']), default='zero')
def show(rule: int, initial_conditions: str, base: int,
         frame_width: int, frame_steps: int, boundary_condition: str) -> None:
    automaton = CellularAutomata(rule, initial_conditions, base, frame_width, frame_steps, boundary_condition)
    print(automaton)


# noinspection PyProtectedMember
@cli.command()
@click.option('--rule', type=int, required=True)
@click.option('--initial_conditions', type=str, default='1')
@click.option('--base', type=int, default=2)
@click.option('--frame_width', type=int, default=101)
@click.option('--frame_steps', type=int, default=50)
@click.option('--boundary_condition', type=click.Choice(['zero', 'periodic', 'one']), default='zero')
@click.option('--output_format', type=click.Choice(['png', 'jpg', 'svg']), default='png')
def draw(rule: int, initial_conditions: str, base: int,
         frame_width: int, frame_steps: int, boundary_condition: str,
         output_format: str) -> None:
    automaton = CellularAutomata(rule, initial_conditions, base, frame_width, frame_steps, boundary_condition)
    filename = (f'automaton-{rule}-{initial_conditions}-{base}-'
                f'{frame_width}-{frame_steps}-{boundary_condition}.{output_format}')
    if output_format == 'png':
        automaton._repr_png_().save(f'{filename}.png')
    elif output_format == 'jpg':
        automaton._repr_jpeg_().save(f'{filename}.jpg')
    elif output_format == 'svg':
        automaton._repr_svg_().save(f'{filename}.svg')
    print(f'Automaton saved to {filename}')
# TBD - Above does not work <<<


if __name__ == '__main__':
    cli()
