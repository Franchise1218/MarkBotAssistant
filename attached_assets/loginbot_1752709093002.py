import os

# 🔐 Set path to your credentials file
CRED_FILE = "/Users/josemarrero/Desktop/Cloud Log Ins/Passwords.txt"

def load_credentials():
    creds = {}
    if not os.path.exists(CRED_FILE):
        print(f"🛑 Credential file not found: {CRED_FILE}")
        return creds

    with open(CRED_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 3:
                cloud, email, password = parts
                creds[cloud.lower()] = (email.strip(), password.strip())
    return creds

def get_login(cloud_name):
    cloud_name = cloud_name.lower().strip()
    creds = load_credentials()
    if cloud_name in creds:
        email, password = creds[cloud_name]
        return f"📦 {cloud_name.upper()}\nEmail: {email}\nPassword: {password}"
    else:
        return f"🛑 No login info found for '{cloud_name}'"

def list_clouds_starting(prefix, limit=10):
    """Returns a list of cloud aliases that start with a given prefix."""
    matches = []
    if not os.path.exists(CRED_FILE):
        print(f"🛑 Credential file not found: {CRED_FILE}")
        return matches

    with open(CRED_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 3:
                cloud = parts[0].strip()
                if cloud.lower().startswith(prefix.lower()):
                    matches.append(cloud)
    return matches[:limit]

# 🔧 Manual testing interface
if __name__ == "__main__":
    while True:
        query = input("🔍 Enter cloud alias or prefix: ").strip()
        if query.lower() in ["exit", "quit"]:
            break
        elif query.lower().startswith("prefix:"):
            prefix = query[7:].strip()
            clouds = list_clouds_starting(prefix)
            if clouds:
                print(f"\n📦 Clouds matching '{prefix}':\n• " + "\n• ".join(clouds))
            else:
                print(f"\n🛑 No clouds found starting with '{prefix}'.")
        else:
            print(get_login(query))
