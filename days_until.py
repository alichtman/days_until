# Standard Library Imports
import sys
from datetime import date, datetime
from os import environ, path

# 3rd-Party Imports
import yaml
from colorama import Fore, Style


########
# CONFIG
########

def get_config_path():
    """Gets path to config, respecting XDG spec"""
    xdg_config = environ.get('XDG_CONFIG_HOME') or path.join(path.expanduser('~'), '.config')
    return path.join(xdg_config, "days_until.yaml")


def create_config_if_nonexistent(config_path):
    """Creates the config file if it doesn't exist"""
    if not path.exists(config_path):
        with open(config_path, 'w'):
            pass
        print_notification(f"Created config at: {config_path}")


def read_config(config_path):
    """Reads the YAML config and returns it as a dict"""
    with open(config_path, "r") as f:
        try:
            data = yaml.safe_load(f)
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
BOLD = Style.BRIGHT
RESET = Style.RESET_ALL


def print_section_header(title, color):
    """Prints variable sized section header in bold color"""
    block = "#" * (len(title) + 4)
    print(color + BOLD + block)
    print("#", title, "#")
    print(block + "\n" + RESET)


def print_error(msg):
    print(RED + BOLD + f"ERROR: {msg}")


def print_notification(msg):
    print(GREEN + BOLD + f"{msg}")


#################
# Per-Event Logic
#################

def display_progress_chart(percentage_complete):
    fill_char = "▓"
    empty_char = "▓"
    chart_len = 20
    chart = fill_char * round(percentage_complete * 10 / 1000)
    print(len(chart))
    chart += empty_char * (chart_len - len(chart))
    # TODO: Print the chart with pretty graphics
    print(f"{chart} {percentage_complete}%\n")


def show_data_for_dates(start_date, end_date):
    """Displays the progress chart for an entry"""
    today = date.today()
    try:
        total_days = calculate_days_between(start_date, end_date)
        days_past_start = calculate_days_between(start_date, today)
    except ValueError:
        print_error("Start date after end date.")
        return

    print(GREEN + BOLD + f"Current Date: {today}")
    print(GREEN + BOLD + f"Days Remaining: {total_days - days_past_start}")
    percentage_complete = round((days_past_start / total_days) * 100, 1)
    display_progress_chart(percentage_complete)


def calculate_days_between(start_date, target_date):
    """Returns the number of days between start and end date. Raises ValueError if
    the end date is before the start date."""
    diff = (target_date - start_date).days
    if diff < 0:
        raise ValueError
    else:
        return diff


def show_entry(entry_data):
    print_section_header(entry_data["event"], BLUE)
    start_date = datetime.strptime(entry_data["dates"]["start"], "%Y-%m-%d").date()
    end_date = datetime.strptime(entry_data["dates"]["end"], "%Y-%m-%d").date()
    show_data_for_dates(start_date, end_date)


######
# Main
######

def main():
    """Creates config if it doesn't exist, reads the config and displays the
    data contained in the config."""
    config_path = get_config_path()
    create_config_if_nonexistent(config_path)
    data = read_config(config_path)
    if data is None:
        print_error(f"No data in config: {config_path}")
        sys.exit()

    for key in data:
        show_entry(data[key])


if __name__ == "__main__":
    main()
