app_name = "disbursement"
app_label = "Disbursement"
menu_label = (app_name, f"/{app_name}", app_label)
model_name = "Disbursement"


from .views import bp
from .models import Disbursement, DisbursementDetail
