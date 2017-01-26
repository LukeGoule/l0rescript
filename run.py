import random, sys, os

debugging = False
linux     = True
file      = ""

argc = len(sys.argv)
if (argc > 1):
	for arg in sys.argv:
		if (arg.split("=")[0] == "--dbg"):
			if (arg.split("=")[1] == "on"):
				debugging = True
			elif (arg.split("=")[1] == "off"):
				debugging = False
		elif (arg.split("=")[0] == "--linux"):
			if (arg.split("=")[1] == "on"):
				linux = True
			elif (arg.split("=")[1] == "off"):
				linux = False
		elif (arg.split("=")[0] == "--f"):
			try:
				file = arg.split("=")[1];
				try:
					with open("scripts/"+file, "r") as f____:
						f____.close()
				except:
					print("File doesn't exist!")
					quit()
			except:
				print("Arg --f set wrong")
				quit()

info_char = '@'
comment_char = '#'
variables = []
routines = []

var_a = 'v'
var_b = 'i'

pr_syn = "Unrecognised syntax"
pr_vsyn = "Unrecognised variable syntax"
pr_visyni = "Not integer value"
pr_print = "Failed to scan string"
pr_routine = "Bad routine syntax"

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def dprint(s, m=OKBLUE):
	if (debugging):
		print("DBG >>> " + m + s + ENDC)

def Ran():
	return random.randint(0,10000)

def FGet(fl):
	with open("scripts/"+fl, "r") as f:
		return f.readlines();

def IsInt(i):
	try:
		int(i)
		return True
	except:
		return False

def GetStr(l):
	s_t = 0
	s_s = False
	s_o = ""
	global variables

	for c in l:
		if c == '"':
			if (s_t == 0):
				s_s = True
				continue
			elif (s_t > 0):
				break;
		elif s_s:
			if (s_t == len(l)):
				if (not c == '"'):
					s_o = "<BAD_LITERAL_ENDING>"
					break;

			s_o += c
			s_t += 1
		else:
			continue
		
		dprint("GetStr( ) c=%s;ss=%s;so=%s" % (c,str(s_s),s_o))
	
	if (not s_o == ""):
		#variable search
		out = s_o
		for obj in variables:
			f = "&v:" + obj[0]
			dprint("fn " + f)
			dprint("fv " + "&v:" + str(obj[1]))
			out = out.replace(f, str(obj[1]))

		return out
	else:
		return "<INVALID>"

def GetStrAB(l, ch, ch2):
	s_t = 0
	s_s = False
	s_o = ""
	global variables

	for c in l:
		if c == ch or c == ch2:
			if (s_t == 0):
				s_s = True
				continue
			elif (s_t > 0):
				break;
		elif s_s:
			if (s_t == len(l)):
				if (not c == ch or not c == ch2):
					s_o = "<BAD_LITERAL_ENDING>"
					break;

			s_o += c
			s_t += 1
		else:
			continue
		
		dprint("GetStr( ) c=%s;ss=%s;so=%s" % (c,str(s_s),s_o))
	
	if (not s_o == ""):
		out = s_o
		return out
	else:
		return "<INVALID>"

def GetIntVar(l):
	v_s = l.split(" ")
	v_n = ""
	v_v = 0
	global variables
	try:
		if (v_s[0] == "vi"):
			try:
				tsplit = v_s[1].split("=")
				v_n = tsplit[0]
				v_v = tsplit[1]
			except:
				return "<INVALID>"
		else:
			return "<INVALID>"
	except:
		return "<INVALID>"
	finally:
		variables += [[v_n, int(v_v.replace("\n", ""))]]
		return v_n + "::" + v_v

def BuildRoutine(l):
	route_out = ""
	route_name = ""
	route_func = ""

	global variables
	
	if not l.split(" ")[0] == "route": #should never be true
		route_out = "<NOT_ROUTINE>"
		return route_out

	if not len(l.split(" ")) > 2:
		route_out = "<INVALID_R_SYNTAX>"
		return route_out

	temp = GetStrAB(l, "(", ")")
	if (temp == "<BAD_LITERAL_ENDING>" or temp == "<INVALID>"):
		route_out = "<INVALID_R_SYNTAX>"
		return route_out
	else:
		route_name = l.split(" ")[1]
		route_func = temp
		route_out = route_name + "::" + route_func
		return route_out

def CallRoutine(l):
	global routines

	gs = GetStrAB(l, "(", ")")

	for r in routines:
		if (gs == r[0]):
			Parse([r[1]])

def FindArgs(l):
	args_out = []

	global variables
	args_out = GetStrAB(l, "(", ")").split(",")
	for arg in args_out:
		arg = arg.replace(" ", "")

	return args_out # eg generic_routine("abc", "def") -> ["abc", "def"]


def Parse(filedata):

	sname = "nullname"
	script = filedata
	linen = 0
	problem = ""
	rand = Ran()
	global routines

	for line in script:
		linen += 1
		rand = Ran()

		line = line.replace("&r", str(random.randint(0,10000)))
		line = line.replace("&n", str(sname))
		line = line.replace("&r", str(FAIL))
		line = line.replace("&g", str(OKBLUE))
		line = line.replace("&b", str(OKGREEN))
		line = line.replace("&e", str(ENDC))
		line = line.replace("&linux", str(linux))
		line = line.replace("&dbg", str(debugging))

		sp_split = line.split(" ")

		dprint("Parsing: " + line)
		if line[0] == info_char:
			print("Info: " + line[1:].replace("\n", ""))
			continue
		elif line[0] == comment_char:
			print("Comment: " + line[1:].replace("\n", ""))
			continue
		elif line.split(" ")[0] == "vi": #varint declaration start
			temp = GetIntVar(line)
			if (not temp == "<INVALID>"):
				dprint("stored var int " + temp.split("::")[0] + " = " + temp.split("::")[1])
			else:
				dprint("could not store variable ", FAIL)
				problem = pr_vsyn
		elif sp_split[0] == "print":
			temp = GetStr(line)
			if (temp != "<INVALID>"):
				print(temp)
			elif (temp == "<BAD_LITERAL_ENDING>"):
				problem = pr_print
				break;
			else:
				problem = pr_print
				break;
		elif sp_split[0] == "route":
			br = BuildRoutine(line);
			if not br == "<NOT_ROUTINE>" or not br == "<INVALID_R_SYTAX>":
				routines += [[br.split("::")[0], br.split("::")[1]]]
			else:
				problem = pr_routine
				break;
		elif sp_split[0] == "call":
			CallRoutine(line)
		else:
			problem = pr_syn
			break

		for obj in routines:
			#print(obj)
			pass

		for obj in variables:
			#dprint("[\"" + obj[0] + "\", " + str(str(obj[1])) + "]")
			pass

	if (problem != ""):
		print("%sProblem: line=%s;problem=%s%s" % (FAIL, linen, problem, ENDC))
		sys.exit();




if __name__ == "__main__":
	if (not linux):
		HEADER = ""
		OKBLUE = ""
		OKGREEN = ""
		WARNING = ""
		FAIL = ""
		ENDC = ""
		BOLD = ""
		UNDERLINE = ""

	if (file == ""):
		script = FGet("test.lre")
	else:
		script = FGet(file)
	Parse(script)
