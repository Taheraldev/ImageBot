import os

# Function to declare the private Secret environment variables
def declare_vars():
    # GOOGLE_APPLICATION_CREDENTIALS
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/path/to/my/credetials.json"
    # TB_TOKEN
    os.environ["TB_TOKEN"]="my:telegram-token"
