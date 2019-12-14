# Module Imports
from .__version__ import __version__

# Standard Library Imports
import sys
from datetime import date, datetime
from os import environ, path

# 3rd-Party Imports
import yaml
import click
from colorama import Fore, Style


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


##########
# Printing
##########

RED = Fore.RED
BLUE = Fore.BLUE
GREEN = Fore.GREEN
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
    print(RED + BOLD + f"ERROR: {msg}")


def print_notification(msg):
    """Prints message in bright green."""
    print(GREEN + BOLD + f"{msg}")


#################
# Per-Event Logic
#################

def display_progress_chart(percentage_complete):
    """Prints a nice-looking chart filled proportionally to
    percentage_complete."""
    fill_char = "▓"
    empty_char = "░"
    chart_len = 20
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
    print(WHITE + f"Days Passed:         {days_past_start}")
    print(WHITE + f"Days Remaining:      {total_days - days_past_start}")
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
@click.option('--config', is_flag=True, default=False, help="Print config path.")
@click.option('--compress', '-c', is_flag=True, default=False, help="Compress output when printing.")
@click.option('--version', '-v', is_flag=True, default=False, help='Print version and author info.')
def main(config, compress, version):
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
    if data is None:
        print_error(f"No data in config: {config_path}")
        sys.exit()

    for key in data:
        show_entry(data[key], compress)


if __name__ == "__main__":
    main()
