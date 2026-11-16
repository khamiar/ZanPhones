from rest_framework.routers import DefaultRouter
from .views import BranchViewSet, BranchStockViewSet

router = DefaultRouter()

router.register("branches", BranchViewSet)
router.register("stock", BranchStockViewSet)

urlpatterns = router.urls