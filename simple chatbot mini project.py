print("Mini Chatbot")

name = input("Bot: Hi! What's your name? ")

print("Bot: Nice to meet you,",name)
print("Bot: You can chat with me now. Type 'bye' to exit.")

while True:
    msg = input("You: ").lower()   # convert to lowercase

    if msg == "bye":
        print("Bot: Bye", name, " Take care ")
        break

    elif "how are you" in msg:
        print("Bot: I'm doing great. Thanks for asking!")
