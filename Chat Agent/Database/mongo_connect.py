from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["amitabh_info"]
biography = db["biography"]

# Fetch the big paragraph
bio_doc = biography.find_one()
bio_text = bio_doc["bio"]

print("📖 Bio Loaded:\n")
print(bio_text)

# Simple Q&A with keyword search
def answer_question(question):
    q = question.lower()
    if "first movie" in q:
        return "His first movie was Saat Hindustani (1969)."
    elif "popular movie" in q:
        return "His most popular and career-defining film is Sholay (1975)."
    elif "where" in q and "live" in q:
        return "He currently lives in Mumbai, India at his bungalow 'Jalsa'."
    elif "awards" in q:
        return "He has won Padma Shri (1984), Padma Bhushan (2001), Padma Vibhushan (2015), and many film awards."
    elif "tv" in q or "kaun banega crorepati" in q:
        return "He has hosted 'Kaun Banega Crorepati' since 2000."
    elif "family" in q:
        return "He is married to Jaya Bhaduri and has two children, Abhishek Bachchan and Shweta Bachchan."
    else:
        return "Sorry, I couldn’t find the answer in the bio."

# Example Questions
print("\nQ: Where does Amitabh Bachchan live?")
print("A:", answer_question("Where does Amitabh Bachchan live?"))

print("\nQ: What is his first movie?")
print("A:", answer_question("What is his first movie?"))

print("\nQ: Which awards has he won?")
print("A:", answer_question("Which awards has he won?"))
