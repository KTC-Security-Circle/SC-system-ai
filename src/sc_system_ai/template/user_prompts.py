from sc_system_ai.template.prompts import user_info_template


class User():
    """
    ### User class
    
    Args:
        name (str): user's name
        major (str): user's major
    """
    def __init__(self, name, major):
        self.name = name
        self.major = major

    def __str__(self):
        return f"name: {self.name}, major: {self.major},"



class UserPrompt():
    def __init__(self, user_args: User = None):
        self.user_args = user_args
        if user_args is not None:
            self.user_prompt = self._format()

    def __str__(self):
        if self.user_args is not None:
            return self.user_prompt
        else:
            return "No user args. Please format user args."
    
    def _format(self):
        return user_info_template.format(name=self.user_args.name, major=self.user_args.major)

    def format(self, user_args: User):
        self.user_args = user_args
        self.user_prompt = self._format()




if __name__ == "__main__":
    user = User("yuki", "スーパーAIクリエイター専攻")
    print(user)
    user_prompt = UserPrompt(user)
    # user_prompt.format(user)
    print(user_prompt)