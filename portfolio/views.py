import copy
from decimal import Decimal
from secrets import FINNHUB_API_KEY
from django.http.response import JsonResponse
from django.db import transaction
from django.db.models import F
from rest_framework import status
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import finnhub
from portfolio.serializers import TransactionSerializer, \
    HoldingSerializer, SplitTransactionSerializer
from portfolio.models import DepositAndWithdrawalRecord, \
    SplitTransaction, Transaction, Holding


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
        serializer.is_valid(raise_exception=True)
        transaction = Transaction.objects.get_or_create(user=request.user, 
            **serializer.validated_data)[0]
        holding = Holding.objects.get_or_create(
            user=request.user, 
            ticker=transaction.ticker, 
            default={'num_shares': 0, 'total_cost': 0}
        )[0]
        holding.num_shares += transaction.num_shares
        holding.total_cost += transaction.total_cost
        holding.save()
        return Response({'status': 'success'})

    @action(methods=['post'], detail=False, 
        url_path='split-transaction', 
        url_name='split_trasaction')
    def split_trasaction(self, request):
        serializer = SplitTransactionSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response('bad request', status=status.HTTP_400_BAD_REQUEST)
        print(serializer.validated_data)
        for split_request in serializer.validated_data:
            with transaction.atomic():
                from_t = Transaction.objects.get(
                    pk=split_request['from_transaction_id'])
                to_t = copy.deepcopy(from_t)
                to_t.pk = None
                from_user_holding = Holding.objects.get(
                    user=from_t.user, ticker=from_t.ticker)
                to_user_holding = Holding.objects.get_or_create(
                    user=split_request['to_user_id'],
                    ticker=from_t.ticker,
                    defaults={'num_shares': 0, 'total_cost': 0})

                percent_out = split_request['num_shares'] / float(from_t.num_shares)
                orig_total_cost = from_t.total_cost
                orig_transaction_fee = from_t.transaction_fee

                to_t.user = split_request['to_user_id']
                from_t.num_shares -= split_request['num_shares']
                to_t.num_shares = split_request['num_shares']
                from_user_holding.num_shares -= split_request['num_shares']
                from_t.total_cost *= 1 - percent_out
                from_t.transaction_fee *= 1 - percent_out
                from_user_holding.total_cost -= (orig_total_cost - from_t.total_cost) + \
                    (orig_transaction_fee - from_t.transaction_fee)
                from_t.save()
                from_user_holding.save()

                to_user_holding.num_shares += to_t.num_shares
                to_t.total_cost = orig_total_cost - to_t.total_cost
                to_t.transaction_fee = orig_transaction_fee - to_t.transaction_fee
                to_user_holding.total_cost += to_t.total_cost + to_t.transaction_fee
                to_t.save()
                to_user_holding.save()
                
        return JsonResponse(serializer.validated_data, safe=False)
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


class SplitTransactionViewSet(viewsets.ModelViewSet):
    queryset = SplitTransaction.objects.all()
    serializer_class = SplitTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        serializer = SplitTransactionSerializer(data=request.data, 
            many=True)
        serializer.is_valid(raise_exception=True)
        print(serializer.validated_data)
        for split_request in serializer.validated_data:
            from_t = Transaction.objects.get(
                pk=split_request['from_transaction_id'])
            to_t = Transaction.objects.get_or_create(
                user=split_request['to_user'],
                transaction_time=from_t.transaction_time,
                defaults={
                    'ticker': from_t.ticker, 'num_shares': 0,
                    'currency': from_t.currency,
                    'total_cost': 0, 'transaction_fee':0
                })
            percent_out = split_request['num_shares_transferred'] /\
                float(from_t.num_shares)
            # [note] 'F' is used to avoid race condition
            to_t.num_shares = F('num_shares') + \
                split_request['num_shares_transferred']
            to_t.total_cost = F('total_cost') + \
                percent_out * from_t.total_cost
            to_t.transaction_fee = F('transaction_fee') + \
                percent_out * from_t.transaction_fee

class HoldingViewSet(viewsets.ModelViewSet):
    serializer_class = HoldingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Holding.objects.filter(user=self.request.user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = HoldingSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path='get-profit', 
        url_name='get_profit')
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
        for deposit in DepositAndWithdrawalRecord.objects.all():
            total_deposits += deposit.amount
        total_profit = curr_assets - total_deposits
        return Response({
            'total_profit': total_profit, 
            'profit_percentage': total_profit / total_deposits
        })

