#!/bin/sh

if [[ "$(uname)" == "Darwin" ]]; then
  pyinstaller main.py --clean --onefile --noconsole --name "Pivuh" --add-data "images/*:images" --icon=images/pivuh.icns
else
  pyinstaller main.py --clean --onefile --name "Pivuh" --add-data "images/*:images"
fi
