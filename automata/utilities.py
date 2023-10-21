# noinspection PyPackageRequirements
from IPython.display import display
# noinspection PyPackageRequirements
from ipywidgets import (IntSlider, Checkbox, ColorPicker, FloatSlider, Combobox, IntRangeSlider,
                        Layout, VBox, HBox, interactive)

from .core import Rule, SliceSpec, HighlightBounds, CellularAutomata

# USE - For use in Jupyter notebooks; assumes ipywidgets (and IPython) is installed in the Python environment


# TBD - Should be better coordinated with number of colors and color all_controls
_DISPLAY_BASE_MAX = 4

_MIN_SLICE_STEPS = 1


def get_controls(display_parameters=None, frame_steps=25, frame_width=201) -> dict:
    rule_slider = IntSlider(min=0, max=Rule(0, base=2).n_rules - 1, step=1, value=90, description='Rule:')
    base_slider = IntSlider(min=2, max=_DISPLAY_BASE_MAX, step=1, value=2, description='Base:')

    # Adjust the max r to correspond to the base
    def update_r_max(*_) -> None:
        rule_slider.max = Rule(0, base=int(base_slider.value)).n_rules - 1
    base_slider.observe(update_r_max, names='value')
    update_r_max()

    initial_conditions_entry = Combobox(
        value='1',
        options=[],
        description='Start:',
        ensure_option=False,  # allowing freeform input
        disabled=False
    )

    def validate_initial_conditions_entry(change):
        valid_chars = Rule.ALPHABET[:base_slider.value]
        new_value = ''.join([ch for ch in change['new'] if ch in valid_chars])

        # If the new value is different (i.e., some characters were filtered out),
        # set the Combobox value to '1'. Otherwise, add to options if not already present.
        if new_value != change['new']:
            initial_conditions_entry.value = new_value
        else:
            if new_value and new_value not in initial_conditions_entry.options:
                initial_conditions_entry.options = list(initial_conditions_entry.options) + [new_value]
    initial_conditions_entry.observe(validate_initial_conditions_entry, names='value')
    # validate_initial_conditions(chang=None)

    def validate_initial_conditions_for_base(*_):
        valid_chars = Rule.ALPHABET[:base_slider.value]
        if not all(ch in valid_chars for ch in initial_conditions_entry.value):
            initial_conditions_entry.value = '1'

    # Observe changes to the base_slider's value
    base_slider.observe(validate_initial_conditions_for_base, names='value')

    slice_slider = IntRangeSlider(
        value=[0, frame_steps],
        min=0,
        max=frame_steps,  # TBD - Change when frame_steps set by a control
        step=1,
        description='Slice:',
        disabled=False,
        continuous_update=True,
        orientation='horizontal',
        readout=True,
        readout_format='d',
    )

    def enforce_gap(change):
        old_lower, old_upper = change['old']
        lower, upper = change['new']

        if upper - lower < _MIN_SLICE_STEPS:
            # If the upper value has been moved most recently
            if upper != old_upper:
                new_lower = upper - _MIN_SLICE_STEPS
                # Ensure the new lower value isn't out of bounds
                if new_lower < slice_slider.min:
                    slice_slider.value = (slice_slider.min, slice_slider.min + _MIN_SLICE_STEPS)
                else:
                    slice_slider.value = (new_lower, upper)
            # If the lower value has been moved most recently
            elif lower != old_lower:
                new_upper = lower + _MIN_SLICE_STEPS
                # Ensure the new upper value isn't out of bounds
                if new_upper > slice_slider.max:
                    slice_slider.value = (slice_slider.max - _MIN_SLICE_STEPS, slice_slider.max)
                else:
                    slice_slider.value = (lower, new_upper)
    slice_slider.observe(enforce_gap, names=['value'])

    use_highlight_checkbox = Checkbox(value=False, description='Highlight')
    h_start_slider = IntSlider(min=0, max=frame_steps, step=1, value=0, description='Start:')
    h_width_slider = IntSlider(min=1, max=frame_width, step=1, value=21, description='Width:')
    h_offset_slider = IntSlider(min=-frame_width // 2, max=frame_width // 2, step=1, value=0,
                                description='Offset:')
    h_steps_slider = IntSlider(min=1, max=frame_steps, step=1, value=20, description='Steps:')

    rule_rows_slider = IntSlider(min=0, max=6, step=1, value=Rule(0, base=2).best_rows(),
                                 description='Rule rows:')

    def update_rule_rows_default(*_) -> None:
        rule_rows_slider.value = Rule(0, base=int(base_slider.value)).best_rows()

    base_slider.observe(update_rule_rows_default, names='value')
    update_rule_rows_default()

    # Enable/disable h_start and h_width based on the checkbox
    def update_highlight_controls(change=None) -> None:
        new_value = use_highlight_checkbox.value if change is None else change.new
        h_start_slider.disabled = not new_value
        h_width_slider.disabled = not new_value
        h_offset_slider.disabled = not new_value
        h_steps_slider.disabled = not new_value
    use_highlight_checkbox.observe(update_highlight_controls, names='value')
    update_highlight_controls()

    grid_color_picker = ColorPicker(concise=True, value='white', disabled=False, description='Grid color:')
    grid_thickness_slider = FloatSlider(min=0, max=2, step=0.025, value=0.2, description='Grid width:')

    cell_color_pickers = {0: ColorPicker(concise=True, value='black', disabled=False, description='0 ='),
                          1: ColorPicker(concise=True, value='yellow', disabled=False, description='1 ='),
                          2: ColorPicker(concise=True, value='red', disabled=False, description='2 ='),
                          3: ColorPicker(concise=True, value='green', disabled=False, description='3 =')}

    # Enable/disable cell color pickers based on current value of base
    def update_grid_color_controls(*_) -> None:
        for digit in cell_color_pickers.keys():
            if digit > int(base_slider.value) - 1:
                cell_color_pickers[digit].layout.display = 'none'
            else:
                cell_color_pickers[digit].layout.display = 'flex'  # REV - or 'block' or 'inline'

    base_slider.observe(update_grid_color_controls, names='value')
    update_grid_color_controls()

    controls = {
        'rule': rule_slider,
        'base': base_slider,
        'initial_conditions': initial_conditions_entry,
        'slice_bounds': slice_slider,
        'use_highlight': use_highlight_checkbox,
        'h_start': h_start_slider,
        'h_width': h_width_slider,
        'h_offset': h_offset_slider,
        'h_steps': h_steps_slider,
        'grid_color': grid_color_picker,
        'grid_thickness': grid_thickness_slider,
        'cell_color_0': cell_color_pickers[0],
        'cell_color_1': cell_color_pickers[1],
        'cell_color_2': cell_color_pickers[2],
        'cell_color_3': cell_color_pickers[3],  # REV - Can't be greater than _DISPLAY_BASE_MAX-1
        'rule_rows': rule_rows_slider
    }

    if display_parameters is None:
        display_parameters = controls.keys()

    # Filter all_controls based on the provided list of control names
    selected_controls = {parameter: controls[parameter] for parameter in display_parameters if parameter in controls}

    return selected_controls


