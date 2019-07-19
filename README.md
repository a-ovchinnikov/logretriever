# LogRetriever

A handy tool to monitor Apache logs and display statistics and alerts.

## Requirements

The tool has been tested with Python 2.7 and Python 3.4 under Linux. No
third-party libraries are required to run the tool.

## Installation

```bash
python setup.py --install
```

After installation is complete provide a configuration file based on
./etc/config.cfg.sample. By default the file is expected to be found at path
/etc/logretriever/config.cfg. For further details on configuration please
consider ./etc/config.cfg.sample

## Testing

To run unit tests from this repository use the following:
```bash
cd logretriever && nosetests ../tests
```

## Usage

To use the installed tool run the following command in your terminal:

```bash
logretriever
```

Alternatively one can run main.py directly without installing the tool.

For further insights please refer to project documentation.

## License

Licensed under CC-BY-NC-ND 4.0. Please refer to LICENSE file for further
details.
