#!/usr/bin/env python
# encoding: utf8

"""
A simple CLI for the automata package.

.. note::
    Any additional note.
"""

import click
from automata.core import CellularAutomata

@click.group()
def cli():
    pass

@cli.command()
@click.option('--rule', type=int, required=True)
@click.option('--initial_conditions', type=str, required=True)
@click.option('--base', type=int, default=2)
@click.option('--frame_width', type=int, default=101)
@click.option('--frame_steps', type=int, default=200)
@click.option('--boundary_condition', type=click.Choice(['zero', 'periodic', 'one']), default='zero')
def generate(rule, initial_conditions, base, frame_width, frame_steps, boundary_condition):
    global automaton
    automaton = CellularAutomata(rule, initial_conditions, base, frame_width, frame_steps, boundary_condition)

@cli.command()
@click.option('--output_format', type=click.Choice(['png', 'jpg', 'svg']), default='png')
def display(output_format):
    if output_format == 'png':
        print(automaton._repr_png_())
    elif output_format == 'jpg':
        print(automaton._repr_jpeg_())
    elif output_format == 'svg':
        print(automaton._repr_svg_())

if __name__ == '__main__':
    cli()
