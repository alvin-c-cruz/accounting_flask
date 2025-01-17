from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, g
import json
from sqlalchemy.exc import IntegrityError
from .models import AccountClassification as Obj
from .models import UserAccountClassification as Preparer
from .models import AdminAccountClassification as Approver
from .forms import Form
from application.extensions import db, Url
from application.blueprints.user import login_required, roles_accepted
from flask_login import current_user

from . import app_name, app_label


bp = Blueprint(app_name, __name__, template_folder="pages", url_prefix=f"/{app_name}")
ROLES_ACCEPTED = app_label


@bp.route("/")
@login_required
@roles_accepted([ROLES_ACCEPTED])
def home():
    rows = Obj.query.order_by(getattr(Obj, "priority")).all()
    for row in rows:
        row.url = Url(row)

    context = {
        "rows": rows,
        "app_name": app_name,
        "url": Url(Obj),
        "app_label": app_label,
    }

    return render_template(f"{app_name}/home.html", **context)


@bp.route("/add", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def add():
    form = Form(Obj)
    if request.method == "POST":
        obj = Obj()
        form.post(request, obj)
        obj.active = True

        if form.validate_on_submit():
            db.session.add(obj)
            db.session.commit()

            prepared_dict = {
                "user_id": current_user.id, 
                f"{app_name}_id": obj.id
            }
            prepared_by = Preparer(**prepared_dict)
            db.session.add(prepared_by)
            db.session.commit()

            return redirect(url_for(f'{app_name}.home'))

    context = {
        "form": form,
        "url": Url(Obj),
        "app_name": app_name,
        "app_label": app_label,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route(f"/edit/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def edit(record_id):   
    obj = Obj.query.get_or_404(record_id)
    form = Form(Obj)

    if request.method == "POST":
        form.post(request, obj)
        obj.active = True

        if form.validate_on_submit():
            # Delete old preparer
            old_preparer_dict = {
                f"{app_name}_id": obj.id
            }
            old_preparer = Preparer.query.filter_by(**old_preparer_dict).first_or_404()
            db.session.delete(old_preparer)

            # Record new preparer
            prepared_dict = {
                "user_id": current_user.id, 
                f"{app_name}_id": obj.id
            }
            prepared_by = Preparer(**prepared_dict)
            db.session.add(prepared_by)
            db.session.commit()

            return redirect(url_for(f'{app_name}.home'))
    else:
        form.get(obj)

    context = {
        "form": form,
        "url": Url(obj),
        "app_name": app_name,
        "app_label": app_label,
    }

    return render_template(f"{app_name}/form.html", **context)


@bp.route("/delete/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def delete(record_id):   
    obj = Obj.query.get_or_404(record_id)
    preparer = obj.preparer
    try:
        db.session.delete(preparer)
        db.session.delete(obj)
        db.session.commit()
        flash(f"{obj} has been deleted.", category="success")
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete {obj} because it has related records.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/approve/<int:record_id>", methods=['GET'])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def approve(record_id):
    if not current_user.admin:
        flash("Administrator rights required.", category="error")
        return redirect(url_for(f"{app_name}.home"))
    
    obj = Obj.query.get_or_404(record_id)

    _dict = {
        f"{app_name}_id": record_id
    }
    approve = Approver(**_dict)
    approve.user_id = current_user.id

    db.session.add(approve)
    db.session.commit()

    flash(f"Approved: {getattr(obj, f'{app_name}_name')}", category="success")
    return redirect(url_for(f'{app_name}.home'))   
    

@bp.route("/activate/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def activate(record_id):   
    obj = Obj.query.get_or_404(record_id)
    obj.active = True    

    db.session.commit()

    flash(f"{obj} has been activated.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/deactivate/<int:record_id>", methods=["POST", "GET"])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def deactivate(record_id):   
    obj = Obj.query.get_or_404(record_id)
    obj.active = False    

    db.session.commit()

    flash(f"{obj} has been deactivated.", category="error")

    return redirect(url_for(f'{app_name}.home'))


@bp.route("/unlock/<int:record_id>", methods=['GET'])
@login_required
@roles_accepted([ROLES_ACCEPTED])
def unlock(record_id):
    if not current_user.admin:
        flash("Administrator rights required.", category="error")
        return redirect(url_for(f'{app_name}.home'))
    
    obj = Obj.query.get_or_404(record_id)
    obj.active = True

    _dict = {
        f"{app_name}_id": record_id
    }

    approve = Approver.query.filter_by(**_dict).first()
    
    db.session.delete(approve)
    db.session.commit()

    flash(f"Unlocked: {obj}", category="error")
    return redirect(url_for(f'{app_name}.home'))   
    

@bp.route("/_autocomplete", methods=['GET'])
def autocomplete():
    rows = [row for row in Obj.query.order_by(getattr(Obj, f"{app_name}_name")).all()]
    return Response(json.dumps(rows), mimetype='application/json')
