from flask_login import current_user

class UsersPolicy:
    def __init__(self, record):
        self.record = record

    def delete_book(self):
        return current_user.is_admin()

    def create_book(self):
        return current_user.is_admin()

    def edit_book(self):
        return current_user.is_admin() or current_user.is_moder()
    
