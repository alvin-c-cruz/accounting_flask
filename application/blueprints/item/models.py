from application.extensions import db
from . import app_name, model_name


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    item_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return getattr(self, f"{app_name}_name")
    
    def options(self):
        _options = [{"id": record.id, "dropdown_name": getattr(record, f"{app_name}_name")} for record in self.query.order_by(f"{app_name}_name").all() if record.active]
        return _options

    @property
    def preparer(self):
        user_prepare = UserItem.query.filter(getattr(UserItem, f"{app_name}_id")==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminItem.query.filter(getattr(AdminItem, f"{app_name}_id")==self.id).first()
        return admin_approve


class UserItem(db.Model):
    item_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    item = db.relationship(model_name, backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminItem(db.Model):
    item_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    item = db.relationship(model_name, backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_approved', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name
