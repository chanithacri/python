a = []
with open("file1.txt", "r") as f:
    for i in range(2):
        a.append(f.readline())
    with open("file2.txt", "w") as n:
        for i in a:
            n.write(i)

with open("file2.txt", "r") as d:
    z = d.read()
    print(z)
