#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import sys, getopt, re
DEBUG = 0
def load_data(arg):
	try:
		tree = ET.parse(arg)
		xmlroot = tree.getroot()
	except:
		print("31: Špatná struktura XML souboru.")
		sys.exit(31)
	else:
		return xmlroot

def check_header(root):
	if(root.tag != "program") or ('language' not in root.attrib) or (root.attrib['language']  !=  "IPPcode18"):
		print("31: Nesprávně zadaná hlavička!")
		sys.exit(31)
	order = 1
	for ch in xmlroot:
		if(ch.tag != "instruction") or (ch.attrib["opcode"] not in operation) or (ch.attrib["order"] != str(order)):
			print("31: Neznámá instrukce/atribut neobsahuje řetězec instruction nebo opcode.")
			sys.exit(31)
		order += 1

def find_label(child, root):
	labels = {}
	for child in root:
		if(child.attrib["opcode"] in ['LABEL']):
			count_args(child, 1)
			new_label = control_get_value(child[0], "label", labels)
			labels[child[0].text] = child.attrib["order"]
	return labels

def check_instr_arg(child):
	argplus=1
	for subchild in child:
		if(subchild.tag != "arg"+str(argplus)) or (subchild.attrib["type"] not in types):
			print("31: Neznámý typ v argumentu/špatné pořadí argumentů instrukce.")
			sys.exit(31)
		if subchild.attrib["type"] != "string" and subchild.text is None:
			print("32: Chybí hodnota.")
			sys.exit(32)
		elif (subchild.text is not None and " " in subchild.text) and (subchild.attrib["type"] == "string" or subchild.attrib["type"] == "int"):
			print("31: Mezera v hodnotě.")
			sys.exit(31)
		argplus+=1

def check_atrib_type(type, atrib_type):
	if(type != atrib_type):
		print("32: Argument nemá zadán správný typ.")
		sys.exit(32)

def get_atrib_type(atrib_type):
	if(atrib_type == "var"):
		return atrib_type
	elif(atrib_type == "int"):
		return atrib_type
	elif(atrib_type == "bool"):
		return atrib_type
	elif(atrib_type == "string"):
		return atrib_type
	elif(atrib_type == "label"):
		return atrib_type
	elif(atrib_type == "type"):
		return atrib_type
	else:
		print("32: Argument nemá zadán validní typ.")
		sys.exit(32)

def get_type(value):
	if isinstance(value, str) and value not in ['true', 'false'] or value == None:
		return "string"
	elif isinstance(value, int):
		return "int"
	elif isinstance(value, str):
		return "bool"

def var_type_control(var):
	if type(var) is int:
		return "int";
	else:
		if isinstance(var, str) and var not in ['true', 'false', 'True', 'False'] or var == None:
			return "string";
		elif (isinstance(var, bool)) or (isinstance(var, str) and var in ['true', 'false', 'True', 'False']):
			return "bool";
		elif var.isdigit():
			return "int";

def is_int(num):
	try:
		int(num)
	except:
		print("53: Argument není typu int.")
		sys.exit(53)
	return num;

def is_bool(val):
	if val == "true":
		return True;
	elif val == "false":
		return False;
	else:
		print("53: Argument není typu bool.")
		sys.exit(53)

def is_var(var):
	if "GF@" in var or "TF@" in var or "LF@" in var:
		return var
	else:
		print("53: Argument není typu var.")
		sys.exit(53)

def is_string(string):
	if isinstance(string, str):
		esc = re.findall("\\\\\d\d\d", string)
		for escape_seq in esc:
			string = string.replace(escape_seq, chr(int(escape_seq.lstrip('\\'))))
		return string
	else:
		print("53: Argument není typu string.")
		sys.exit(53)

def is_label(label, labels):
	if label not in labels:
		print("52: Neexistující návěští.")
		sys.exit(52)

def control_get_value(value, type, lab):
	if type == "var":
		is_var(value.text)
		check_atrib_type("var", value.attrib["type"])
		return value.text;
	elif type == "int":
		is_int(value.text)
		check_atrib_type("int", value.attrib["type"])
		return int(value.text);
	elif type == "bool":
		is_bool(value.text)
		check_atrib_type("bool", value.attrib["type"])
		return value.text;
	elif type == "string":
		if value.text == None:
			return ""
		is_string(value.text)
		check_atrib_type("string", value.attrib["type"])
		return value.text;
	elif type == "type":
		if value.text not in ['int', 'bool', 'string']:
			print("52: Argument type má nesprávnou hodnotu.")
			sys.exit(52)
	elif type == "label":
		is_label(value.text, lab)
		return value.text
	else:
		print("32: Nesprávný typ.")
		sys.exit(32)

