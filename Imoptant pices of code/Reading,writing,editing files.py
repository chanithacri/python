# Read(recomended way)
with open("example_file.txt", "r") as f:
    a = f.readlines()  #list[str]
    b = f.read()  #str


# Write(recomended way)
with open("example file.txt", "w") as f:
    f.write("infomation......"). #str
    f.writelines(["line 1", "line 2", "line n"])  #list[str]


# Add text without erasing previous info(recomended)
with open("example_file.txt", "a") as f:
    f.write("info")
    f.writelines(["line 1", "line 2", "line n"])  # list[str]

