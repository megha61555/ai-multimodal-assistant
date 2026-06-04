user_data = {}

def save_user_name(name):

    user_data["name"] = name

def get_user_name():

    return user_data.get("name")