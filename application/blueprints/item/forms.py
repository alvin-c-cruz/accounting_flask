from dataclasses import dataclass
from sqlalchemy import func
from application.extensions import db
from .models import Item as Obj
from .models import UserItem as Preparer
from . import app_name

INTEGER_FIELDS = []
FLOAT_FIELDS = []


@dataclass
class Form:
    id: int = None
    item_name: str = ""
    
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

        if not self.item_name:
            self.errors["item_name"] = "Please type item name."
        else:
            existing_ = Obj.query.filter(func.lower(Obj.item_name) == func.lower(self.item_name), Obj.id != self.id).first()
            if existing_:
                self.errors["item_name"] = "Item name already exists."

        if not self.errors:
            return True
        else:
            return False    
