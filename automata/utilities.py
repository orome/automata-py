from ipywidgets import IntSlider, Checkbox, interact
from .core import Rule, HighlightBounds, CellularAutomata


def get_controls(control_names, eg_frame_steps=25, eg_frame_width=201):
    rule_slider = IntSlider(min=0, max=Rule(0, base=2).n_rules - 1, step=1, value=90, description='Rule')
    base_slider = IntSlider(min=2, max=3, step=1, value=2, description='Base')

    # Adjust the max r to correspond to the base
    def update_r_max():
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

    controls = {
        'rule_slider': rule_slider,
        'base_slider': base_slider,
        'highlight_checkbox': highlight_checkbox,
        'h_start_slider': h_start_slider,
        'h_width_slider': h_width_slider,
        'h_offset_slider': h_offset_slider,
        'h_steps_slider': h_steps_slider
    }

    # Filter controls based on the provided list of control names
    selected_controls = {name: controls[name] for name in control_names if name in controls}

    return selected_controls


def display_automaton(rule_slider, base_slider, highlight_checkbox, h_start_slider, h_width_slider, h_offset_slider,
                      h_steps_slider, eg_frame_steps=80, eg_frame_width=151):
    if not highlight_checkbox:
        highlights = [HighlightBounds()]
    else:
        highlights = [HighlightBounds(steps=h_steps_slider, start_step=h_start_slider, offset=h_offset_slider,
                                      width=h_width_slider)]

    CellularAutomata(rule_slider, '1', base=base_slider, frame_steps=eg_frame_steps,
                     frame_width=eg_frame_width).display(
        CellularAutomata.DisplayParams(
            fig_width=12,
            grid_color='white', grid_width=0.2, cell_colors=['black', 'yellow', 'red', 'orange'],
            highlights=highlights,
            check_highlight_bounds=False),
        rule_display_params=None,
        show_rule=True
    )


def interactive_display_automaton(eg_frame_steps=80, eg_frame_width=151):
    controls = get_controls(
        ['rule_slider', 'base_slider',
         'highlight_checkbox', 'h_start_slider', 'h_width_slider', 'h_offset_slider', 'h_steps_slider'])

    @interact(**controls)
    def interactive_display(rule_slider, base_slider,
                            highlight_checkbox,
                            h_start_slider, h_width_slider, h_offset_slider, h_steps_slider):
        display_automaton(rule_slider, base_slider,
                          highlight_checkbox,
                          h_start_slider, h_width_slider, h_offset_slider, h_steps_slider,
                          eg_frame_steps, eg_frame_width)
