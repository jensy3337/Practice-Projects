fruits = ["orange","chikkoo","custard apple","mango","guava"]


# display all fruits list
print("Fruit Analyzer\n")
print("All Fruits:")
for i in fruits:
  print(">",i)


# to count total number of fruits
# total = 0
# for i in fruits:
#   total +=1
# print("\nTotal Fruits:",total)

# OR
total=len(fruits)
print("\nTotal Fruits:",total)


# count fruits with long names
long_count = 0
for i in fruits:
  if len(i)>5:
    long_count +=1
print("\nFruits with long names =",long_count)


# fruits name with a 
print("\nFruits with letter 'a':")
for i in fruits:
  if "a" in i:
    print("-",i)