def var_control(frame_name, var_name, global_frame, local_frame, temp_frame):
	if frame_name == "GF":
		if var_name not in global_frame:
			print("54: Neexistující proměnná.")
			sys.exit(54)

	elif frame_name == "TF":
		if temp_frame == None:
			print("55: Neexistující rámec.")
			sys.exit(55)
		if var_name not in temp_frame:
			print("54: Neexistující proměnná.")
			sys.exit(54)

	elif frame_name == "LF":
		if local_frame == None:
			print("55: Neexistující rámec.")
			sys.exit(55)
		if var_name not in local_frame:
			print("54: Neexistující proměnná.")
			sys.exit(54)

def get_var(var_name, global_frame, local_frame, temp_frame):
	if var_name in global_frame:
		return global_frame[var_name]
	elif local_frame is not None and var_name in local_frame:
		return local_frame[var_name]
	elif temp_frame is not None and var_name in temp_frame:
		return temp_frame[var_name]
	else:
		print("54: Proměnná neexistuje v žádném rámci.")
		sys.exit(54)

def def_var(frame_name, var_name, global_frame, local_frame, temp_frame):
	if frame_name == "GF":
		global_frame[var_name] = None

	elif frame_name == "TF":
		if(temp_frame == None):
			print("55: Neexistující rámec.")
			sys.exit(55)
		else:
			temp_frame[var_name] = None

	elif frame_name == "LF":
		if(local_frame == None):
			print("55: Neexistující rámec.")
			sys.exit(55)
		else:
			local_frame[var_name] = None
	else:
		print("55: Nevalidní označení rámce.")
		sys.exit(55)

def set_val_to_var(frame_name, var_name, val, global_frame, local_frame, temp_frame):
	if frame_name == "GF":
		global_frame[var_name] = val

	elif frame_name == "TF":
		temp_frame[var_name] = val

	elif frame_name == "LF":
		local_frame[var_name] = val

def relational_op(val, values, global_frame, local_frame, temp_frame, labels):
	count_args(val, 3)
	values.append(control_get_value(val[0], "var", labels))
	var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
	typ1 = get_atrib_type(val[1].attrib["type"])
	typ2 = get_atrib_type(val[2].attrib["type"])
	if typ1 == 'int' or typ1 == 'string' or typ1 == 'bool' or typ1 == 'var':
		values.append(control_get_value(val[1], typ1, labels))
		if typ1 == 'var':
			var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
			values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
	else:
		print("53: Nesprávný typ operandu.")
		sys.exit(53)
	if typ2 == 'int' or typ2 == 'string' or typ2 == 'bool' or typ2 == 'var':
		values.append(control_get_value(val[2], typ2, labels))
		if typ2 == 'var':
			var_control(values[2][:2], values[2][3:], global_frame, local_frame, temp_frame)
			values[2] = get_var(values[2][3:], global_frame, local_frame, temp_frame)
	else:
		print("53: Nesprávný typ instrukce.")
		sys.exit(53)
	if(type(values[1]) != type(values[2])):
		print("53: Typy operandů nejsou stejné.")
		sys.exit(53)
	return values

def bool_op(val, values, global_frame, local_frame, temp_frame, labels):
	values.append(control_get_value(val[0], "var", labels))
	var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
	typ1 = get_atrib_type(val[1].attrib["type"])
	typ2 = get_atrib_type(val[2].attrib["type"])
	if typ1 == "bool" or typ1 == "var":
		values.append(control_get_value(val[1], typ1, labels))
		if typ1 == "var":
			var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
			values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
			is_bool(values[1])
	else:
		print("53: Nesprávný typ operandů.")
		sys.exit(53)
	if typ2 == "bool" or typ2 == "var":
		values.append(control_get_value(val[2], typ2, labels))
		if typ2 == "var":
			var_control(values[2][:2], values[2][3:], global_frame, local_frame, temp_frame)
			values[2] = get_var(values[2][3:], global_frame, local_frame, temp_frame)
			is_bool(values[2])
	else:
		print("53: Nesprávný typ operandů.")
		sys.exit(53)
	var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
	return values;

