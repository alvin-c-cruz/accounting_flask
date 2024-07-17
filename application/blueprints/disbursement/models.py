from application.extensions import db, short_date, Url
from . import app_name, model_name


class Disbursement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.String())

    cash_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    cash = db.relationship('Account', backref='disbursements', lazy=True)

    disbursement_number = db.Column(db.String())
    check_number = db.Column(db.String())

    check_name_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    check_name = db.relationship('Vendor', backref='disbursements', lazy=True)

    submitted = db.Column(db.String())
    cancelled = db.Column(db.String())

    def __str__(self):
        return getattr(self, f"{app_name}_number")

    @property
    def preparer(self):
        obj = UserDisbursement.query.filter(getattr(UserDisbursement, f"{app_name}_id")==self.id).first()
        return obj

    @property
    def formatted_record_date(self):
        return short_date(self.record_date) if self.record_date else None

    @property
    def formatted_submitted(self):
        return short_date(self.submitted) if self.submitted else None

    @property
    def formatted_cancelled(self):
        return short_date(self.cancelled) if self.cancelled else None
    
    def is_submitted(self):
        return True if self.submitted else False

    @property
    def url(self):
        return Url(self)
    
    @property
    def amount(self):
        return "Coming soon"
    
    @property
    def formatted_amount(self):
        return "Coming soon"
    

class DisbursementDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    disbursement_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), nullable=False)
    disbursement = db.relationship(model_name, backref=f'{app_name}_details', lazy=True)

    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    vendor = db.relationship('Vendor', backref=f'{app_name}_details', lazy=True)

    reference = db.Column(db.String())
    not_applicable = db.Column(db.Float, default=0)
    exempted = db.Column(db.Float, default=0)
    zero_rated = db.Column(db.Float, default=0)
    vat_registered = db.Column(db.Float, default=0)

    vat_id = db.Column(db.Integer, db.ForeignKey(f'vat.id'), nullable=False)
    vat = db.relationship('Vat', backref=f'{app_name}_details', lazy=True)

    wtax_id = db.Column(db.Integer, db.ForeignKey(f'wtax.id'), nullable=False)
    wtax = db.relationship('Wtax', backref=f'{app_name}_details', lazy=True)

    account_id = db.Column(db.Integer, db.ForeignKey(f'account.id'), nullable=False)
    account = db.relationship('Account', backref=f'{app_name}_details', lazy=True)

    particulars = db.Column(db.String())


class UserDisbursement(db.Model):
    disbursement_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    disbursement = db.relationship(model_name, backref='user_prepare', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_prepared', lazy=True)

    def __str__(self):
        return self.user.user_name

    def __repr__(self):
        return self.user.user_name


class AdminDisbursement(db.Model):
    disbursement_id = db.Column(db.Integer, db.ForeignKey(f'{app_name}.id'), primary_key=True)
    disbursement = db.relationship(model_name, backref='user_approved', lazy=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User', backref=f'{app_name}_approved', lazy=True)
