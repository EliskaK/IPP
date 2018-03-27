#!/usr/bin/env

# IPP projekt 2018
# 2. uloha
# interpret.py
# Eliska Kadlecova, xkadle34

import sys
import xml.etree.ElementTree as etree
DEBUG = True
if DEBUG:
    print(sys.argv)

instrukce = ['MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR', 'CALL',
            'RETURN', 'PUSHS', 'POPS', 'ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT',
            'EQ', 'AND', 'OR', 'NOT', 'INT2CHAR', 'STRI2INT', 'READ', 'WRITE',
            'CONCAT', 'STRLEN', 'GETCHAR', 'SETCHAR', 'TYPE', 'LABEL', 'JUMP',
            'JUMPIFEQ', 'JUMPIFNEQ', 'DPRINT', 'BREAK']

class funcs:
    def my_args(arg):
        if (len(sys.argv) == 2):
            value = sys.argv[1]
            if DEBUG:
                print(value)
            if value == '--help':
                print("Nápověda:")
                print("Spuštění: python3.6 intepret.py [--source=file | --help]")
                print("- file označuje vstupní XML soubor\n- --help zobrazí tuto nápovědu")
                sys.exit(0)
            elif '--source=' in value:
                return value[9:] # vse co je za --source= je nazev souboru s XML
            elif not '--source=' in value:
                print("Error: Chybí povinný parametr --stats=file. Pro více informací zadejte parametr --help.")
                sys.exit(10)
        else:
            # TODO BONUS
            print("Error: Špatně zadané argumenty. Pro více informací zadejte parametr --help.")
            sys.exit(10)

class XMLclass:
    def open_file(arg):
        # pokus o otevreni souboru:
        try:
            file = open(inputfile, 'r');
            return file;
        except FileNotFoundError:
            sys.stderr.write("Error: Soubor nelze otevřít.\n")
            sys.exit(11)
    def read_xml(arg):
        try:
            xmltree = etree.parse(inputfile)
            root = xmltree.getroot()
        except:
            sys.stderr.write("Error: Soubor XML má chybný formát.\n")
            sys.exit(31)
        else:
            return root
    # kontrola hlavicky XML: <program language="IPPcode18">
    def is_header_ok(self):
        if (xmlroot.attrib['language'] == "IPPcode18"):
            return True;
        else:
            return False;

#####################################################################################
funcs = funcs();
xmlclass = XMLclass();

inputfile = funcs.my_args()
if DEBUG:
    print(inputfile)
file = xmlclass.open_file()
xmlroot = xmlclass.read_xml()
if DEBUG:
    print(xmlroot)
if not xmlclass.is_header_ok():
    sys.stderr.write("Error: XML nemá validní hlavičku nebo kořenový element.\n")
    sys.exit(31)
