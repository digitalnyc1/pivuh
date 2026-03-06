#!/bin/sh

if [[ "$(uname)" == "Darwin" ]]; then
  pyinstaller main.py --clean --onefile --name "Pivuh" --add-data "images/*:images" --icon=images/pivuh.icns --windowed
else
  pyinstaller main.py --clean --onefile --name "Pivuh" --add-data "images/*:images"
fi
