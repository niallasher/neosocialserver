AFFIRMATIVE_RESPONSES = ['y', 'yes']
NEGATIVE_RESPONSES = ['n', 'no']


def get_input_bool(prompt):
    while True:
        user_input = input(prompt)
        if user_input.lower() in AFFIRMATIVE_RESPONSES:
            return True
        elif user_input.lower() in NEGATIVE_RESPONSES:
            return False


def get_str_input(prompt):
    while True:
        user_input = input(prompt)
        if user_input:
            return user_input


def get_int_input(prompt):
    while True:
        user_input = input(prompt)
        if user_input:
            try:
                return int(user_input)
            except ValueError:
                print('Please enter a number')
