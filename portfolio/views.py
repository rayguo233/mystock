from rest_framework.decorators import action
from portfolio.serializers import TransactionSerializer, HoldingSerializer
from portfolio.models import Transaction, Holding
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status
import requests
from decimal import Decimal


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
            transaction = Transaction.objects.create(user=request.user, **serializer.validated_data)
            try:
                holding = Holding.objects.filter(user=request.user, ticker=transaction.ticker)[0]
            except IndexError:
                holding = Holding.objects.create(user=request.user, ticker=transaction.ticker, 
                    num_shares=transaction.num_shares, total_cost=transaction.total_cost)
            else:
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
        queryset = self.get_queryset()
        profit = {}
        total_profit = 0
        for holding in queryset:
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={holding.ticker}&apikey=J1HPLK5KK39B2PTS'
            data = requests.get(url).json()
            data = list(data['Time Series (Daily)'].items())
            cost = holding.total_cost
            curr_value = Decimal(data[0][1]['5. adjusted close']) * holding.num_shares
            profit[holding.ticker] = curr_value - cost
            total_profit += curr_value - cost
        return Response({'profit': profit, 'total_profit': total_profit})
