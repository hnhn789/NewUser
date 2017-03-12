from rest_framework import serializers
from NewUser.models import BoughtItems, ItemList

class BoughtItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoughtItems
        fields = ('item_name', 'item_quantity')


class ItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemList
        fields = ('pk', 'name','price','remain')