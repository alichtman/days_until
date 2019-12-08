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

def show_progress_chart(start_date, end_date):
    """Displays the progress chart for an entry"""
    today = date.today()
    total_days = calculate_days_between(start_date, end_date)
    days_past_start = calculate_days_between(start_date, today)
    days_remaining = total_days - days_past_start
    percentage_complete = round((days_past_start / total_days) * 100, 1)
    print(GREEN + BOLD + f"Current Date: {today}")
    print(GREEN + BOLD + f"Days Remaining: {days_remaining}")
    
    fill_char = "▓"
    empty_char = "▓"
    # TODO: Print the chart with pretty graphics
    print(f"{percentage_complete}%\n")


def calculate_days_between(start_date, target_date):
    return (target_date - start_date).days


def show_entry(entry_data):
    print_section_header(entry_data["event"], BLUE)
    start_date = datetime.strptime(entry_data["dates"]["start"], "%Y-%m-%d").date()
    end_date = datetime.strptime(entry_data["dates"]["end"], "%Y-%m-%d").date()
    show_progress_chart(start_date, end_date)


######
# Main
######

def main():
    """Creates config if it doesn't exist, reads the config and displays the
    data contained in the config."""
    config_path = get_config_path()
    create_config_if_nonexistent(config_path)
    data = read_config(config_path)
    print(data)
    if data is None:
        print_error(f"No data in config: {config_path}")
        sys.exit()

    for key in data:
        show_entry(data[key])


if __name__ == "__main__":
    main()
