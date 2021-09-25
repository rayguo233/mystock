import finnhub
from rest_framework.decorators import action
from portfolio.serializers import TransactionSerializer, HoldingSerializer
from portfolio.models import DepositAndWithdrawal, Transaction, Holding
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status
from decimal import Decimal
from secrets import FINNHUB_API_KEY


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = Transaction.objects.filter(user=request.user)
        serializer = TransactionSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            transaction = Transaction.objects.get_or_create(user=request.user, **serializer.validated_data)[0]
            holding = Holding.objects.get_or_create(user=request.user, ticker=transaction.ticker, 
                default={'num_shares': 0, 'total_cost': 0})[0]
            holding.num_shares += transaction.num_shares
            holding.total_cost += transaction.total_cost
            holding.save()
            return Response({'status': 'success'})
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class HoldingViewSet(viewsets.ModelViewSet):
    serializer_class = HoldingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Holding.objects.filter(user=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = HoldingSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='get-profit', url_name='get_profit')
    def get_profit(self, request):
        total_profit = 0
        holdings = self.get_queryset()
        curr_assets = 0
        for holding in holdings:
            if holding.num_shares == 0:
                continue
            print('--------------------')
            print(holding.ticker)
            finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
            curr_value = Decimal(finnhub_client.quote(holding.ticker)['c']) * holding.num_shares
            curr_assets += curr_value
        total_deposits = 0
        for deposit in DepositAndWithdrawal.objects.all():
            total_deposits += deposit.amount
        total_profit = curr_assets - total_deposits
        return Response({
            'total_profit': total_profit, 
            'profit_percentage': total_profit / total_deposits
        })

