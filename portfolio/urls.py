from django.conf.urls import include, url
from portfolio.views import TransactionViewSet, HoldingViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('transactions', TransactionViewSet, basename='transaction')
router.register('holdings', HoldingViewSet, basename='holding')

urlpatterns = [
    url('', include(router.urls)),
]