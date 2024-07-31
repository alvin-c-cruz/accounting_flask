from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import Disbursement as Obj
from .models import DisbursementDetail as ObjDetail
from .models import UserDisbursement as Preparer
from datetime import datetime
from werkzeug.utils import secure_filename
from pathlib import Path
from flask import current_app

from . import app_name

HEADER_INTEGER_FIELDS = ["cash_id", "check_name_id"]
HEADER_FLOAT_FIELDS = []

DETAIL_INTEGER_FIELDS = ["vendor_id", "vat_id", "wtax_id", "account_id"]
DETAIL_FLOAT_FIELDS = ["not_applicable", "exempted", "zero_rated", "vat_registered"]

DETAIL_ROWS = 10


def get_attributes(object):
    attributes = [x for x in dir(object) if (not x.startswith("_"))]
    exceptions = (
        "user_prepare_id", 
        "user_prepare", 
        "errors", 
        "active", 
        "details", 
        "files",
        )
    for i in exceptions:
        try:
            attributes.remove(i)
        except ValueError:
            pass
    return attributes


def get_attributes_as_dict(object):
    attributes = get_attributes(object)
    return {
        attribute: getattr(object, attribute)
        for attribute in attributes
    }


@dataclass
class SubForm:
    id: int = 0
    vendor_id:int = 0
    reference: str = ""
    not_applicable: float = 0
    exempted: float = 0
    zero_rated: float = 0
    vat_registered: float = 0
    vat_id: int = 0
    wtax_id: int = 0
    account_id: int = 0
    particulars: str = ""

    errors = {}

    def _populate(self, row):
        for attribute in get_attributes(self):
            setattr(self, attribute, getattr(row, attribute))

    def _validate(self):
        self.errors = {}

        if self._is_dirty():            
            if not self.vendor_id:
                self.errors["vendor_id"] = "Please select vendor."

            if not self.account_id:
                self.errors["account_id"] = "Please select account."
                                
        if not self.errors:
            return True
        else:
            return False    

    def _is_dirty(self):
        _attributes = [
            self.vendor_id,
            self.reference,
            self.not_applicable,
            self.exempted,
            self.zero_rated,
            self.vat_registered,
            self.vat_id,
            self.wtax_id,
            self.account_id,
            self.particulars,
        ]

        return any(_attributes)    

        

