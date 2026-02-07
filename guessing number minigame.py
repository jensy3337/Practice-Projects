import random

secret = random.randint(1,20)

print("Guess The Number Game")
print("I'm thinking of a number between 1 and 20...")

guess = 0
attempts = 0 #counts tries

while guess != secret:
    guess = int(input("enter your guess:"))
    attempts += 1  #add 1 try
  
    if guess > secret:
      print("too high")
    elif guess < secret:
      print("too low")
    else:
      print("correct")
      print("tries time:",attempts)
