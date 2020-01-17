# days-until

This CLI helps you count down to upcoming events. Inspired by [`year-progress`](https://github.com/alichtman/scripts/blob/master/year-progress.sh).

<h1 align="center">
  <img src="img/demo.png" width="50%" />
  <br />
</h1>

## Installation

```bash
$ git clone https://github.com/alichtman/days_until.git
$ cd days_until
$ python3 setup.py install
$ days-until  # The config file will be created the first time you run the program
$ vim $(days-until --config)  # Then, edit the configuration file
$ days-until
```

## Options

```bash
$ days_until -h
Usage: days_until [OPTIONS]

  Count down days until events.
  Written by Aaron Lichtman. https://github.com/alichtman/days_until

Options:
  -c, --compress     Compress output when printing.
  --config           Print path to config file.
  --remove           Interactively remove events with end dates that have
                     passed.
  -v, --version      Print version and author info.
  -h, -help, --help  Show this message and exit.
```

## Configuration and Events

`days-until` reads its configuration from `$XDG_CONFIG_HOME/.config/days-until.yaml` or `~/.config/days_until.yaml`.

Each event should be in the following format.

```yaml
event1:
  event: "Final Day in Switzerland"
  dates:
    start: "2019-12-7"
    end: "2019-12-20"
```

The top level keys (`event1` in this example) don't matter as long as they're unique. I tend to use `event{N}`, but anything will work.

- `event` is a string name for the event.
- `start` is the date on from which you'd like progress to be tracked.
- `end` is the date of the event.

All dates should be in `YYYY-MM-DD` format.

To remove entries interactively, use the `--remove` option. 

