"""
A simple cellular automata based on those discussed in Wolfram's A New Kind of Science.
Currently limited to 1D, multi-state, immediate neighbor automata, using various boundary conditions.
"""

from dataclasses import dataclass

import matplotlib.axes
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.gridspec as gridspec


class CellularAutomataError(ValueError):
    def __init__(self, *args: str):
        # super().__init__(", ".join(args).capitalize() + ".")
        super().__init__(", ".join(args) + ".")


@dataclass
class HighlightBounds:
    start_step: int = None
    steps: int = None
    offset: int = None
    width: int = None


@dataclass(frozen=True)
class SliceSpec:
    start_step: int = None
    steps: int = None

    def range(self):
        return slice(self.start_step, self.start_step + self.steps)


class Rule:
    def __init__(self, rule_number: int, base: int = 2):

        self.input_range = 1  # TBD - generalize to allow for larger neighborhoods, using argument
        # !!! - CellularAutomata currently makes no use of input_range; input_range of 1 is hard coded there

        self.base = base
        self.rule_number = rule_number

        self.input_span = 2 * self.input_range + 1        # Number of cells in the input neighborhood
        self.n_input_patterns = base ** self.input_span   # Number of input states for a rule
        self.n_rules = base ** self.n_input_patterns      # Number of possible rules for the given span and base

        # Validate the rule number
        if rule_number < 0 or rule_number > self.n_rules - 1:
            raise CellularAutomataError(f"Invalid rule number. Must be between 0 and {self.n_rules - 1}.")

        # Convert rule number to base representation; also the rule output pattern, in R-L order
        self.encoding = self._encode(self.rule_number, self.base, self.n_input_patterns)

        # Generate all configurations, of a given length
        input_patterns = [self._encode(i, self.base, length=self.input_span) for i in range(len(self.encoding))]
        input_patterns.reverse()  # Ordered to match rule number, which corresponds to output order by definition
        self.pattern_to_output = dict(zip(input_patterns, self.encoding))

        assert len(self.pattern_to_output) == self.n_input_patterns

    ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    @staticmethod
    def get_cell_colors(color_list: [str], base: int) -> {str: str}:
        cell_colors = {e: c for e, c in
                       zip(Rule.ALPHABET[:base],
                           color_list if color_list else Rule.DisplayParams.get_default_cell_colors(base))}
        return cell_colors  # , cell_colors.values()

    @staticmethod
    def _encode(value: int, base: int, length: int) -> str:
        """
        Converts a value to its representation in the given base, padded to length.
        """
        if base > len(Rule.ALPHABET):
            raise ValueError(f"Base too large. Can't handle base > {len(Rule.ALPHABET)}")

        digits = [Rule.ALPHABET[value // base ** i % base] for i in range(length)][::-1]

        return '{:>{fill}{length}}'.format(''.join(digits), fill=Rule.ALPHABET[0], length=length)

    @staticmethod
    def _decode(encoding: str, base: int) -> int:
        """
        Converts a value in a given base to a base 10 value.
        """
        if base > len(Rule.ALPHABET):
            raise ValueError(f"Base too large. Can't handle base > {len(Rule.ALPHABET)}")

        return sum([Rule.ALPHABET.index(digit) * (base ** i) for i, digit in enumerate(reversed(encoding))])

    @dataclass(frozen=True)
    class DisplayParams:
        fig_width: float = 12
        gap: float = 0.2
        vertical_shift: float = 0.5
        cell_colors: [str] = None
        grid_color: str = 'black'
        grid_thickness: float = 0.5
        rows: int = 1

        @staticmethod
        def get_default_cell_colors(base):
            return [str(c) for c in np.linspace(1, 0, base)]

    def best_rows(self, max_per_row: int = 14) -> int:
        total = self.n_input_patterns
        return next(filter(lambda d: total % d == 0 and total // d <= max_per_row, range(1, total + 1)), total)

    def _plot_display(self, ax: matplotlib.axes.Axes, display_params: DisplayParams) -> None:

        cell_color_mapping = Rule.get_cell_colors(display_params.cell_colors, self.base)

        def draw_cell(x, y, d, cell_size=1):
            rect = Rectangle((x, y), cell_size, cell_size,
                             edgecolor=display_params.grid_color, facecolor=cell_color_mapping[d],
                             linewidth=display_params.grid_thickness)
            ax.add_patch(rect)

        # noinspection PyProtectedMember
        plot_params = _PlotParams(self.n_input_patterns, display_params.rows)
        ax.set_xlim(plot_params.x_min, plot_params.x_max)
        ax.set_ylim(plot_params.y_min, plot_params.y_max)
        ax.set_aspect('equal')
        ax.axis('off')

        for pattern_idx, input_pattern in enumerate(self.pattern_to_output.keys()):
            row_idx = pattern_idx // plot_params.patterns_per_row

            # Adjust y position based on row index
            y_top_adj = 2.5 * (display_params.rows - row_idx - 1) + 1.5
            y_bottom_adj = 2.5 * (display_params.rows - row_idx - 1) + 0.5

            # Adjust x position based on the center_offset
            x_shift = (pattern_idx % plot_params.patterns_per_row) * 4

            # Draw the input digits
            for input_digit_pos, input_digit in enumerate(input_pattern):
                draw_cell(input_digit_pos + x_shift, y_top_adj, input_digit)
            # Draw the output digit below the input, with a gap
            draw_cell(x_shift + 1, y_bottom_adj, self.pattern_to_output[input_pattern])

    def get_display(self, display_params: DisplayParams = None) -> (plt.Figure, (plt.Axes | None, plt.Axes | None)):
        return _get_display_grid(None, self,
                                 None, display_params,
                                 False, True)

    def display(self, display_params: DisplayParams = None) -> None:
        _, _ = self.get_display(display_params)
        plt.show()


class CellularAutomata:

    _instances = {}

    # Overriding the __new__ method for memoization
    def __new__(cls, *args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[key] = instance
        return cls._instances[key]

    def __init__(self, rule_number: int, initial_conditions: str, base=2,
                 frame_width=101, frame_steps=200,
                 boundary_condition="zero"):

        # Avoid re-initializing an instance retrieved from memoization
        if getattr(self, '_initialized', False):
            return

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

        self.rule = Rule(self.rule_number, base)

        self._lattice = np.empty((self.frame_steps, self.frame_width), dtype='<U1')
        self._lattice.fill(Rule.ALPHABET[0])

        # Process initial_conditions as a string and center on the 0th step
        # If the string length is even, pad it with a '0' at the left end
        if len(initial_conditions) % 2 == 0:
            initial_conditions = Rule.ALPHABET[0] + initial_conditions
        center = self.frame_width // 2
        start = center - len(initial_conditions) // 2

        # Check for overflow of initial conditions
        if start < 0 or start + len(initial_conditions) > self.frame_width:
            raise CellularAutomataError("Initial conditions overflow the frame boundaries when centered.")

        for idx, char in enumerate(initial_conditions):
            if char not in Rule.ALPHABET[:base]:
                raise CellularAutomataError(f"Initial condition contains invalid symbol '{char}'.")
            self._lattice[0, start + idx] = char

        self._compute_automaton()

        self._initialized = True

    # Return the lattice, optionally with a slice specified using a SliceSpec object
    def lattice(self, slice_spec: SliceSpec = None) -> np.ndarray:
        slice_spec = self._validate_slice_bounds(slice_spec, check_bounds=True)
        return self._lattice[slice_spec.range()]

    def _get_boundary_values(self, current_row) -> (str, str):
        """
        Returns boundary values based on boundary condition and current row.
        """
        if self.boundary_condition == "zero":
            return Rule.ALPHABET[0], Rule.ALPHABET[0]
        elif self.boundary_condition == "periodic":
            return current_row[-1], current_row[0]
        elif self.boundary_condition == "one":
            return Rule.ALPHABET[1], Rule.ALPHABET[1]

    def _compute_automaton(self) -> None:
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

            # Form patterns considering the current base
            patterns = [left + center + right for left, center, right in
                        zip(left_neighbors, center_neighbors, right_neighbors)]

            # Use the patterns to directly get the output values from the rule's pattern_to_output dictionary
            self._lattice[row] = [self.rule.pattern_to_output[pattern] for pattern in patterns]

    def _validate_highlight_bounds(self, highlight: HighlightBounds, check_bounds: bool) -> None:
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

    def _validate_slice_bounds(self, slice_spec: SliceSpec, check_bounds: bool) -> SliceSpec:
        """
        Check bounds for slice and error messages for any invalid bounds.
        Return a SliceSpec that is valid for the lattice.
        """
        if slice_spec is None:
            return SliceSpec(0, self.frame_steps)

        if check_bounds:
            if slice_spec.start_step is not None:
                if slice_spec.start_step < 0:   # slice_spec.start_step is None or
                    raise CellularAutomataError(f"Invalid slice start step {slice_spec.start_step}. Must be >= 0.")
                elif slice_spec.start_step >= self.frame_steps:
                    raise CellularAutomataError(
                        f"Invalid slice start step {slice_spec.start_step}. Must be < {self.frame_steps}.")
            if slice_spec.steps is not None:
                if slice_spec.steps < 1:  # slice_spec.steps is None or
                    raise CellularAutomataError(f"Invalid slice steps {slice_spec.steps}. Must be >= 1.")
                else:
                    fixed_start_step = slice_spec.start_step if slice_spec.start_step is not None else 0
                    if slice_spec.steps > self.frame_steps - fixed_start_step:
                        raise CellularAutomataError(
                            f"Invalid slice steps {slice_spec.steps}. "
                            f"Must be <= {self.frame_steps - fixed_start_step}.")

        validated_start_step = slice_spec.start_step
        validated_steps = slice_spec.steps

        if validated_start_step is None or validated_start_step < 0:
            validated_start_step = 0
        elif slice_spec.start_step >= self.frame_steps:
            validated_start_step = self.frame_steps - 1
        if validated_steps is None or validated_steps < 1:
            validated_steps = 1
        elif validated_steps > self.frame_steps - validated_start_step:
            validated_steps = self.frame_steps - validated_start_step

        return SliceSpec(validated_start_step, validated_steps)

    # TBD - This should be frozen and validating the bounds of the slice should be handled differently
    @dataclass
    class DisplayParams:
        fig_width: float = 12
        highlights: [HighlightBounds] = (HighlightBounds(),)
        slice_spec: SliceSpec = None
        highlight_mask: float = 0.3
        grid_color: str = None
        grid_thickness: float = 0.5
        cell_colors: [str] = None
        check_highlight_bounds: bool = True

    def _plot_display(self, ax: matplotlib.axes.Axes, display_params: DisplayParams) -> None:
        """
        Displays the cellular automaton lattice
        optionally highlighting a frame within it and
        optionally showing a grid around the cells.
        """

        cell_color_mapping = Rule.get_cell_colors(display_params.cell_colors, self.rule.base)

        # REV - Assumes _validate_highlight_bounds and _validate_slice_bounds by caller
        # for highlight in display_params.highlights:
        #     self._validate_highlight_bounds(highlight, check_bounds=display_params.check_highlight_bounds)
        # display_params.slice_spec = self._validate_slice_bounds(display_params.slice_spec, check_bounds=False)

        # Create a mask for highlighting, constraining the highlighted region to the bounds of the lattice
        mask = np.ones(self._lattice.shape, dtype=float) * display_params.highlight_mask
        for highlight in display_params.highlights:
            mask[highlight.start_step:highlight.start_step + highlight.steps,
                 max(0, (self.frame_width - highlight.width) // 2 + highlight.offset):
                 min(self.frame_width, (self.frame_width + highlight.width) // 2 + highlight.offset)] = 1

        # REV - See if there's a better way to do this
        # Convert the encoded lattice data to color using the color's dictionary.
        color_strings = np.vectorize(cell_color_mapping.get)(self._lattice[display_params.slice_spec.range()])
        # Convert the entire color_strings array to an array of RGBA values
        rgba_values = mpl.colors.to_rgba_array(color_strings.ravel())
        # Reshape the rgba_values to match the shape of the color_strings array with an additional dimension for RGBA
        rgb_lattice = rgba_values.reshape(*color_strings.shape, 4)
        # Mask the highlighted region
        rgb_lattice[..., 3] *= mask[display_params.slice_spec.range()]

        ax.imshow(rgb_lattice, aspect='equal', interpolation='none')

        # Add grid with lines around each cell if grid_color is specified
        if display_params.grid_color and display_params.grid_thickness > 0:
            ax.grid(which='minor', color=display_params.grid_color, linewidth=display_params.grid_thickness)
            ax.set_xticks(np.arange(-.5, self.frame_width, 1), minor=True)
            # Note: not using frame_steps here; only showing the slice
            ax.set_yticks(np.arange(-.5, display_params.slice_spec.steps, 1), minor=True)
            ax.grid(which='major', visible=False)
            ax.tick_params(which='both', bottom=False, left=False, labelbottom=False, labelleft=False)
        else:
            ax.axis('off')

        plt.setp(ax.spines.values(), color=display_params.grid_color, linewidth=display_params.grid_thickness)

    def get_display(self, display_params: DisplayParams = None,
                    rule_display_params: Rule.DisplayParams = None,
                    show_rule: bool = False) -> (plt.Figure, (plt.Axes | None, plt.Axes | None)):
        return _get_display_grid(self, self.rule,
                                 display_params, rule_display_params,
                                 True, show_rule)

    def display(self, display_params: DisplayParams = None,
                rule_display_params: Rule.DisplayParams = None,
                show_rule: bool = False) -> None:
        _, _ = self.get_display(display_params, rule_display_params, show_rule)
        plt.show()


@dataclass(frozen=True)
class _PlotParams:
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    patterns_per_row: int
    height_ratio: float

    def __init__(self, total_patterns: int, rows: int, left_buffer: float = 0.25, right_buffer: float = 0.75):
        patterns_per_row = -(-total_patterns // rows)
        height_ratio = (4 * patterns_per_row - right_buffer + left_buffer) / (2.5 * rows)
        x_min = -left_buffer
        x_max = 4 * patterns_per_row - right_buffer
        y_min = 0
        y_max = 2.5 * rows

        object.__setattr__(self, 'patterns_per_row', patterns_per_row)
        object.__setattr__(self, 'height_ratio', height_ratio)
        object.__setattr__(self, 'x_min', x_min)
        object.__setattr__(self, 'x_max', x_max)
        object.__setattr__(self, 'y_min', y_min)
        object.__setattr__(self, 'y_max', y_max)


def _get_display_grid(automaton: CellularAutomata | None, rule: Rule | None,
                      display_params: CellularAutomata.DisplayParams | None,
                      rule_display_params: Rule.DisplayParams | None,
                      show_automaton: bool, show_rule: bool) -> (plt.Figure, (plt.Axes | None, plt.Axes | None)):

    assert not show_automaton or (show_automaton and automaton is not None)
    assert not show_rule or (show_rule and rule is not None)

    if display_params is None:
        display_params = CellularAutomata.DisplayParams()

    if rule_display_params is not None:
        show_rule = True

    if show_automaton:
        for highlight in display_params.highlights:
            # noinspection PyProtectedMember
            automaton._validate_highlight_bounds(highlight, check_bounds=display_params.check_highlight_bounds)
        # noinspection PyProtectedMember
        display_params.slice_spec = automaton._validate_slice_bounds(display_params.slice_spec, check_bounds=False)

    fig_width = display_params.fig_width if show_automaton else rule_display_params.fig_width

    if show_rule:
        if rule_display_params is None:
            rule_display_params = Rule.DisplayParams(cell_colors=display_params.cell_colors)
        # noinspection PyProtectedMember
        h_rule = (fig_width / _PlotParams(rule.n_input_patterns, rule_display_params.rows).height_ratio)
    else:
        h_rule = 0

    if show_automaton:
        h_lattice = fig_width * display_params.slice_spec.steps / automaton.frame_width
    else:
        h_lattice = 0

    fig = plt.figure(figsize=(fig_width, h_rule + h_lattice))
    gs = gridspec.GridSpec(2, 1,
                           height_ratios=[h_rule, h_lattice], hspace=0.0005 * fig_width)

    if show_rule:
        rule_ax = fig.add_subplot(gs[0])
        # noinspection PyProtectedMember
        rule._plot_display(rule_ax, rule_display_params)
    else:
        rule_ax = None

    if show_automaton:
        lattice_ax = fig.add_subplot(gs[1])
        # noinspection PyProtectedMember
        automaton._plot_display(lattice_ax, display_params)
    else:
        lattice_ax = None

    return fig, (rule_ax, lattice_ax)
