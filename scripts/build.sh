#!/bin/sh

pyinstaller main.pyw --clean --onefile --name "Pivuh" --icon=image/pivuh.ico --add-data "images/*:images"
