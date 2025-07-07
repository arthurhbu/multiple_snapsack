file_new_column = open('tetstehdsahiodsa.txt', 'r')

file_instancia = open('pedaco_instancia5.txt', 'r')

file = open('kdsakdsa.txt', 'w')

for line in file_instancia:
    last_value = file_new_column.readline()
    line = line.split()
    file.write(line[0] + ' ' + line[1] + ' ' + last_value)

file_new_column.close()

file_instancia.close()

