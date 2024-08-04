from sqlalchemy import func
from .models import Account as Obj
from my_form import MyForm


class Form(MyForm):
    def validate_on_submit(self):
        self.errors = {}

        if not self.account_number:
            self.errors["account_number"] = "Please type account number."
        else:
            existing_ = Obj.query.filter(func.lower(Obj.account_number) == func.lower(self.account_number), Obj.id != self.id).first()
            if existing_:
                self.errors["account_number"] = "Account number already exists."

        if not self.account_name:
            self.errors["account_name"] = "Please type account title."
        else:
            existing_ = Obj.query.filter(func.lower(Obj.account_name) == func.lower(self.account_name), Obj.id != self.id).first()
            if existing_:
                self.errors["account_name"] = "Account title already exists."

        if not self.errors:
            return True
        else:
            return False    
