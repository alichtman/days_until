import yaml
from datetime import date
from colorama import Fore, Style
from os import environ, path


########
# CONFIG
########

def get_config_path():
    """Gets path to config, respecting XDG spec"""
    xdg_config = environ.get('XDG_CONFIG_HOME') or path.join(path.expanduser('~'), '.config')
    return path.join(xdg_config, "days_until.yaml")


def create_config_if_nonexistent(path):
    """Creates the config file if it doesn't exist"""
    if not path.exists(path):
        with open(path, 'w'):
            pass
        print_notification(f"Created config at: {path}")


def read_config(config_path):
    """Reads the YAML config and returns it as a dict"""
    with open(config_path, "r") as f:
        data = yaml.full_load(f)
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


def print_progress_chart(start_date, end_date):
    """Displays the progress chart for an entry"""
    total_days = calculate_days_between(start_date, end_date)
    days_past_start = calculate_days_between(start_date, date.today())
    percentage_complete = days_past_start // total_days
    # TODO: Print the chart with pretty graphics
    print(f"{percentage_complete}%")


############
# Date Logic
############

def calculate_days_between(start_date, target_date):
    return (start_date - target_date).days


######
# Main
######

def main():
    """Creates config if it doesn't exist, reads the config and displays the
    data contained in the config."""
    config_path = get_config_path()
    create_config_if_nonexistent(config_path)
    data = read_config(config_path)
    if not data:
        print_error("No data in config.")

    for entry in data:
        print(entry)


if __name__ == "__main__":
    main()
