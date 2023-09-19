"""
A simple cellular automata based on those discussed in Wolfram's A New Kind of Science.
Currently limited to simple elementary (1D, multi-state, immediate neighbor) automata,
using various boundary conditions.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle
import matplotlib.gridspec as gridspec
from dataclasses import dataclass


class CellularAutomataError(ValueError):
    def __init__(self, *args: str):
        # super().__init__(", ".join(args).capitalize() + ".")
        super().__init__(", ".join(args) + ".")


# A simple class for specifying highlighting bounds
class HighlightBounds:
    def __init__(self, start_step=None, steps=None, offset=None, width=None):
        self.start_step = start_step
        self.steps = steps
        self.offset = offset
        self.width = width


class SliceSpec:
    def __init__(self, start_step=None, steps=None):
        self.start_step = start_step
        self.steps = steps

    def range(self):
        return slice(self.start_step, self.start_step + self.steps)


class Rule:
    def __init__(self, rule_number, base=2, length=None):

        self.input_range = 1  # TBD - generalize to allow for larger neighborhoods, using argument
        # !!! - CellularAutomata currently makes no use of input_range; range of 1 is hard coded there

        self.base = base
        self.rule_number = rule_number
        self.length = length

        self.input_span = 2*self.input_range + 1
        self.rules = Rule.n_rules(base, self.input_span)
        # Validate the rule number
        if rule_number < 0 or rule_number > self.rules - 1:
            raise CellularAutomataError(f"Invalid rule number. Must be between 0 and {self.rules - 1}.")

        # Convert rule number to base representation
        self.encoding = self._encode(self.rule_number, self.base, self.input_span, self.length)

    @staticmethod
    def n_rules(base, input_span):
        return base ** (base ** input_span)

    ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    @staticmethod
    def _encode(rule_number, base=2, input_span=3, length=None):
        """
        Converts a rule number to its representation in the given base.
        """
        if length is None:
            length = base ** input_span

        if base > len(Rule.ALPHABET):
            raise ValueError(f"Base too large. Can't handle base > {len(Rule.ALPHABET)}")

        digits = []
        while rule_number:
            digits.append(Rule.ALPHABET[rule_number % base])
            rule_number //= base

        # Pad with zeros (or '0' equivalents for the base) to the desired length
        while len(digits) < length:
            digits.append(Rule.ALPHABET[0])

        return ''.join(reversed(digits))

    @staticmethod
    def _decode(encoding, base=2):
        """
        Converts a rule encoded in the given base to its rule number.
        """
        if base > len(Rule.ALPHABET):
            raise ValueError(f"Base too large. Can't handle base > {len(Rule.ALPHABET)}")

        rule_number = 0
        for digit in encoding:
            rule_number = rule_number * base + Rule.ALPHABET.index(digit)
        return rule_number

    @dataclass
    class DisplayParams:
        fig_width: float = 12
        gap: float = 0.2
        vertical_shift: float = 0.5
        grid_color: str = 'black'
        grid_width: float = 0.5

    def _plot_display(self, ax, display_params: DisplayParams = DisplayParams()):
        # TBD - Repeated in code for CellularAutomata.get_display, make into utility function; use one system
        colors = {k: str(v) for k, v in zip(Rule.ALPHABET[:self.base], np.linspace(1, 0, self.base))}

        def draw_custom_cell(x, y, d, cell_size=1):
            cell_color = colors[d]
            rect = Rectangle((x, y), cell_size, cell_size,
                             edgecolor=display_params.grid_color, facecolor=cell_color,
                             linewidth=display_params.grid_width)
            ax.add_patch(rect)

        # Generate all configurations, of a given length, in order for a given base, using list comprehension
        configurations = [self._encode(i, self.base, length=self.input_span) for
                          i in range(self.base ** self.input_span)]
        configurations.reverse()

        # Create a new figure and axis
        # fig, ax = plt.subplots(figsize=(fig_width, fig_width*2.5/(2*len(configurations))))
        ax.set_xlim(-0.25, 4*len(configurations)-0.75)
        ax.set_ylim(0, 2.5)
        ax.set_aspect('equal')
        ax.axis('off')
        # REV - Cleaner way to get aspect ratio?
        height_ratio = ((ax.get_xlim()[1] - ax.get_xlim()[0]) / (ax.get_ylim()[1] - ax.get_ylim()[0]))

        # Adjust the vertical position using the vertical_shift
        y_top = 2 - display_params.gap - display_params.vertical_shift
        y_bottom = 1 - 2 * display_params.gap - display_params.vertical_shift

        # Iterate over each configuration and draw it followed by its output
        for idx, config in enumerate(configurations):
            output = self.encoding[idx]
            # Draw the 3-bit configuration
            for i, digit in enumerate(config):
                draw_custom_cell(i + idx * 4, y_top, digit)

            # Draw the output below the configuration, with a gap
            draw_custom_cell(idx * 4 + 1, y_bottom, output)

        # plt.tight_layout()
        return height_ratio

    def get_display(self, display_params: DisplayParams = DisplayParams()):
        fig, ax = plt.subplots(figsize=(display_params.fig_width,
                                        display_params.fig_width * 2.5 / (2 * (self.base ** self.input_span))))
        height_ratio = self._plot_display(ax, display_params)
        plt.tight_layout()
        return fig, ax, height_ratio

    def display(self, display_params: DisplayParams = DisplayParams()):
        _, _, _ = self.get_display(display_params)
        plt.show()


class CellularAutomata:
    def __init__(self, rule_number, initial_conditions, base=2, length=None,
                 frame_width=101, frame_steps=200,
                 boundary_condition="zero"):

        # Validate boundary condition
        valid_boundary_conditions = ["zero", "periodic", "one"]
        if boundary_condition not in valid_boundary_conditions:
            raise CellularAutomataError(
                f"Invalid boundary condition. Must be one of {', '.join(valid_boundary_conditions)}.")

        # Set properties
        self.rule_number = rule_number
        self.frame_width = frame_width
        self.frame_steps = frame_steps
        self.boundary_condition = boundary_condition

        self.rule = Rule(self.rule_number, base, length)

        # Initialize the lattice with zeros
        self._lattice = np.zeros((self.frame_steps, self.frame_width), dtype=int)

        # CHANGE: Process initial_conditions as a string and center on the 0th step
        # If the string length is even, pad it with a '0' at the left end
        if len(initial_conditions) % 2 == 0:
            initial_conditions = '0' + initial_conditions
        center = self.frame_width // 2
        start = center - len(initial_conditions) // 2

        # Check for overflow of initial conditions
        if start < 0 or start + len(initial_conditions) > self.frame_width:
            raise CellularAutomataError("Initial conditions overflow the frame boundaries when centered.")

        for idx, char in enumerate(initial_conditions):
            value = Rule.ALPHABET.index(char)
            if value >= base:
                raise CellularAutomataError(f"Initial condition contains invalid symbol '{char}'.")
            self._lattice[0, start + idx] = value

        # Compute the automaton
        self._compute_automaton()

    # Return the lattice, optionally with a slice specified using a SliceSpec object
    def lattice(self, slice_steps: SliceSpec = None):
        if slice_steps is None:
            slice_steps = SliceSpec(0, self.frame_steps)
        else:
            self._validate_slice_bounds(slice_steps, check_bounds=True)
        return self._lattice[slice_steps.range()]

    def _get_boundary_values(self, current_row):
        """
        Returns boundary values based on boundary condition and current row.
        """
        if self.boundary_condition == "zero":
            return 0, 0
        elif self.boundary_condition == "periodic":
            return current_row[-1], current_row[0]
        elif self.boundary_condition == "one":
            return 1, 1

    def _compute_automaton(self):
        """
        Generates the automaton based on the rule and initial conditions using a vectorized approach.
        """
        for row in range(1, self.frame_steps):
            # Get boundary values and extend current row
            left_boundary, right_boundary = self._get_boundary_values(self._lattice[row - 1])
            extended_current_row = np.hstack(([left_boundary], self._lattice[row - 1], [right_boundary]))

            # Use slicing to get left, center, and right neighbors for each cell
            left_neighbors = extended_current_row[:-2]
            center_neighbors = extended_current_row[1:-1]
            right_neighbors = extended_current_row[2:]

            #Form patterns considering the current base
            patterns = left_neighbors * self.rule.base ** 2 + center_neighbors * self.rule.base + right_neighbors

            # Use the patterns to index into the rule's encoding considering the current base
            self._lattice[row] = [int(self.rule.encoding[self.rule.base ** 3 - 1 - pattern]) for pattern in patterns]

    def _validate_highlight_bounds(self, highlight: HighlightBounds, check_bounds: bool):
        """
        Checks bounds for highlighting and returns error messages for any explicitly provided invalid bounds.
        Set any unspecified highlight bounds to default values.
        Adjust unchecked provided bounds implement the intended highlight (which may be clipped or outside the frame).
        """
        # Check if the highlight region specified by any provided highlight bounds exceeds the bounds of the lattice
        if check_bounds:
            error_messages = []
            if all([highlight.start_step, highlight.steps]):
                if highlight.start_step + highlight.steps > self.frame_steps:
                    error_messages.append(
                        f"highlight starts at step {highlight.start_step} "
                        f"and ends at step {highlight.start_step + highlight.steps} (> {self.frame_steps})")
            if all([highlight.start_step]):
                if highlight.start_step < 0:
                    error_messages.append(f"highlight starts before step 0")
            if all([highlight.offset, highlight.width]):
                if (self.frame_width + highlight.width) // 2 + highlight.offset > self.frame_width:
                    error_messages.append(
                        f"highlight exceeds right bound with "
                        f"{(self.frame_width + highlight.width) // 2 + highlight.offset} (> {self.frame_width})")
                if (self.frame_width - highlight.width) // 2 + highlight.offset < 0:
                    error_messages.append(
                        f"highlight exceeds left bound with "
                        f"{(self.frame_width - highlight.width) // 2 + highlight.offset} (< 0)")
            if error_messages:
                raise CellularAutomataError(*error_messages)

        # Set any unspecified highlight bounds to default values
        if highlight.start_step is None:
            highlight.start_step = 0
        if highlight.steps is None:
            highlight.steps = self.frame_steps - highlight.start_step
        if highlight.offset is None:
            highlight.offset = 0
        if highlight.width is None:
            highlight.width = self.frame_width

        # Adjust unchecked provided bounds
        if highlight.start_step < 0:
            highlight.steps = max(0, highlight.steps + highlight.start_step)
            highlight.start_step = 0

    def _validate_slice_bounds(self, slice_spec: SliceSpec, check_bounds: bool):
        """
        Checks bounds for slice and returns error messages for any explicitly provided invalid bounds.
        Implement default behavior for missing or unchecked invalid specs.
        """
        if slice_spec.start_step is None or slice_spec.start_step < 0:
            if check_bounds:
                raise CellularAutomataError(f"Invalid slice start step {slice_spec.start_step}. Must be >= 0.")
            else:
                slice_spec.start_step = 0
        elif slice_spec.steps is None or slice_spec.steps < 1:
            if check_bounds:
                raise CellularAutomataError(f"Invalid slice steps {slice_spec.steps}. Must be >= 1.")
            else:
                slice_spec.steps = 1
        elif slice_spec.steps > self.frame_steps - slice_spec.start_step:
            if check_bounds:
                raise CellularAutomataError(
                    f"Invalid slice steps {slice_spec.steps}. Must be <= {self.frame_steps - slice_spec.start_step}.")
            else:
                slice_spec.steps = self.frame_steps - slice_spec.start_step

    @dataclass
    class DisplayParams:
        fig_width: float = 12
        highlights: [HighlightBounds] = (HighlightBounds(),)
        slice_steps: SliceSpec = None
        highlight_mask: float = 0.3
        grid_color: str = None
        grid_width: float = 0.5
        cell_colors: [str] = None
        check_highlight_bounds: bool = True
        show_rule: bool = False

    def _plot_display(self, ax, display_params: DisplayParams = DisplayParams()):
        """
        Displays the cellular automaton lattice
        optionally highlighting a frame within it and
        optionally showing a grid around the cells.
        """

        # TBD - Repeated in code for Rule.get_display, make into utility function; use one system (dict or list)
        if display_params.cell_colors is None:
            display_params.cell_colors = [str(c) for c in np.linspace(1, 0, self.rule.base)]

        for highlight in display_params.highlights:
            self._validate_highlight_bounds(highlight, check_bounds=display_params.check_highlight_bounds)

        # Create a mask for highlighting, constraining the highlighted region to the bounds of the lattice
        mask = np.ones_like(self._lattice) * display_params.highlight_mask
        for highlight in display_params.highlights:
            mask[highlight.start_step:highlight.start_step + highlight.steps,
                 max(0, (self.frame_width - highlight.width) // 2 + highlight.offset):
                 min(self.frame_width, (self.frame_width + highlight.width) // 2 + highlight.offset)] = 1

        # Set the slice to the entire frame if not specified
        if display_params.slice_steps is None:
            display_params.slice_steps = SliceSpec(0, self.frame_steps)
        else:
            # Otherwise set unspecified or overflowing slice bounds to default values
            self._validate_slice_bounds(display_params.slice_steps, check_bounds=False)

        # Plotting
        ax.imshow(self._lattice[display_params.slice_steps.range()]/(self.rule.base-1),
                  alpha=mask[display_params.slice_steps.range()],
                  cmap=ListedColormap(display_params.cell_colors),
                  aspect='equal', interpolation='none')

        # Add grid with lines around each cell if grid_color is specified
        if display_params.grid_color:
            ax.grid(which='minor', color=display_params.grid_color, linewidth=display_params.grid_width)
            ax.set_xticks(np.arange(-.5, self.frame_width, 1), minor=True)
            # Note: not using frame_steps here
            ax.set_yticks(np.arange(-.5, display_params.slice_steps.steps, 1), minor=True)

            # Turn off major grid lines
            ax.grid(which='major', visible=False)

            ax.tick_params(which='both', bottom=False, left=False, labelbottom=False,
                           labelleft=False)  # Hide ticks and labels
        else:
            ax.axis('off')

        plt.setp(ax.spines.values(), color=display_params.grid_color, linewidth=display_params.grid_width)

    def get_display(self, display_params: DisplayParams = DisplayParams()):

        if not display_params.show_rule:
            fig, lattice_ax = plt.subplots(figsize=(display_params.fig_width,
                                                    display_params.fig_width * self.frame_steps / self.frame_width))
            self._plot_display(lattice_ax, display_params)
            plt.tight_layout()
            return fig, lattice_ax
        else:
            # Create a dummy figure to compute rule's aspect ratio
            # REV - This seems pretty stupid, there has to be a better way than calling self.rule._plot_display twice
            dummy_fig, dummy_ax, rule_height_ratio = self.rule.get_display()
            plt.close(dummy_fig)

            # Calculate heights
            h_rule = display_params.fig_width / rule_height_ratio
            h_lattice = display_params.fig_width * self.frame_steps / self.frame_width

            # Create main figure with adjusted height
            total_height = h_rule + h_lattice + 0.05 * display_params.fig_width  # Adding small gap
            fig = plt.figure(figsize=(display_params.fig_width, total_height))

            # GridSpec layout
            gs = gridspec.GridSpec(2, 1,
                                   height_ratios=[h_rule, h_lattice], hspace=0.0005*display_params.fig_width)

            # Rule plot
            rule_ax = plt.subplot(gs[0])
            self.rule._plot_display(rule_ax)

            # Lattice plot
            lattice_ax = plt.subplot(gs[1])
            self._plot_display(lattice_ax, display_params)

            return fig, (rule_ax, lattice_ax)

    def display(self, display_params: DisplayParams = DisplayParams()):
        _, _ = self.get_display(display_params)
        plt.show()
