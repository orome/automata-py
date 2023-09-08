"""
A simple cellular automata based on those discussed in Wolfram's A New Kind of Science.
Currently limited to simple elementary (1D, two-state, immediate neighbor) automata,
using 0 boundary conditions.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


class CellularAutomataError(ValueError):
    def __init__(self, *args):
        super().__init__(", ".join(args).capitalize() + ".")


class CellularAutomata:
    def __init__(self, rule_number, initial_conditions, frame_width=101, frame_steps=200):
        # Validate the rule number
        if rule_number < 0 or rule_number > 255:
            raise CellularAutomataError("Invalid rule number. Must be between 0 and 255.")

        # Set properties
        self.rule_number = rule_number
        self.initial_conditions = initial_conditions
        self.frame_width = frame_width
        self.frame_steps = frame_steps

        # Convert rule number to binary representation
        self.rule_binary = self._rule_number_to_binary(self.rule_number)

        # Initialize the lattice with zeros
        self._lattice = np.zeros((self.frame_steps, self.frame_width), dtype=int)

        # Set the initial conditions
        center = self.frame_width // 2
        for idx in initial_conditions:
            if center + idx < 0 or center + idx >= self.frame_width:
                raise CellularAutomataError("Initial condition at index", str(idx), "is outside of the frame.")
            self._lattice[0, center + idx] = 1

        # Compute the automaton
        self._compute_automaton()

    def _rule_number_to_binary(self, rule_number):
        """Converts a rule number to its binary representation."""
        return format(rule_number, '08b')

    def _compute_automaton(self):
        """Generates the automaton based on the rule and initial conditions."""
        for row in range(1, self.frame_steps):
            for col in range(1, self.frame_width - 1):
                pattern = self._lattice[row - 1, col - 1:col + 2]
                idx = 7 - int("".join(map(str, pattern)), 2)  # Convert binary pattern to index
                self._lattice[row, col] = int(self.rule_binary[idx])

    def _check_highlight_bounds(self, highlight_start_step, highlight_steps, highlight_width, highlight_offset):
        """Checks bounds for highlighting and returns error messages if they exist."""
        error_messages = []
        if highlight_start_step + highlight_steps > self.frame_steps:
            error_messages.append(
                f"starts at step {highlight_start_step} and ends at step {highlight_start_step + highlight_steps} (> {self.frame_steps})")
        if highlight_start_step < 0:
            error_messages.append(f"starts before step 0")
        if self.frame_width // 2 + highlight_offset + highlight_width // 2 > self.frame_width:
            error_messages.append(
                f"width exceeds right bound with {self.frame_width // 2 + highlight_offset + highlight_width // 2} (> {self.frame_width})")
        if self.frame_width // 2 + highlight_offset - highlight_width // 2 < 0:
            error_messages.append(
                f"width exceeds left bound with {self.frame_width // 2 + highlight_offset - highlight_width // 2} (< 0)")
        return error_messages

    def display(self, fig_width=12, highlight_width=50, highlight_steps=50,
                highlight_start_step=0, highlight_offset=0, highlight_mask=0.3, show_axes=False):
        """Displays the cellular automaton lattice with optional highlighting and axes."""

        # Check if the highlight region exceeds the bounds of the lattice
        error_messages = self._check_highlight_bounds(highlight_start_step, highlight_steps, highlight_width,
                                                      highlight_offset)
        if error_messages:
            raise CellularAutomataError(*error_messages)

        # Create a mask for highlighting
        mask = np.ones_like(self._lattice) * highlight_mask
        mask[highlight_start_step:highlight_start_step + highlight_steps,
        self.frame_width // 2 + highlight_offset - highlight_width // 2:
        self.frame_width // 2 + highlight_offset + highlight_width // 2] = 1

        # Plotting
        fig, ax = plt.subplots(figsize=(fig_width, fig_width * self.frame_steps / self.frame_width))
        ax.imshow(self._lattice * mask, cmap='binary', aspect='equal', interpolation='none')

        # Show axes if required
        if show_axes:
            ax.spines['top'].set_color('lightgray')
            ax.spines['bottom'].set_color('lightgray')
            ax.spines['left'].set_color('lightgray')
            ax.spines['right'].set_color('lightgray')
            ax.xaxis.set_ticks_position('both')
            ax.yaxis.set_ticks_position('both')
            ax.tick_params(axis='both', colors='lightgray', which='both')

            ax.set_xticks([i for i in range(0, self.frame_width, 10)])
            ax.set_yticks([i for i in range(0, self.frame_steps, 10)])

            # Adjusting label positions
            ax.xaxis.set_label_position("top")
            ax.yaxis.set_label_position("left")

            # Setting labels for x-axis as offsets from the center
            ax.set_xticklabels([i - self.frame_width // 2 for i in range(0, self.frame_width, 10)])

            # Setting labels for y-axis as steps
            ax.set_yticklabels([i for i in range(0, self.frame_steps, 10)])

            # Remove padding
            ax.set_xlim(left=0, right=self.frame_width)
            ax.set_ylim(bottom=self.frame_steps, top=0)

        else:
            ax.axis('off')

        plt.tight_layout()
        plt.show()


# # Testing with the previous version of the display method
# ca10 = CellularAutomata(30, [-1, 1], frame_steps=50)
# ca10.display(highlight_width=10, highlight_steps=20, highlight_start_step=0, highlight_offset=-5, highlight_mask=0.1)
#CellularAutomata(30, [-1, 1], frame_steps=50).display(highlight_width=10, highlight_steps=20, highlight_start_step=0, highlight_offset=-5, highlight_mask=0.1)


# def x_display(self, fig_width=12, highlight_width=50, highlight_steps=50,
    #             highlight_start_step=0, highlight_offset=0, highlight_mask=0.3):
    #     """Displays the cellular automaton lattice with optional highlighting."""
    #
    #     # Check if the highlight region exceeds the bounds of the lattice
    #     if (highlight_start_step + highlight_steps > self.frame_steps or
    #             highlight_start_step < 0 or
    #             self.frame_width // 2 + highlight_offset + highlight_width // 2 > self.frame_width or
    #             self.frame_width // 2 + highlight_offset - highlight_width // 2 < 0):
    #         raise ValueError("Requested highlight region exceeds the bounds of the lattice.")
    #
    #     # Create a mask for highlighting
    #     mask = np.ones_like(self._lattice) * highlight_mask
    #     mask[highlight_start_step:highlight_start_step + highlight_steps,
    #     self.frame_width // 2 + highlight_offset - highlight_width // 2:
    #     self.frame_width // 2 + highlight_offset + highlight_width // 2] = 1
    #
    #     # Plotting
    #     fig, ax = plt.subplots(figsize=(fig_width, fig_width * self.frame_steps / self.frame_width))
    #     ax.imshow(self._lattice * mask, cmap='binary', aspect='equal', interpolation='none')
    #     ax.axis('off')
    #     plt.show()
