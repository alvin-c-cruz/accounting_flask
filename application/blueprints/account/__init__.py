app_name = "account"
app_label = "Account"
model_name = "Account"

menu_label = (app_name, f"/{app_name}", app_label)


from .views import bp
from .models import Account
