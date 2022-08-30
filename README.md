# HWiNFO log parsing

Parse a HwInfo log file (csv) and display selected data points in a set of graphs. Export and import these selections.

```
python -m main [--export layout.txt] [--layout layout.txt] [--format FORMAT] <logfile.csv>
```

HWiNFO log files are expected to be encoded in ISO-8859-1 (Latin-1). The same encoding is used for `layout.txt` files created by this script. Tested in German and English.

The default date format used to parse timestamps is `%d.%m.%Y %H:%M:%S`. Use `--format` to supply your own if this is not the date format in your HWiNFO log file.

![example with multiple graphs and multiple series](/img/example.png)