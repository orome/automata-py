"""
A simple cellular automata based on those discussed in Wolfram's A New Kind of Science.
Currently limited to simple elementary (1D, two-state, immediate neighbor) automata,
using various boundary conditions.
"""


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap



class CellularAutomataError(ValueError):
    def __init__(self, *args):
        super().__init__(", ".join(args).capitalize() + ".")



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

    def _rule_number_to_binary(self, rule_number):
        """
        Converts a rule number to its binary representation.
        """
        return format(rule_number, '08b')

    def _get_boundary_values(self, current_row):
        """
        Returns boundary values based on boundary condition and current row.
        """
        if self.boundary_condition == "zero":
            return (0, 0)
        elif self.boundary_condition == "periodic":
            return (current_row[-1], current_row[0])
        elif self.boundary_condition == "one":
            return (1, 1)

    def _compute_automaton(self):
        """
        Generates the automaton based on the rule and initial conditions.
        """
        for row in range(1, self.frame_steps):
            left_boundary, right_boundary = self._get_boundary_values(self._lattice[row - 1])
            extended_current_row = np.hstack(([left_boundary], self._lattice[row - 1], [right_boundary]))
            for col in range(1, self.frame_width + 1):  # Adjusted to account for extended row
                pattern = extended_current_row[col - 1:col + 2]
                idx = 7 - int("".join(map(str, pattern)), 2)  # Convert binary pattern to index
                self._lattice[row, col - 1] = int(self.rule_binary[idx])  # Adjusted to account for extended row

    def _check_highlight_bounds(self, highlight_start_step, highlight_steps, highlight_width, highlight_offset):
        """
        Checks bounds for highlighting and returns error messages any explicitly provided.
        """
        error_messages = []
        if all([highlight_start_step, highlight_steps]):
            if highlight_start_step + highlight_steps > self.frame_steps:
                error_messages.append(
                    f"starts at step {highlight_start_step} and ends at step {highlight_start_step + highlight_steps} (> {self.frame_steps})")
        if all([highlight_start_step]):
            if highlight_start_step < 0:
                error_messages.append(f"starts before step 0")
        if all([highlight_offset, highlight_width]):
            if self.frame_width // 2 + highlight_offset + highlight_width // 2 > self.frame_width:
                error_messages.append(
                    f"width exceeds right bound with {self.frame_width // 2 + highlight_offset + highlight_width // 2} (> {self.frame_width})")
            if self.frame_width // 2 + highlight_offset - highlight_width // 2 < 0:
                error_messages.append(
                    f"width exceeds left bound with {self.frame_width // 2 + highlight_offset - highlight_width // 2} (< 0)")
        return error_messages

    def get_display(self, fig_width=12,
                    highlight_start_step=None, highlight_steps=None, highlight_offset=None, highlight_width=None,
                    highlight_mask=0.3, grid_color=None, grid_width=0.5,
                    check_highlight_bounds=True):
        """
        Displays the cellular automaton lattice
        optionally highlighting a frame within it and
        optionally showing a grid around the cells.
        """

        # Check if the highlight region specified by any provided highlight bounds exceeds the bounds of the lattice
        if check_highlight_bounds:
            error_messages = self._check_highlight_bounds(highlight_start_step, highlight_steps,
                                                          highlight_width, highlight_offset)
            if error_messages:
                raise CellularAutomataError(*error_messages)
        print(highlight_start_step, highlight_steps, highlight_offset, highlight_width)

        # Set any unspecified highlight bounds to default values
        if highlight_start_step is None:
            highlight_start_step = 0
        if highlight_steps is None:
            highlight_steps = self.frame_steps - highlight_start_step
        if highlight_offset is None:
            highlight_offset = 0
        if highlight_width is None:
            highlight_width = self.frame_width

        print(highlight_start_step, highlight_steps, highlight_offset, highlight_width)

        # Create a mask for highlighting, constraining the highlighted region to the bounds of the lattice
        # !!! - Something wrong where with how frame with is fixed <<<
        mask = np.ones_like(self._lattice) * highlight_mask
        mask[highlight_start_step:highlight_start_step + highlight_steps,
        self.frame_width // 2 + min(0, highlight_offset - highlight_width // 2):
        self.frame_width // 2 + max(0, highlight_offset + highlight_width // 2)] = 1

        # Plotting
        fig, ax = plt.subplots(figsize=(fig_width, fig_width * self.frame_steps / self.frame_width))
        ax.imshow(self._lattice * mask, cmap='binary', aspect='equal', interpolation='none')

        # Add grid with lines around each cell if grid_color is specified
        if grid_color:
            ax.grid(which='minor', color=grid_color, linewidth=grid_width)  # Use the specified grid width
            ax.set_xticks(np.arange(-.5, self.frame_width, 1), minor=True)
            ax.set_yticks(np.arange(-.5, self.frame_steps, 1), minor=True)

            # Turn off major grid lines
            ax.grid(which='major', visible=False)

            ax.tick_params(which='both', bottom=False, left=False, labelbottom=False,
                           labelleft=False)  # Hide ticks and labels
        else:
            ax.axis('off')

        for spine in ax.spines.values():
            plt.setp(ax.spines.values(), color=grid_color, linewidth=grid_width)

        plt.tight_layout()
        return fig, ax

    def display(self, *args, **kwargs):
        fig, ax = self.get_display(*args, **kwargs)
        plt.show()