@dataclass
class Form:
    id: int = None
    record_date: str = ""
    cash_id: int = 0
    disbursement_number: str = ""
    check_number: str = ""
    check_name_id: int = 0
    submitted: str = ""
    cancelled: str = ""

    user_prepare_id: int = None

    details = []
    errors = {}
    files = []

    def __post_init__(self):
        self.details = []
        for i in range(DETAIL_ROWS):
            self.details.append((i, SubForm()))

    def _save(self, submitted=None):
        if self.id is None:
            # Add a new record
            _dict = {}
            for i in get_attributes(self): _dict[i] = getattr(self, i)
            _dict.pop("id")
            
            new_record = Obj(
                **_dict
                )
            db.session.add(new_record)
            db.session.commit()

            self.id = new_record.id

            for _, detail in self.details:
                if detail._is_dirty():
                    _dict = get_attributes_as_dict(detail)
                    _dict.pop("id")
                    new_detail = ObjDetail(**_dict)
                    setattr(new_detail, f"{app_name}_id", new_record.id)
                    db.session.add(new_detail)
                    db.session.commit()
            
            preparer = Preparer(**{f"{app_name}_id": new_record.id})
            preparer.user_id=self.user_prepare_id

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get(self.id)
            if record:
                preparer = Preparer.query.filter_by(**{f"{app_name}_id": self.id}).first()
                preparer.user_id = self.user_prepare_id

                for attribute in get_attributes(self):
                    if attribute == "id": continue
                    setattr(record, attribute, getattr(self, attribute))
                                
                details = ObjDetail.query.filter(
                    getattr(ObjDetail, f"{app_name}_id")==self.id
                    )
                
                for detail in details:
                    db.session.delete(detail)

                for i, detail in self.details:
                    if detail._is_dirty():
                        _dict = {
                            attribute: getattr(detail, attribute)
                            for attribute in get_attributes(SubForm)
                        }

                        _dict[f"{app_name}_id"] = record.id
                        row_detail = ObjDetail(**_dict)
                        db.session.add(row_detail)
                
        db.session.commit()
        
        #  Iterate thru files
        for file in self.files:
            if file:
                filename = secure_filename(file.filename)
                root = Path(current_app.instance_path)
                
                upload_path = root / "uploads"
                if not upload_path.is_dir():  upload_path.mkdir()
                
                disbursements_path = upload_path / "disbursements"
                if not disbursements_path.is_dir():  disbursements_path.mkdir()
                
                voucher_path = disbursements_path / self.disbursement_number
                if not voucher_path.is_dir():  voucher_path.mkdir()

                file.save(voucher_path / filename)
            else:
                if "files" not in self.errors: self.errors["files"] = []
                self.errors["files"].append(f"{filename} is not a valid file.")

   
    def _populate(self, obj):
        for attribute in get_attributes(self):
            setattr(self, attribute, getattr(obj, attribute))

        for i, row in enumerate(getattr(obj, f"{app_name}_details")):
            subform = SubForm()
            subform._populate(row)
            self.details[i] = (i, subform)

        root = Path(current_app.instance_path)
                
        upload_path = root / "uploads"
        if not upload_path.is_dir():  upload_path.mkdir()
                
        disbursements_path = upload_path / "disbursements"
        if not disbursements_path.is_dir():  disbursements_path.mkdir()
                
        voucher_path = disbursements_path / self.disbursement_number
        if not voucher_path.is_dir():  voucher_path.mkdir()

                    
        

    def _post(self, request_form):
        for attribute in get_attributes(self):
            if attribute == "id":
                value = getattr(request_form, "get")(f"record_id")
                if value:
                    setattr(self, "id", int(value))
            elif attribute in HEADER_INTEGER_FIELDS:
                setattr(self, attribute, int(getattr(request_form, "get")(attribute)))
            elif attribute in HEADER_FLOAT_FIELDS:
                setattr(self, attribute, float(getattr(request_form, "get")(attribute)))
            else:
                setattr(self, attribute, getattr(request_form, "get")(attribute))

        for i in range(DETAIL_ROWS):
            for attribute in get_attributes(SubForm):
                if attribute in DETAIL_FLOAT_FIELDS:
                    setattr(self.details[i][1], attribute, float(request_form.get(f'{attribute}-{i}')))
                elif attribute in DETAIL_INTEGER_FIELDS:
                    setattr(self.details[i][1], attribute, int(request_form.get(f'{attribute}-{i}')))
                else:
                    setattr(self.details[i][1], attribute, request_form.get(f'{attribute}-{i}'))

    def _post_files(self, files):
        if not files or files[0].filename == '':
            # No selected files
            return
        
        self.files = files
    
    def _validate_on_submit(self):
        self.errors = {}
        detail_validation = True

        if not self.record_date:
            self.errors["record_date"] = "Please type date."

        if not self.cash_id:
            self.errors["cash_id"] = "Please select cash account."

        if not self.disbursement_number:
            self.errors["disbursement_number"] = "Please type cd number."
        else:
            duplicate = Obj.query.filter(
                func.lower(
                    Obj.disbursement_number
                    ) == func.lower(self.disbursement_number), 
                    Obj.id != self.id
                    ).first()
            if duplicate:
                self.errors["disbursement_number"] = "CD number is already used, please verify."        

        if not self.check_number:
            self.errors["check_number"] = "Please type check number."
        else:
            duplicate = Obj.query.filter(
                func.lower(
                    Obj.check_number
                    ) == func.lower(self.check_number), 
                    Obj.id != self.id
                    ).first()
            if duplicate:
                self.errors["check_number"] = "Check number is already used, please verify."        

        if not self.check_name_id:
            self.errors["check_name_id"] = "Please select name on check."

        for i in range(DETAIL_ROWS):
            if not self.details[i][1]._validate():
                detail_validation = False

        all_not_dirty = True
        for _, detail in self.details:
            if detail._is_dirty():
                all_not_dirty = False

        if all_not_dirty:
            self.errors["entry"] = "There should be at least one entry."       
    
        if not self.errors and detail_validation:
            return True        
    
    def _submit(self):
        self.submitted = str(datetime.today())[:10]

    @property
    def _locked(self):
        if self.submitted or self.cancelled:
            return True
        else:
            return False
