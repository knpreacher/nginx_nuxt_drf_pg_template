from rest_framework.routers import DefaultRouter

from .views import PublicCatalogItemViewSet

router = DefaultRouter()
router.register(r"", PublicCatalogItemViewSet, basename="public-catalog")

urlpatterns = router.urls
