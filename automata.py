"""
A simple cellular automata based on those discussed in Wolfram's A New Kind of Science.
Currently limited to simple elementary (1D, two-state, immediate neighbor) automata,
using various boundary conditions.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


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


class CellularAutomata:
    def __init__(self, rule_number, initial_conditions,
                 frame_width=101, frame_steps=200,
                 boundary_condition="zero"):
        # Validate the rule number
        if rule_number < 0 or rule_number > 255:
            raise CellularAutomataError("Invalid rule number. Must be between 0 and 255.")

        # Validate boundary condition
        valid_boundary_conditions = ["zero", "periodic", "one"]
        if boundary_condition not in valid_boundary_conditions:
            raise CellularAutomataError(
                f"Invalid boundary condition. Must be one of {', '.join(valid_boundary_conditions)}.")

        # Set properties
        self.rule_number = rule_number
        self.initial_conditions = initial_conditions
        self.frame_width = frame_width
        self.frame_steps = frame_steps
        self.boundary_condition = boundary_condition

        # Convert rule number to binary representation
        self.rule_binary = self._rule_number_to_binary(self.rule_number)

        # Initialize the lattice with zeros
        self._lattice = np.zeros((self.frame_steps, self.frame_width), dtype=int)

        # Set the initial conditions
        center = self.frame_width // 2
        for idx in initial_conditions:
            # Check that all nonzero initial conditions are within the frame
            if center + idx < 0 or center + idx >= self.frame_width:
                raise CellularAutomataError("Initial condition at index", str(idx), "is outside of the frame.")
            self._lattice[0, center + idx] = 1

        # Compute the automaton
        self._compute_automaton()

    # Return the lattice, optionally with a slice specified using a SliceSpec object
    def lattice(self, slice_steps: SliceSpec = None):
        if slice_steps is None:
            slice_steps = SliceSpec(0, self.frame_steps)
        else:
            self._validate_slice_bounds(slice_steps, check_bounds=True)
        return self._lattice[slice_steps.range()]

    @staticmethod
    def _rule_number_to_binary(rule_number):
        """
        Converts a rule number to its binary representation.
        """
        return format(rule_number, '08b')

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

            # Form the 3-bit binary numbers for each cell in parallel
            patterns = left_neighbors * 4 + center_neighbors * 2 + right_neighbors

            # Use the patterns to index into the rule's binary representation and update the entire next row
            self._lattice[row] = [int(self.rule_binary[7 - pattern]) for pattern in patterns]

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

    def get_display(self, fig_width=12,
                    highlights: [HighlightBounds] = [HighlightBounds()],
                    slice_steps: SliceSpec = None,
                    highlight_mask=0.3, grid_color=None, grid_width=0.5,
                    cell_colors=('white', 'black'),
                    check_highlight_bounds=True):
        """
        Displays the cellular automaton lattice
        optionally highlighting a frame within it and
        optionally showing a grid around the cells.
        """
        for highlight in highlights:
            self._validate_highlight_bounds(highlight, check_bounds=check_highlight_bounds)

        # Create a mask for highlighting, constraining the highlighted region to the bounds of the lattice
        mask = np.ones_like(self._lattice) * highlight_mask
        for highlight in highlights:
            mask[highlight.start_step:highlight.start_step + highlight.steps,
                 max(0, (self.frame_width - highlight.width) // 2 + highlight.offset):
                 min(self.frame_width, (self.frame_width + highlight.width) // 2 + highlight.offset)] = 1

        # Set the slice to the entire frame if not specified
        if slice_steps is None:
            slice_steps = SliceSpec(0, self.frame_steps)
        else:
            # Otherwise set unspecified or overflowing slice bounds to default values
            self._validate_slice_bounds(slice_steps, check_bounds=False)

        # Plotting
        fig, ax = plt.subplots(figsize=(fig_width, fig_width * self.frame_steps / self.frame_width))
        ax.imshow(self._lattice[slice_steps.range()], alpha=mask[slice_steps.range()],
                  cmap=ListedColormap(cell_colors),
                  aspect='equal', interpolation='none')

        # Add grid with lines around each cell if grid_color is specified
        if grid_color:
            ax.grid(which='minor', color=grid_color, linewidth=grid_width)  # Use the specified grid width
            ax.set_xticks(np.arange(-.5, self.frame_width, 1), minor=True)
            ax.set_yticks(np.arange(-.5, slice_steps.steps, 1), minor=True)  # Note: not using frame_steps here

            # Turn off major grid lines
            ax.grid(which='major', visible=False)

            ax.tick_params(which='both', bottom=False, left=False, labelbottom=False,
                           labelleft=False)  # Hide ticks and labels
        else:
            ax.axis('off')

        plt.setp(ax.spines.values(), color=grid_color, linewidth=grid_width)

        plt.tight_layout()
        return fig, ax

    def display(self, *args, **kwargs):
        _, _ = self.get_display(*args, **kwargs)
        plt.show()
