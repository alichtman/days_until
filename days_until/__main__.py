# Standard Library Imports
import sys
import uuid
from datetime import date, datetime
from os import environ, path

# 3rd-Party Imports
import yaml
import click
from colorama import Fore, Style

# Module Imports
from .__version__ import __version__


########
# CONFIG
########

def get_config_path():
    """Gets path to config, respecting XDG spec"""
    xdg_config = environ.get('XDG_CONFIG_HOME') or \
        path.join(path.expanduser('~'), '.config')
    return path.join(xdg_config, "days_until.yaml")


def create_config_if_nonexistent(config_path):
    """Creates the config file if it doesn't exist"""
    if not path.exists(config_path):
        with open(config_path, 'w'):
            pass
        print_notification(f"Created config at: {config_path}")


def read_config(config_path):
    """Reads the YAML config and returns it as a dict"""
    with open(config_path, "r") as conf:
        try:
            data = yaml.safe_load(conf)
        except yaml.YAMLError as exc:
            print_error("Config was unparsable. Make sure it is properly formatted.")
            print(exc)
            sys.exit()
    return data


def write_config(config_path, data):
    """Writes data to config_path in YAML format"""
    with open(config_path, "w") as conf:
        yaml.dump(data, conf)


##########
# Printing
##########

RED = Fore.RED
BLUE = Fore.BLUE
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
WHITE = Fore.WHITE
BOLD = Style.BRIGHT
RESET = Style.RESET_ALL


def print_section_header(title, color):
    """Prints variable sized section header in bold color"""
    block = "#" * (len(title) + 4)
    print(color + BOLD + block)
    print("#", title, "#")
    print(block + "\n" + RESET)


def print_error(msg):
    """Prints message in bright red, prepended with 'ERROR: '"""
    print(RED + BOLD + f"ERROR: {msg}" + RESET)


def print_notification(msg):
    """Prints message in bright green."""
    print(GREEN + BOLD + f"{msg}" + RESET)


def print_blue_bold(msg):
    """Prints message in bright blue"""
    print(BLUE + BOLD + f"{msg}" + RESET)


###########
# Prompting
###########

def prompt_yes_no(question):
    """Prompt user for a yes/no answer. Returns True if 'y' is input, otherwise returns False."""
    question = f"{question.strip()} {WHITE} [y/N] "
    return input(question).strip().casefold() == "y"


def prompt_null_invalid(question):
    """Prompt user with a question. Returns the string that's entered if
    it's not None. Otherwise, prompts again.
    """
    question = f"{question.strip()}{WHITE}: "
    answer = input(question).strip()
    while answer == "":
        print_error("Input is required.")
        answer = prompt_null_invalid(question)
    return answer


def prompt_null_valid(question):
    """Prompt user with a question and return the string that's entered.
    """
    question = f"{question.strip()}{WHITE}: "
    return input(question).strip()


##################
# Removing Entries
##################

def removal_confirmation_and_update(config_path, new_config, events_to_remove):
    """Prompt user for confirmation to remove events_to_remove from the config.
    If confirmed, update config. Otherwise, don't. Print update messages.
    """
    print()
    for name in events_to_remove:
        print_blue_bold(f"[ {name} ]")
    print()

    number_of_events_to_remove = len(events_to_remove)
    if number_of_events_to_remove == 1:
        question = "Remove 1 entry?"
    else:
        question = f"Remove {number_of_events_to_remove} entries?"

    if prompt_yes_no(RED + BOLD + question):
        write_config(config_path, new_config)
        print_notification("Successfully removed.")
    else:
        print_notification("Aborted.")


def remove_entries_prompt(config_path, data):
    """
    Interactively remove entries. Writes the update config to config_path.
    :param config_path: Path to config file
    :param data: Current config data
    """
    if not data:
        print_error("No entries in config.")
        sys.exit()

    new_config = {}
    events_to_remove = []
    for key in data.keys():
        try:
            if prompt_yes_no(RED + f"Remove: {data[key]['event']}?"):
                events_to_remove.append(data[key]['event'])
            else:
                new_config[key] = data[key]
        except ValueError:
            continue

    if not events_to_remove:
        print_notification("No entries modified.")
        sys.exit()

    removal_confirmation_and_update(config_path, new_config, events_to_remove)


def clean_passed_entries(config_path, data):
    """
    Remove entries with end dates that have passed. Writes the update config
    to config_path.
    :param config_path: Path to config file
    :param data: Current config data
    """
    if not data:
        print_error("No entries in config.")
        sys.exit()

    new_config = {}
    events_to_remove = []
    for key in data.keys():
        try:
            end_date = datetime.strptime(data[key]["dates"]["end"], "%Y-%m-%d")
            if calculate_days_between(end_date.date(), date.today()) >= 0:
                events_to_remove.append(data[key]['event'])
            else:
                new_config[key] = data[key]
        except ValueError:
            continue

    if not events_to_remove:
        print_notification("No entries modified.")
        sys.exit()

    removal_confirmation_and_update(config_path, new_config, events_to_remove)


