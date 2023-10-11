# noinspection PyPackageRequirements
from ipywidgets import IntSlider, Checkbox, ColorPicker, interact
from .core import Rule, HighlightBounds, CellularAutomata

# USE - For use in Jupyter notebooks; assumes ipywidgets is installed in the Python environment


def get_controls(control_names, eg_frame_steps=25, eg_frame_width=201):
    rule_slider = IntSlider(min=0, max=Rule(0, base=2).n_rules - 1, step=1, value=90, description='Rule')
    base_slider = IntSlider(min=2, max=3, step=1, value=2, description='Base')

    # Adjust the max r to correspond to the base
    def update_r_max(*args):
        rule_slider.max = Rule(0, base=base_slider.value).n_rules - 1

    base_slider.observe(update_r_max, names='value')

    highlight_checkbox = Checkbox(value=True, description='Focus Highlight')
    h_start_slider = IntSlider(min=0, max=eg_frame_steps, step=1, value=0, description='Start')
    h_width_slider = IntSlider(min=1, max=eg_frame_width, step=1, value=21, description='Width')
    h_offset_slider = IntSlider(min=-eg_frame_width // 2, max=eg_frame_width // 2, step=1, value=0,
                                description='Offset')
    h_steps_slider = IntSlider(min=1, max=eg_frame_steps, step=1, value=20, description='Steps')

    # Enable/disable h_start and h_width based on the checkbox
    def update_highlight_controls(change):
        h_start_slider.disabled = not change.new
        h_width_slider.disabled = not change.new
        h_offset_slider.disabled = not change.new
        h_steps_slider.disabled = not change.new

    highlight_checkbox.observe(update_highlight_controls, names='value')

    grid_color_picker = ColorPicker(concise=True, value='white', disabled=False, description='Grid color')

    cell_color_pickers = {0: ColorPicker(concise=True, value='black', disabled=False, description='0'),
                          1: ColorPicker(concise=True, value='yellow', disabled=False, description='1'),
                          2: ColorPicker(concise=True, value='red', disabled=False, description='2'),
                          3: ColorPicker(concise=True, value='green', disabled=False, description='3')}

    # Enable/disable cell color pickers based on current value of base
    def update_grid_color_controls(*args):
        # for digit in cell_color_pickers.keys():
        #     cell_color_pickers[digit].disabled = digit > b_slider.value - 1
        # for digit in cell_color_pickers.keys():
        #     if digit > b_slider.value - 1:
        #         cell_color_pickers[digit].layout.visibility = 'hidden'
        #     else:
        #         cell_color_pickers[digit].layout.visibility = 'visible'
        for digit in cell_color_pickers.keys():
            if digit > base_slider.value - 1:
                cell_color_pickers[digit].layout.display = 'none'
            else:
                cell_color_pickers[digit].layout.display = 'flex'  # REV - or 'block' or 'inline'

    base_slider.observe(update_grid_color_controls, names='value')
    update_grid_color_controls()

    controls = {
        'rule_slider': rule_slider,
        'base_slider': base_slider,
        'highlight_checkbox': highlight_checkbox,
        'h_start_slider': h_start_slider,
        'h_width_slider': h_width_slider,
        'h_offset_slider': h_offset_slider,
        'h_steps_slider': h_steps_slider,
        'grid_color_picker': grid_color_picker,
        'cell_color_picker_0': cell_color_pickers[0],
        'cell_color_picker_1': cell_color_pickers[1],
        'cell_color_picker_2': cell_color_pickers[2],
        'cell_color_picker_3': cell_color_pickers[3]
    }

    # Filter controls based on the provided list of control names
    selected_controls = {name: controls[name] for name in control_names if name in controls}

    return selected_controls


def display_automaton(rule_slider, base_slider,
                      use_highlight_checkbox=True, h_start=0, h_width=21, h_offset=0, h_steps=20,
                      grid_color='white',
                      cell_color_0='black', cell_color_1='yellow', cell_color_2='red', cell_color_3='green',
                      eg_frame_steps=80, eg_frame_width=151):
    if not use_highlight_checkbox:
        highlights = [HighlightBounds()]
    else:
        highlights = [HighlightBounds(steps=h_steps, start_step=h_start, offset=h_offset, width=h_width)]

    CellularAutomata(rule_slider, '1', base=base_slider,
                     frame_steps=eg_frame_steps, frame_width=eg_frame_width).display(
        CellularAutomata.DisplayParams(
            fig_width=12,
            grid_color=grid_color, grid_width=0.2,
            cell_colors=[cell_color_0, cell_color_1, cell_color_2, cell_color_3],
            highlights=highlights,
            check_highlight_bounds=False),
        rule_display_params=None,
        show_rule=True
    )
    return


def interactive_display_automaton(frame_steps=80, frame_width=151):
    controls = get_controls(
        ['rule_slider', 'base_slider',
         'highlight_checkbox', 'h_start_slider', 'h_width_slider', 'h_offset_slider', 'h_steps_slider',
         'grid_color_picker',
         'cell_color_picker_0', 'cell_color_picker_1', 'cell_color_picker_2', 'cell_color_picker_3'],
        eg_frame_steps=frame_steps, eg_frame_width=frame_width)

    @interact(**controls)
    def interactive_display(rule_slider, base_slider,
                            highlight_checkbox, h_start_slider, h_width_slider, h_offset_slider, h_steps_slider,
                            grid_color_picker,
                            cell_color_picker_0, cell_color_picker_1, cell_color_picker_2, cell_color_picker_3):
        display_automaton(rule_slider, base_slider,
                          highlight_checkbox, h_start_slider, h_width_slider, h_offset_slider, h_steps_slider,
                          grid_color_picker,
                          cell_color_picker_0, cell_color_picker_1, cell_color_picker_2, cell_color_picker_3,
                          frame_steps, frame_width)
