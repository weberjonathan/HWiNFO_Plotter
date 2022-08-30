# HWiNFO log parsing

Parse a HwInfo log file (csv) and display selected data points in a set of graphs. Export and import these selections.

```
python -m main [--export layout.txt] [--layout layout.txt] <logfile.csv>
```

HWiNFO log files are expected to be encoded in ISO-8859-1 (Latin-1). The same encoding is used for `layout.txt` files created by this script. Tested in German and English.

![example with multiple graphs and multiple series](/img/example.png)