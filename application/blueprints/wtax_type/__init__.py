app_name = "wtax_type"
app_label = "Wtax Type"
model_name = "WtaxType"

menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import WtaxType
