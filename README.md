# days-until

This CLI allows you to count down to upcoming events.

<h1 align="center">
  <img src="img/demo.png" width="50%" />
  <br />
</h1>

## Installation

```bash
$ git clone https://github.com/alichtman/days_until.git
$ cd days_until
$ python3 setup.py install
$ days-until
```

## Configuration

`days-until` reads its configuration from `$XDG_CONFIG_HOME/.config/days-until.yaml` or `~/.config/days_until.yaml`.

Each event should be in this format. The top level keys doesn't matter as long as they are unique. I tend to use `event{N}`, but whatever you'd like to use works.

```yaml
event1:
  event: "Final Day in Switzerland"
  dates:
    start: "2019-12-7"
    end: "2019-12-20"
```

`event` is a string name for the event.
`start` is the date on from which you'd like progress to be tracked.
`end` is the date of the event.

All dates should be in `YYYY-MM-DD` format.