def aritmetic_op(val, values, global_frame, local_frame, temp_frame, labels):
	count_args(val, 3)
	values.append(control_get_value(val[0], "var", labels))
	var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
	typ1 = get_atrib_type(val[1].attrib["type"])
	typ2 = get_atrib_type(val[2].attrib["type"])
	if typ1 == "int" or typ1 == "var":
		values.append(control_get_value(val[1], typ1, labels))
		if typ1 == "var":
			var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
			values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
			is_int(values[1])
	else:
		print("53: Nesprávný typ operandů.")
		sys.exit(53)
	if typ2 == "int" or typ2 == "var":
		values.append(control_get_value(val[2], typ2, labels))
		if typ2 == "var":
			var_control(values[2][:2], values[2][3:], global_frame, local_frame, temp_frame)
			values[2] = get_var(values[2][3:], global_frame, local_frame, temp_frame)
			is_int(values[2])
	else:
		print("53: Nesprávný typ operandů.")
		sys.exit(53)
	var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
	return values;

def interpret(root):
	for child in root:
		global labels, global_frame, local_frame, temp_frame, stack, frame_stack, call_stack, order
		values = []
		order += 1
		global instr_total
		instr_total += 1
		check_instr_arg(child)
		if DEBUG:
			print (child.attrib["opcode"])
		if(child.attrib["opcode"] in ['MOVE']):
			count_args(child, 2)
			values.append(control_get_value(child[0], "var", labels))
			var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
			typ = get_atrib_type(child[1].attrib["type"])
			values.append(control_get_value(child[1], typ, labels))
			if typ == "var":
				var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
				values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
			typ = get_type(values[1])
			if typ == 'string':
				values[1] = is_string(values[1])
			if DEBUG:
				print(typ)
			if values[1] == None:
				print("56: Chybějící hodnota v proměnné.")
				sys.exit(56)

			set_val_to_var(values[0][:2], values[0][3:], values[1], global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['CREATEFRAME']):
			count_args(child, 0)
			temp_frame = {}

		elif(child.attrib["opcode"] in ['PUSHFRAME']):
			count_args(child, 0)
			if(temp_frame == None):
				print("55: Rámec neexistuje.")
				sys.exit(55)
			frame_stack.append(temp_frame)
			local_frame = frame_stack[len(frame_stack)-1]
			temp_frame = None

		elif(child.attrib["opcode"] in ['POPFRAME']):
			count_args(child, 0)
			if(local_frame == None):
				print("55: Rámec neexistuje.")
				sys.exit(55)
			temp_frame = frame_stack[0]
			frame_stack.pop(0)
			if len(frame_stack) != 0:
				local_frame = frame_stack[len(frame_stack)-1]
			else:
				local_frame = None

		elif(child.attrib["opcode"] in ['DEFVAR']):
			count_args(child, 1)
			values.append(control_get_value(child[0], "var", labels))
			def_var(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['CALL']):
			count_args(child, 1)
			values.append(control_get_value(child[0], "label", labels))
			if values[0] not in labels:
				print("52: Neexistující návěští.")
				sys.exit(52)
			call_stack.append(int(child.attrib["order"]))
			interpret(xmlroot[int(labels[child[0].text]):])
			break

		elif(child.attrib["opcode"] in ['RETURN']):
			count_args(child, 0)
			if call_stack == []:
				print("56: Zásobník volání je prázdný.")
				sys.exit(56)
			interpret(xmlroot[call_stack.pop():])
			break
		elif(child.attrib["opcode"] in ['PUSHS']):
			count_args(child, 1)
			typ = get_atrib_type(child[0].attrib["type"])
			values.append(control_get_value(child[0], typ, labels))
			if typ == 'var':
				var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
				values[0] = get_var(values[0][3:], global_frame, local_frame, temp_frame)
			elif typ in ['label', 'type']:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			stack.append(values[0])

		elif(child.attrib["opcode"] in ['POPS']):
			count_args(child, 1)
			if stack == []:
				print("56: Zásobník je prázdný.")
				sys.exit(56)
			typ = get_atrib_type(child[0].attrib["type"])
			if typ == 'var':
				values.append(control_get_value(child[0], typ, labels))
				var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			set_val_to_var(values[0][:2], values[0][3:], stack.pop(),global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['ADD']):
			values = aritmetic_op(child, values, global_frame, local_frame, temp_frame, labels)
			result = values[1] + values[2]
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['SUB']):
			values = aritmetic_op(child, values, global_frame, local_frame, temp_frame, labels)
			result = values[1] - values[2]
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['MUL']):
			values = aritmetic_op(child, values, global_frame, local_frame, temp_frame, labels)
			result = values[1] * values[2]
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['IDIV']):
			values = aritmetic_op(child, values, global_frame, local_frame, temp_frame, labels)
			if(int(values[2]) == 0):
				print("57: Dělení nulou!")
				sys.exit(57)
			result = int(values[1]) // int(values[2])
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['LT']):
			values = relational_op(child, values, global_frame, local_frame, temp_frame, labels)
			result = values[1] < values[2]
			result = str(result).lower()
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['GT']):
			values = relational_op(child, values, global_frame, local_frame, temp_frame, labels)
			result = values[1] > values[2]
			result = str(result).lower()
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['EQ']):
			values = relational_op(child, values, global_frame, local_frame, temp_frame, labels)
			result = values[1] == values[2]
			result = str(result).lower()
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['AND']):
			values = bool_op(child, values, global_frame, local_frame, temp_frame, labels)
			if((values[1]) == "true" and (values[2]) == "true"):
				result = 'true'
			else:
				result = 'false'
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['OR']):
			values = bool_op(child, values, global_frame, local_frame, temp_frame, labels)
			if((values[1]) == "true" or (values[2]) == "true"):
				result = 'true'
			else:
				result= 'false'
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['NOT']):
			count_args(child, 2)
			values.append(control_get_value(child[0], "var", labels))
			var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
			values.append(control_get_value(child[1], "bool", labels))
			if((values[1]) == "true"):
				result = 'false'
			else:
				result = 'true'
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['INT2CHAR']):
			count_args(child, 2)
			values.append(control_get_value(child[0], "var", labels))
			var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
			typ1 = get_atrib_type(child[1].attrib["type"])
			if typ1 == 'int' or typ1 == 'var':
				values.append(control_get_value(child[1], typ1, labels))
				if typ1 == 'var':
					var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
					values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
					is_int(values[1])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			try:
				result = chr(values[1])
			except:
				print("58: Nevalidní ordinální hodnota znaku.")
				sys.exit(58)
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['STRI2INT']):
			count_args(child, 3)
			values.append(control_get_value(child[0], "var", labels))
			var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
			typ1 = get_atrib_type(child[1].attrib["type"])
			if typ1 == 'string' or typ1 == 'var':
				values.append(control_get_value(child[1], typ1, labels))
				if typ1 == 'var':
					var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
					values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
					values[1] = is_string(values[1])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			typ2 = get_atrib_type(child[2].attrib["type"])
			if typ2 == 'int' or typ2 == 'var':
				values.append(control_get_value(child[2], typ2, labels))
				if typ2 == 'var':
					var_control(values[2][:2], values[2][3:], global_frame, local_frame, temp_frame)
					values[2] = get_var(values[2][3:], global_frame, local_frame, temp_frame)
					is_int(values[2])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			if(len(values[1]) <= values[2]):
				print("58: Index je mimo zadaný řetězec.")
				sys.exit(58)
			result = ord(values[1][values[2]])
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['READ']):
			count_args(child, 2)
			values.append(control_get_value(child[0], "var", labels))
			var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
			values.append(control_get_value(child[1], "type", labels))
			try:
				inpt = input()
			except: # odchyceni, kdyz neni zadano nic
				if (get_atrib_type(child[1].attrib["type"]) == 'type'):
					if (child[1].text == 'int'):
						result = 0
					elif (child[1].text == 'string'):
						result = ''
					elif (child[1].text == 'bool'):
						result = False
					else:
						print("52: Argument type má nesprávnou hodnotu.")
						sys.exit(52)
				else:
					print("53: Nesprávný typ operandu.")
					sys.exit(53)
			else: # kdyz nedojde k vyjimce
				if (get_atrib_type(child[1].attrib["type"]) == 'type'):
					if (child[1].text == 'int'):
						try:
							int(inpt)
						except:
							result = 0
						else:
							result = inpt
					elif (child[1].text == 'string'):
						result = inpt
					elif (child[1].text == 'bool'):
						if inpt in ['true', 'false']:
							result = inpt
						else:
							result = 'false'
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['WRITE']):
			count_args(child, 1)
			typ = get_atrib_type(child[0].attrib["type"])
			if DEBUG:
				print(typ)
			values.append(control_get_value(child[0], typ, labels))
			if typ == "var":
				var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
				values[0] = get_var(values[0][3:], global_frame, local_frame, temp_frame)
				typ = var_type_control(values[0]);
			elif typ == 'int':
				is_int(values[0])
			elif typ == 'string':
				values[0] = is_string(values[0])
			elif typ == 'bool':
				values[0] = str(values[0]).lower()
				is_bool(values[0])
			else:
				values.append(control_get_value(child[0], typ, labels))
			values[0] = str(values[0])
			if values[0] == None:
				print("56: Chybějící hodnota.")
				sys.exit(56)
			print(values[0])

		elif(child.attrib["opcode"] in ['CONCAT']):
			count_args(child, 3)
			values.append(control_get_value(child[0], "var", labels))
			var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
			typ1 = get_atrib_type(child[1].attrib["type"])
			if typ1 == 'string' or typ1 == 'var':
				values.append(control_get_value(child[1], typ1, labels))
				if typ1 == 'var':
					var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
					values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
					values[1] = is_string(values[1])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			typ2 = get_atrib_type(child[2].attrib["type"])
			if typ2 == 'string' or typ2 == 'var':
				values.append(control_get_value(child[2], typ2, labels))
				if typ2 == 'var':
					var_control(values[2][:2], values[2][3:], global_frame, local_frame, temp_frame)
					values[2] = get_var(values[2][3:], global_frame, local_frame, temp_frame)
					values[2] = is_string(values[2])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			result = values[1] + values[2]
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['STRLEN']):
			count_args(child, 2)
			values.append(control_get_value(child[0], "var", labels))
			var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
			typ = get_atrib_type(child[1].attrib["type"])
			if typ == "string":
				values.append(control_get_value(child[1], "string", labels))
			elif typ == "var":
				values.append(control_get_value(child[1], "var", labels))
				var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
				values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
				typ = var_type_control(values[1]);
			if typ == 'string':
				values[1] = is_string(values[1])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			result = int(len(values[1]))
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['GETCHAR']):
			count_args(child, 3)
			values.append(control_get_value(child[0], "var", labels))
			var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
			typ1 = get_atrib_type(child[1].attrib["type"])
			if typ1 == 'string' or typ1 == 'var':
				values.append(control_get_value(child[1], typ1, labels))
				if typ1 == 'var':
					var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
					values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
					values[1] = is_string(values[1])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			typ2 = get_atrib_type(child[2].attrib["type"])
			if typ2 == 'int' or typ2 == 'var':
				values.append(control_get_value(child[2], typ2, labels))
				if typ2 == 'var':
					var_control(values[2][:2], values[2][3:], global_frame, local_frame, temp_frame)
					values[2] = get_var(values[2][3:], global_frame, local_frame, temp_frame)
					is_int(values[2])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			if(len(values[1]) <= values[2]):
				print("58: Index je mimo zadaný řetězec.")
				sys.exit(58)
			result = values[1][values[2]]
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['SETCHAR']):
			count_args(child, 3)
			values.append(control_get_value(child[0], "var", labels))
			var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
			result = get_var(values[0][3:], global_frame, local_frame, temp_frame)
			result = is_string(result)
			typ1 = get_atrib_type(child[1].attrib["type"])
			if typ1 == 'int' or typ1 == 'var':
				values.append(control_get_value(child[1], typ1, labels))
				if typ1 == 'var':
					var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
					values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
					is_int(values[1])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			typ2 = get_atrib_type(child[2].attrib["type"])
			if typ2 == 'string' or typ2 == 'var':
				values.append(control_get_value(child[2], typ2, labels))
				if typ2 == 'var':
					var_control(values[2][:2], values[2][3:], global_frame, local_frame, temp_frame)
					values[2] = get_var(values[2][3:], global_frame, local_frame, temp_frame)
					values[2] = is_string(values[2])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			if(len(values[0]) < values[1] or len(values[2]) == 0):
				print("58: Index je mimo zadaný řetězec./ Prázdný řetězec.")
				sys.exit(58)
			temp_list = list(result)
			temp_list[int(values[1])] = values[2][0]
			result = ''.join(temp_list)
			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['TYPE']):
			count_args(child, 2)
			values.append(control_get_value(child[0], "var", labels))
			var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
			typ = get_atrib_type(child[1].attrib["type"])
			if typ == 'int':
				result = typ
			elif typ == "var":
				values.append(control_get_value(child[1], typ, labels))
				var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
				values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
				if type(values[1]) == int:
					result = 'int'
				elif values[1] == 'true' or values[1] == 'false':
					result = 'bool'
				elif type(values[1]) == str:
					result = 'string'
				else:
					result = ''
			elif typ == 'bool':
				result = typ
			elif typ == 'string':
				result = typ

			set_val_to_var(values[0][:2], values[0][3:], result, global_frame, local_frame, temp_frame)

		elif(child.attrib["opcode"] in ['LABEL']):
			continue
		elif(child.attrib["opcode"] in ['JUMP']):
			count_args(child, 1)
			values.append(control_get_value(child[0], "label", labels))
			if values[0] not in labels:
				print("52: Neexistující návěští.")
				sys.exit(52)
			interpret(xmlroot[(labels[values[0]]):])
			break

		elif(child.attrib["opcode"] in ['JUMPIFEQ']):
			count_args(child, 3)
			values.append(control_get_value(child[0], "label", labels))
			if values[0] not in labels:
				print("52: Neexistující návěští.")
				sys.exit(52)

			typ1 = get_atrib_type(child[1].attrib["type"])
			typ2 = get_atrib_type(child[2].attrib["type"])
			if typ1 == 'int' or typ1 == 'string' or typ1 == 'bool' or typ1 == 'var':
				values.append(control_get_value(child[1], typ1, labels))
				if typ1 == 'var':
					var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
					values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
					typ1 = var_type_control(values[1]);
				if typ1 == 'int':
					is_int(values[1])
				elif typ1 == 'string':
					values[1] = is_string(values[1])
				elif typ1 == 'bool':
					values[1] = str(values[1]).lower()
					is_bool(values[1])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			if typ2 == 'int' or typ2 == 'string' or typ2 == 'bool' or typ2 == 'var':
				values.append(control_get_value(child[2], typ2, labels))
				if typ2 == 'var':
					var_control(values[2][:2], values[2][3:], global_frame, local_frame, temp_frame)
					values[2] = get_var(values[2][3:], global_frame, local_frame, temp_frame)
					typ2 = var_type_control(values[2]);
				if typ2 == 'int':
					is_int(values[2])
				elif typ2 == 'string':
					values[2] = is_string(values[2])
				elif typ2 == 'bool':
					values[2] = str(values[2]).lower()
					is_bool(values[2])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			if(typ1 != typ2):
				print("53: Typy operandů nejsou stejné.")
				sys.exit(53)
			if (values[1] == values[2]):
				interpret(xmlroot[(labels[values[0]]):])
				break

		elif(child.attrib["opcode"] in ['JUMPIFNEQ']):
			count_args(child, 3)
			values.append(control_get_value(child[0], "label", labels))
			if values[0] not in labels:
				print("52: Neexistující návěští.")
				sys.exit(52)

			typ1 = get_atrib_type(child[1].attrib["type"])
			typ2 = get_atrib_type(child[2].attrib["type"])
			if typ1 == 'int' or typ1 == 'string' or typ1 == 'bool' or typ1 == 'var':
				values.append(control_get_value(child[1], typ1, labels))
				if typ1 == 'var':
					var_control(values[1][:2], values[1][3:], global_frame, local_frame, temp_frame)
					values[1] = get_var(values[1][3:], global_frame, local_frame, temp_frame)
					typ1 = var_type_control(values[1]);
				if typ1 == 'int':
					is_int(values[1])
				elif typ1 == 'string':
					values[1] = is_string(values[1])
				elif typ1 == 'bool':
					values[1] = str(values[1]).lower()
					is_bool(values[1])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			if typ2 == 'int' or typ2 == 'string' or typ2 == 'bool' or typ2 == 'var':
				values.append(control_get_value(child[2], typ2, labels))
				if typ2 == 'var':
					var_control(values[2][:2], values[2][3:], global_frame, local_frame, temp_frame)
					values[2] = get_var(values[2][3:], global_frame, local_frame, temp_frame)
					typ2 = var_type_control(values[2]);
				if typ2 == 'int':
					is_int(values[2])
				elif typ2 == 'string':
					values[2] = is_string(values[2])
				elif typ2 == 'bool':
					values[2] = str(values[2]).lower()
					is_bool(values[2])
			else:
				print("53: Nesprávný typ operandu.")
				sys.exit(53)
			if(typ1 != typ2):
				print("53: Typy operandů nejsou stejné.")
				sys.exit(53)
			if (values[1] != values[2]):
				interpret(xmlroot[(labels[values[0]]):])
				break

		elif(child.attrib["opcode"] in ['DPRINT']):
			count_args(child, 1)
			typ = get_atrib_type(child[0].attrib["type"])
			if typ == "var":
				values.append(control_get_value(child[0], "var", labels))
				var_control(values[0][:2], values[0][3:], global_frame, local_frame, temp_frame)
				values[0] = get_var(values[0][3:], global_frame, local_frame, temp_frame)
			else:
				values.append(control_get_value(child[0], typ, labels))
			values[0] = str(values[0]) + '\n'
			sys.stderr.write(values[0])

		elif(child.attrib["opcode"] in ['BREAK']):
			count_args(child, 0)
			print("* * * STATE of INTERPRET: * * *")
			print("Pozice:", instr_total)
			print("Instrukce (vykonáno):", instr_total-1)
			print("Instrukce (celkem):", len(root))
			print("*Obsah rámců:*")
			print("GF [jméno: hodnota]:", global_frame)
			print("LF:", local_frame)
			print("TF:", temp_frame)
			print("Zásobník:", stack)
			print("Návěští [jméno: pozice]:", labels)

		else:
			print("32: Neznámá instrukce.")
			sys.exit(32)
		if DEBUG:
			print("#-#-#-#-#-#-#-#-#-#-#")
			print("#-# DEBUG OUTPUT #-#")
			print("GF:", global_frame)
			print("LF:", local_frame)
			print("TF:", temp_frame)
			print("frame stack:", frame_stack)
			print("stack:", stack)
			print("labels:", labels)
			print("order:", order-1)
			print("instrukce:", child.attrib["order"])
			print("root:", len(root))
			print("#-#-#-#-#-#-#-#-#-#-#")

