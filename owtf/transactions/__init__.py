import re


# The regex find differs for these types :P
REGEX_TYPES = ['HEADERS', 'BODY']

regexs = defaultdict(list)
for regex_type in REGEX_TYPES:
    regexs[regex_type] = {}
compile_regex()
