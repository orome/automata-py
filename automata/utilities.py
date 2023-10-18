# noinspection PyPackageRequirements
from ipywidgets import IntSlider, Checkbox, ColorPicker, FloatSlider, interact
from .core import Rule, HighlightBounds, CellularAutomata

# USE - For use in Jupyter notebooks; assumes ipywidgets is installed in the Python environment

# TBD - Should be better coordinated with number of colors and color controls
_DISPLAY_BASE_MAX = 4


def get_controls(display_parameters=None, frame_steps=25, frame_width=201) -> dict:
    rule_slider = IntSlider(min=0, max=Rule(0, base=2).n_rules - 1, step=1, value=90, description='Rule')
    base_slider = IntSlider(min=2, max=_DISPLAY_BASE_MAX, step=1, value=2, description='Base')

    # Adjust the max r to correspond to the base
    def update_r_max(*_) -> None:
        rule_slider.max = Rule(0, base=int(base_slider.value)).n_rules - 1
    base_slider.observe(update_r_max, names='value')
    update_r_max()

    use_highlight_checkbox = Checkbox(value=False, description='Focus Highlight')
    h_start_slider = IntSlider(min=0, max=frame_steps, step=1, value=0, description='Start')
    h_width_slider = IntSlider(min=1, max=frame_width, step=1, value=21, description='Width')
    h_offset_slider = IntSlider(min=-frame_width // 2, max=frame_width // 2, step=1, value=0,
                                description='Offset')
    h_steps_slider = IntSlider(min=1, max=frame_steps, step=1, value=20, description='Steps')

    rule_rows_slider = IntSlider(min=0, max=6, step=1, value=Rule(0, base=2).best_rows(),
                                 description='Rule rows')

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

    grid_color_picker = ColorPicker(concise=True, value='white', disabled=False, description='Grid color')
    grid_thickness_slider = FloatSlider(min=0, max=2, step=0.025, value=0.2, description='Grid thickness')

    cell_color_pickers = {0: ColorPicker(concise=True, value='black', disabled=False, description='0'),
                          1: ColorPicker(concise=True, value='yellow', disabled=False, description='1'),
                          2: ColorPicker(concise=True, value='red', disabled=False, description='2'),
                          3: ColorPicker(concise=True, value='green', disabled=False, description='3')}

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

    # Filter controls based on the provided list of control names
    selected_controls = {parameter: controls[parameter] for parameter in display_parameters if parameter in controls}

    return selected_controls


def display_automaton(rule=90, base=2,
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

    CellularAutomata(rule, '1', base=base,
                     frame_steps=frame_steps, frame_width=frame_width).display(
        CellularAutomata.DisplayParams(
            fig_width=fig_width,
            grid_color=grid_color, grid_thickness=grid_thickness,
            cell_colors=colors,
            highlights=highlights,
            check_highlight_bounds=False),
        rule_display_params=Rule.DisplayParams(cell_colors=colors, rows=rule_rows) if rule_rows > 0 else None,
        show_rule=rule_rows > 0
    )
    return


def interactive_display_automaton(frame_steps=80, frame_width=151, fig_width=12, display_parameters=None) -> None:
    controls = get_controls(display_parameters=display_parameters,
                            frame_steps=frame_steps, frame_width=frame_width)

    @interact(**controls)
    def interactive_display(**kwargs):
        display_automaton(**kwargs, frame_steps=frame_steps, frame_width=frame_width, fig_width=fig_width)
