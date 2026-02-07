print(" Student Marks Manager")

name = input("Enter student name: ")

m1 = int(input("Enter Math marks: "))
m2 = int(input("Enter Science marks: "))
m3 = int(input("Enter English marks: "))

total = m1 + m2 + m3
average = total / 3

print("\n Result")
print("----------")
print("Name:", name)
print("Total:", total)
print("Average:", average)

if average >= 90:
    print("Grade: A+ ")
elif average >= 80:
    print("Grade: A ")
elif average >= 70:
    print("Grade: B ")
elif average >= 60:
    print("Grade: C ")
else:
    print("Grade: F ")
