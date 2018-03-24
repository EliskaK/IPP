#!/usr/bin/env
import sys
import xml.etree.ElementTree as etree
DEBUG = True
if DEBUG:
    print(sys.argv)

class funcs:
    def my_args(arg):
        if (len(sys.argv) == 2):
            for value in sys.argv:
                if value == '--help':
                    print("Nápověda:")
                    print("Spuštění: python3.6 intepret.py [--source=file | --help]")
                    print("- file označuje vstupní XML soubor\n- help zobrazí tuto nápovědu")
                    sys.exit(0)
                if '--source=' in value:
                    return value[9:] # vse co je za --source= je nazev souboru s XML
class XMLclass:
    def open_file(arg):
        # pokus o otevreni souboru:
        try:
            file = open(inputfile, 'r');
        except FileNotFoundError:
            sys.stderr.write("Error: Soubor nelze otevřít.\n")
            sys.exit(11)

funcs = funcs();
xmlclass = XMLclass()

inputfile = funcs.my_args()
if DEBUG:
    print(inputfile)
# pokus o cteni souboru:
try:
    xmltree = etree.parse(inputfile)
except:
    sys.stderr.write("Error: Soubor nelze přečíst.\n")
    sys.exit(11)
