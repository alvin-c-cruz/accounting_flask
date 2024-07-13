app_name = "vat"
app_label = "VAT"
model_name = "Vat"

menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import Vat
