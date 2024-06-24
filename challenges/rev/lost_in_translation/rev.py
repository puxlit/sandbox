awaflag = open("awawa.txt", "r").read()
flag = open("flag.txt", "w")

# copied from src.py
lookup = "AWawJELYHOSIUMjelyhosiumPCNTpcntBDFGRbdfgr0123456789 .,!'()~_/;\n"

assert awaflag.startswith("awa")
awaflag = awaflag[3:].replace(" awa", "0").replace("wa", "1")
assert len(awaflag) % 8 == 0

output = ""

for i in range(0, len(awaflag), 8):
    output += lookup[int(awaflag[i:i + 8], 2)]

flag.write(output)
