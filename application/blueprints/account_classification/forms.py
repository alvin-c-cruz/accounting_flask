from sqlalchemy import func
from .models import AccountClassification as Obj
from my_form import MyForm


class Form(MyForm):
    def validate_on_submit(self):
        self.errors = {}

        if not self.account_classification_name:
            self.errors["account_classification_name"] = "Please type account classification."
        else:
            existing_ = Obj.query.filter(func.lower(Obj.account_classification_name) == func.lower(self.account_classification_name), Obj.id != self.id).first()
            if existing_:
                self.errors["account_classification_name"] = "Account Classification already exists."

        if not self.priority:
            self.errors["priority"] = "Please type priority."

        if not self.errors:
            return True
        else:
            return False    
