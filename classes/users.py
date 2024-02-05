from classes.connector import Database

class AuthenticatorConfigurator:
    def __init__(self):
        self.db = Database()

    def fetch_user_data(self):
        query = "SELECT \"Username\", \"Name\", \"Email\", \"Password\" FROM public.\"user\""
        fetched_data = self.db.get_request(query)

        user_credentials = {'usernames': {}}
        for user in fetched_data:
            username, name, email, password = user
            cleaned_password = password.replace("{", "").replace("}", "")
            user_credentials['usernames'][username] = {
                'name': name,
                'email': email,
                'password': cleaned_password
            }

        return user_credentials