################
# Adding Entries
################

def add_entry(config_path, config_data):
    """Prompts a user for new event data. Assigns a random id for the event
    name, and writes it to the config_data.
    """
    event_name = prompt_null_invalid("Enter an event name")
    # TODO: Add date formatting validation.
    start_date = prompt_null_valid("Enter a start date (in YYYY-MM-DD format) or hit enter to default to today")
    if start_date == "":
        start_date = datetime.strftime(datetime.today(), "%Y-%m-%d")
    end_date = prompt_null_invalid("Enter an end date (in YYYY-MM-DD format)")

    # Generate unique id for the new event being added.
    unique_id = uuid.uuid4()
    while unique_id in config_data.keys():
        unique_id = uuid.uuid4()

    config_data[str(uuid.uuid4())] = {"event": event_name,
                                      "dates": {
                                          "start": start_date,
                                          "end": end_date
                                      },
                                      }
    write_config(config_path, config_data)
    print_notification(f"Successfully added event [ {event_name} ]")


#################
# Per-Event Logic
#################

def display_progress_chart(percentage_complete):
    """Prints a nice-looking chart filled proportionally to
    percentage_complete."""
    fill_char = "▓"
    empty_char = "░"
    chart_len = 20

    if percentage_complete >= 100:
        chart = fill_char * chart_len
        print(RED + f"{chart} COMPLETE\n")
    else:
        chart = fill_char * round(percentage_complete / 100 * chart_len)
        chart += empty_char * (chart_len - len(chart))
        print(GREEN + f"{chart} {percentage_complete}%\n")


def show_data_for_dates(start_date, end_date, compress=False):
    """Displays the progress chart for an entry"""
    today = date.today()
    try:
        total_days = calculate_days_between(start_date, end_date)
        days_past_start = calculate_days_between(start_date, today)
    except ValueError:
        print_error("Start date after end date.")
        return

    print(WHITE + f"Start Date:          {start_date.strftime('%b %d, %Y')}")
    print(WHITE + f"Current Date:        {today.strftime('%b %d, %Y')}")
    print(WHITE + f"End Date:            {end_date.strftime('%b %d, %Y')}")
    if not compress:
        print()

    # Show how close we are to the deadline with color
    days_remaining = total_days - days_past_start
    if days_remaining <= 0:
        days_remaining = RED + "None"
    elif days_remaining <= 10:
        days_remaining = YELLOW + str(days_remaining)

    print(WHITE + f"Days Since Start:    {days_past_start}")
    print(WHITE + f"Days Remaining:      {days_remaining}")

    if not compress:
        print()
    percentage_complete = round((days_past_start / total_days) * 100, 1)
    display_progress_chart(percentage_complete)


def calculate_days_between(start_date, target_date):
    """Returns the number of days between start and end date. Raises ValueError if
    the end date is before the start date."""
    diff = (target_date - start_date).days
    if diff < 0:
        raise ValueError
    return diff


def show_entry(entry_data, compress):
    """Prints all data for an entry"""
    print_section_header(entry_data["event"], BLUE)
    start_date = datetime.strptime(entry_data["dates"]["start"], "%Y-%m-%d").date()
    end_date = datetime.strptime(entry_data["dates"]["end"], "%Y-%m-%d").date()
    show_data_for_dates(start_date, end_date, compress)


######
# Main
######

def print_version_info():
    """Print version and author info."""
    print(f"v{__version__} by Aaron Lichtman")

# custom help options
@click.command(context_settings=dict(help_option_names=['-h', '-help', '--help']))
@click.option('--add', is_flag=True, help="Prompt to add events.")
@click.option('--clean', is_flag=True, help="Remove events with end dates that have passed.")
@click.option('--compress', is_flag=True, help="Compress output when printing.")
@click.option('--config', is_flag=True, help="Print path to config file.")
@click.option('--remove', is_flag=True, help="Interactively remove events.")
@click.option('--version', '-v', is_flag=True, help='Print version and author info.')
def main(add=False, clean=False, compress=False, config=False, remove=False, version=False):
    """Count down days until events.\n
    \tWritten by Aaron Lichtman. https://github.com/alichtman/days_until"""
    if version:
        print_version_info()
        sys.exit()

    config_path = get_config_path()
    create_config_if_nonexistent(config_path)

    if config:
        print(config_path)
        sys.exit()

    data = read_config(config_path)

    if add:
        add_entry(config_path, data)
        sys.exit()

    if data is None:
        print_error(f"No data in config: {config_path}")
        sys.exit()

    if remove:
        remove_entries_prompt(config_path, data)
        sys.exit()

    if clean:
        clean_passed_entries(config_path, data)
        sys.exit()

    # Normal display mode
    for key in data:
        show_entry(data[key], compress)


if __name__ == "__main__":
    main()
