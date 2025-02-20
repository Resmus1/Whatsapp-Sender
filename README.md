# Whatsapp Sender 🚀

## 📌 Description
Whatsapp message sender.
Sender WakeUp pics.
Choice picture and send yor contacts in Whatsapp

## 🔧 Work
Ver. 1.0 Status(Work)
Create stable version and add settings for start script.

## 🔧 Start Script
1. Add Chrome profile authorize in Whatsapp in chrome_profile.
2. Add your numbers in phone_numbers.txt.

```bash
# Clone the repository
git clone https://github.com/Resmus1/Whatsapp-Sender
cd Whatsapp-Sender

# Install dependencies
pip install -r requirements.txt

# Create an empty "logs" directory (if it doesn't exist)
mkdir -p chrome_profile/"User Data"

# Create a phone_numbers.txt file with example numbers
echo -e "9059454545\n9410449789\n7097895443" > phone_numbers.txt


# Run the script
python main.py whatsapp.py