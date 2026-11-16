from rest_framework.routers import DefaultRouter
from .views import CurrencyConfigViewSet

router = DefaultRouter()

router.register("currencies", CurrencyConfigViewSet)

urlpatterns = router.urls