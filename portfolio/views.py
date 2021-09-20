from portfolio.serializers import TransactionSerializer
from portfolio.models import Transaction
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status

# class ListTransactions(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, format=None):
#         transactions = Transaction.objects.filter(user=request.user)
#         return Response(transactions)

#     def post(self, request):

class TransactionsViewSet(viewsets.ModelViewSet):
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
            Transaction.objects.create(user=request.user, **serializer.validated_data)
            return Response({'status': 'success'})
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
