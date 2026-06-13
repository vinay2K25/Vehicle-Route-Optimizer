import csv
with open('depot.csv') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row[0])
        print(type(row[0]))