from portfolio.views import TransactionsViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('transactions', TransactionsViewSet, basename='transaction')
urlpatterns = router.urls