operation = ['MOVE',
              'CREATEFRAME',
              'PUSHFRAME',
              'POPFRAME',
              'DEFVAR',
              'CALL',
              'RETURN',
              'PUSHS',
              'POPS',
              'ADD',
              'SUB',
              'MUL',
              'IDIV',
              'LT',
              'GT',
              'EQ',
              'AND',
              'OR',
              'NOT',
              'INT2CHAR',
              'STRI2INT',
              'READ',
              'WRITE',
              'CONCAT',
              'STRLEN',
              'GETCHAR',
              'SETCHAR',
              'TYPE',
              'LABEL',
              'JUMP',
              'JUMPIFEQ',
              'JUMPIFNEQ',
              'DPRINT',
              'BREAK'
              ];

types = ['var',
	     'int',
	     'type',
	     'bool',
	     'string',
	     'label'
      	];
def count_args(args, count):
	if(len(args) != count):
		print("31: Špatný počet argumentů u instrukce.")
		sys.exit(31)

def parsing_script_arguments(argv):
	outputfile = ''
	try:
		opts, args = getopt.getopt(sys.argv[1:],"",["help","source="])
	except getopt.GetoptError:
		print("10: Špatně zadané argumenty skriptu.")
		sys.exit(10)
	for opt, arg in opts:
		if (opt == "--help" and len(opts) == 1):
			print("Nápověda:")
			print("Skript interpret.py, verze python3.6")
			print("Spuštění: python3.6 interpret.py [--source=file | --help]")
			print("--help vypíše nápovědu")
			print("file určuje vstupní XML soubor")
			sys.exit(0)
		elif opt == "--source":
			outputfile = arg
			return outputfile
		else:
			print("10: Špatně zadané argumenty skriptu.")
			sys.exit(10)

if __name__ == "__main__":
	instr_total = 0
	local_frame = None
	temp_frame = None
	stack = []
	frame_stack = []
	call_stack = []
	order = 1
	labels = {}
	global_frame = {}
	outputfile = parsing_script_arguments(sys.argv[1:])
	file = open(outputfile,'r')
	xmlroot = load_data(outputfile)
	check_header(xmlroot)
	for child2 in xmlroot:
		if(child2.attrib["opcode"] in ['LABEL']):
			count_args(child2, 1)
			if child2[0].text in labels:
				print("52: Redefinice návěští.")
				sys.exit(52)
			labels[child2[0].text] = int(child2.attrib["order"])
	interpret(xmlroot)