def display_automaton(rule=90, base=2,
                      initial_conditions='1',
                      slice_bounds=None,
                      use_highlight=False, h_start=0, h_width=21, h_offset=0, h_steps=20,
                      grid_color='white', grid_thickness=0.2,
                      cell_color_0='black', cell_color_1='yellow', cell_color_2='red', cell_color_3='green',
                      rule_rows=1,
                      frame_steps=80, frame_width=151, fig_width=12) -> None:
    if not use_highlight:
        highlights = [HighlightBounds()]
    else:
        highlights = [HighlightBounds(steps=h_steps, start_step=h_start, offset=h_offset, width=h_width)]

    colors = [cell_color_0, cell_color_1, cell_color_2, cell_color_3]

    CellularAutomata(rule, initial_conditions, base=base,
                     frame_steps=frame_steps, frame_width=frame_width).display(
        CellularAutomata.DisplayParams(
            fig_width=fig_width,
            slice_spec=SliceSpec(slice_bounds[0], slice_bounds[1]-slice_bounds[0])
            if slice_bounds is not None else None,
            grid_color=grid_color, grid_thickness=grid_thickness,
            cell_colors=colors,
            highlights=highlights,
            check_highlight_bounds=False),
        rule_display_params=Rule.DisplayParams(cell_colors=colors, rows=rule_rows) if rule_rows > 0 else None,
        show_rule=rule_rows > 0
    )
    return


def interactive_display_automaton(frame_steps=80, frame_width=151, fig_width=12, display_parameters=None,
                                  controls=None) -> None:
    all_controls = get_controls(display_parameters=display_parameters,
                                frame_steps=frame_steps, frame_width=frame_width)

    # REV - Simpler version w/o layout
    # @interact(**all_controls)
    # def interactive_display(**kwargs):
    #     display_automaton(**kwargs, frame_steps=frame_steps, frame_width=frame_width, fig_width=fig_width)

    if controls is None:
        controls = all_controls.keys()

    def interactive_display(**kwargs):
        display_automaton(**kwargs, frame_steps=frame_steps, frame_width=frame_width, fig_width=fig_width)

    interactive_controls = interactive(interactive_display, **all_controls)

    def get_column_layout(control_number: int):
        return Layout(
            border='none',
            margin='0px',
            padding='0px',
            width='25%' if control_number > 0 else '0px',
            display='flex',
            flex_flow='column',
            align_items='flex-start',
            visibility='visible' if control_number > 0 else 'hidden'
        )

    output = interactive_controls.children[-1]

    all_column1_controls = ['rule', 'base', 'initial_conditions',
                            'cell_color_0', 'cell_color_1', 'cell_color_2', 'cell_color_3']
    all_column2_controls = ['slice_bounds', 'grid_color', 'grid_thickness', 'rule_rows']
    all_column3_controls = ['use_highlight', 'h_start', 'h_width', 'h_offset', 'h_steps']

    # column1_controls = filter(lambda item: item in controls, all_column1_controls)
    column1_controls = [c for c in controls if c in all_column1_controls]
    column2_controls = [c for c in controls if c in all_column2_controls]
    column3_controls = [c for c in controls if c in all_column3_controls]

    column1 = VBox([all_controls[name] for name in column1_controls],
                   layout=get_column_layout(control_number=len(column1_controls)))
    column2 = VBox([all_controls[name] for name in column2_controls],
                   layout=get_column_layout(control_number=len(column2_controls)))
    column3 = VBox([all_controls[name] for name in column3_controls],
                   layout=get_column_layout(control_number=len(column3_controls)))

    controls_layout = HBox([column1, column2, column3])

    display(controls_layout)
    display(output)
