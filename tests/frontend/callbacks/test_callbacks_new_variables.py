"""Import the names of callback functions you want to test.

from app import display, update

Test callback_new_variables_list - refactor method
Divide function into more callbacks
callback_change_language_variable_metadata_new_input

def test_display_accordions():
output =

def test_update_callback():
output = update(1, 0)
assert output == 'button 1: 1 & button 2: 0'

def test_display_callback():
def run_callback():
context_value.set(AttributeDict(**{"triggered_inputs": [{"prop_id": "btn-1-ctx-example.n_clicks"}]}))
return display(1, 0, 0)

ctx = copy_context()
output = ctx.run(run_callback)
assert output == f'You last clicked button with ID btn-1-ctx-example'
"""
