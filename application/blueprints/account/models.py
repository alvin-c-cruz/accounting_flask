from application.extensions import db
from . import app_name, model_name


class Account(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    account_number = db.Column(db.String(255))
    account_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return f"{record.account_number}: {record.account_name}"
    
    def options(self):
        _options = [
            {"id": record.id, "dropdown_name": f"{record.account_number}: {record.account_name}"} 
            for record in self.query.order_by(f"{app_name}_name").all() 
            if record.active
            ]
        return _options

    @property
    def preparer(self):
        user_prepare = UserAccount.query.filter(getattr(UserAccount, f"{app_name}_id")==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminAccount.query.filter(getattr(AdminAccount, f"{app_name}_id")==self.id).first()
        return admin_approve


class UserAccount(db.Model):
    account_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    account = db.relationship(model_name, backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminAccount(db.Model):
    account_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    account = db.relationship(model_name, backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_approved', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name
