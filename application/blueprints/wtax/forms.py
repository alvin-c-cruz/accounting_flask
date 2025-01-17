from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import Wtax as Obj
from .models import UserWtax as Preparer
from . import app_name

INTEGER_FIELDS = ["wtax_type_id"]
FLOAT_FIELDS = ["tax_rate"]


@dataclass
class Form:
    id: int = None
    wtax_name: str = ""
    atc: str = ""
    tax_rate: float = 0
    wtax_type_id: int = 0
    
    user_prepare_id: int = None
    user_prepare: str = ""

    errors = {}

    def _attributes(self):
        attributes = [x for x in dir(self) if (not x.startswith("_"))]
        for i in ("user_prepare_id", "user_prepare", "errors", "active"):
            try:
                attributes.remove(i)
            except ValueError:
                pass
        return attributes

    def _populate(self, object):
        for i in self._attributes():
            setattr(self, i, getattr(object, i))

        self.user_prepare = object.user_prepare

    def _save(self):
        if self.id is None:
            # Add a new record
            _dict = {}
            for i in self._attributes(): _dict[i] = getattr(self, i)

            record = Obj(**_dict)
            record.active = True

            db.session.add(record)
            db.session.commit()

            _dict = {
                f"{app_name}_id": record.id
            }
            preparer = Preparer(**_dict)
            preparer.user_id = self.user_prepare_id

            db.session.add(preparer)
            db.session.commit()

        else:
            # Update an existing record
            record = Obj.query.get_or_404(self.id)
            _dict = {
                f"{app_name}_id": record.id
            }
            preparer = Preparer.query.filter_by(**_dict).first()

            if record:
                for i in self._attributes():
                    setattr(record, i, getattr(self, i))
                preparer.user_id = self.user_prepare_id

            db.session.commit()

    def _post(self, request_form):
        self.id = request_form.get('record_id')
        for i in self._attributes():
            if i != "id":
                if i in INTEGER_FIELDS:
                    setattr(self, i, int(request_form.get(i)))
                elif i in FLOAT_FIELDS:
                    setattr(self, i, float(request_form.get(i)))
                else:
                    setattr(self, i, request_form.get(i).upper())

    def _validate_on_submit(self):
        self.errors = {}

        if not self.wtax_name:
            existing_ = Obj.query.filter(func.lower(Obj.wtax_name) == func.lower(self.wtax_name), Obj.id != self.id).first()
            if existing_:
                self.errors["wtax_name"] = "Wtax description already exists."

        if not self.atc:
            self.errors["atc"] = "Please type atc."

        if not self.wtax_type_id:
            self.errors["wtax_type_id"] = "Please select wtax type."

        if not self.errors:
            return True
        else:
            return False    
