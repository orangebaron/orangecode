#runs ./resources/main.orng
from orange_code import orange_code
import sys
file = open(sys.path[0]+'/resources/main.orng','r')
orange_code().runCode(file.read())
file.close()
