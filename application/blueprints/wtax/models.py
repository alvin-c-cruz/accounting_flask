from application.extensions import db
from . import app_name, model_name


class Wtax(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    wtax_name = db.Column(db.String(255))
    atc = db.Column(db.String(255))
    tax_rate = db.Column(db.Float())

    wtax_type_id = db.Column(db.Integer, db.ForeignKey('wtax_type.id'), nullable=False)
    wtax_type = db.relationship('WtaxType', backref='wtaxes', lazy=True)

    active = db.Column(db.Boolean())

    def __str__(self):
        return getattr(self, f"{app_name}_name")
    
    def options(self):
        _options = [{"id": record.id, "dropdown_name": getattr(record, f"{app_name}_name")} for record in self.query.order_by(f"{app_name}_name").all() if record.active]
        return _options

    @property
    def preparer(self):
        user_prepare = UserWtax.query.filter(getattr(UserWtax, f"{app_name}_id")==self.id).first()
        return user_prepare
    
    @property
    def approved(self):
        admin_approve = AdminWtax.query.filter(getattr(AdminWtax, f"{app_name}_id")==self.id).first()
        return admin_approve


class UserWtax(db.Model):
    wtax_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    wtax = db.relationship(model_name, backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminWtax(db.Model):
    wtax_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    wtax = db.relationship(model_name, backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_approved', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name
