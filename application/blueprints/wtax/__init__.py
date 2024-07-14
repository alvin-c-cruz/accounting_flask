app_name = "wtax"
app_label = "Wtax"
model_name = "Wtax"

menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import Wtax
