from application.extensions import db
from . import app_name, model_name


class Vat(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    vat_name = db.Column(db.String(255))
    active = db.Column(db.Boolean())

    def __str__(self):
        return getattr(self, f"{app_name}_name")
    
    def options(self):
        _options = [{"id": record.id, "dropdown_name": getattr(record, f"{app_name}_name")} for record in self.query.order_by(f"{app_name}_name").all() if record.active]
        return _options

    @property
    def preparer(self):
        user_prepare = UserVat.query.filter(getattr(UserVat, f"{app_name}_id")==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminVat.query.filter(getattr(AdminVat, f"{app_name}_id")==self.id).first()
        return admin_approve


class UserVat(db.Model):
    vat_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    vat = db.relationship(model_name, backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminVat(db.Model):
    vat_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    vat = db.relationship(model_name, backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_approved', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name
