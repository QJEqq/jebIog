from decimal import Decimal

from catalog.models import Component, Computer


class Cart:
    SESSION_KEY = 'cart'
    VALID_ITEM_TYPES = {
        'computer': Computer,
        'component': Component,
    }

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if not cart:
            cart = self.session[self.SESSION_KEY] = {}
        self.cart = cart

    def _normalize_item_type(self, item_type):
        if hasattr(item_type, '_meta'):
            item_type = item_type._meta.model_name
        elif hasattr(item_type, '__name__'):
            item_type = item_type.__name__

        item_type = str(item_type).lower().strip()
        if item_type not in self.VALID_ITEM_TYPES:
            raise ValueError(f'Unsupported item type: {item_type}')
        return item_type

    def _get_bucket(self, item_type, create=False):
        item_type = self._normalize_item_type(item_type)
        if create and item_type not in self.cart:
            self.cart[item_type] = {}
        return item_type, self.cart.get(item_type, {})

    def save(self):
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True

    def add(self, item, item_type, quantity=1, override_quantity=False):
        item_id = str(item.id)
        available_stock = item.quantity_in_stock
        if item_type not in self.cart:
            self.cart[item_type] = {}

        if item_id not in self.cart[item_type]:
            self.cart[item_type][item_id] = {'quantity': 0}

        if override_quantity:
            self.cart[item_type][item_id]['quantity'] = quantity
        else:
            self.cart[item_type][item_id]['quantity'] += quantity

        
        if self.cart[item_type][item_id]['quantity'] <= 0:
            del self.cart[item_type][item_id]
        elif self.cart[item_type][item_id]['quantity'] >= available_stock:
            self.cart[item_type][item_id]['quantity'] = available_stock
            
            # Если в категории (например, 'computer') пусто, удаляем и её
            if not self.cart[item_type]:
                del self.cart[item_type]

        self.save()

        

    def remove(self, item, item_type):
        item_type, bucket = self._get_bucket(item_type)
        item_id = str(item.id)

        if item_id in bucket:
            del bucket[item_id]

        if bucket:
            self.cart[item_type] = bucket
        elif item_type in self.cart:
            del self.cart[item_type]

        self.save()

    def __iter__(self):
        for item_type, items in self.cart.items():
            model_class = self.VALID_ITEM_TYPES.get(item_type)
            if not model_class: continue

            # Берем только те ID, где количество > 0
            clean_ids = [int(tid) for tid, data in items.items() if data['quantity'] > 0]
            
            if not clean_ids: continue

            products = model_class.objects.filter(id__in=clean_ids)
            products_dict = {p.id: p for p in products}

            for item_id_str, data in items.items():
                qty = data['quantity']
                if qty > 0: # Дополнительная проверка
                    product = products_dict.get(int(item_id_str))
                    if product:
                        product.quantity = qty
                        product.item_type = item_type
                        product.total_price = product.price * qty
                        yield product

    def get_total_price(self):
        total = 0
        for item_type, items in self.cart.items():
            model_class = self.VALID_ITEM_TYPES.get(item_type)
            if not model_class:
                continue
            
            item_ids = items.keys()
            products = model_class.objects.filter(id__in=item_ids)
            
            for p in products:
                qty = items[str(p.id)]['quantity']
                total += p.price * qty
        return total

    def __len__(self):
        return sum(
            item_data['quantity']
            for items in self.cart.values()
            for item_data in items.values()
        )



    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.cart = self.session[self.SESSION_KEY]
        self.session.modified = True

    def get_item_quantity(self, item_type, item_id):
        item_type , bucket = self._get_bucket(item_type)
        item_data = bucket.get(str(item_id))
        return item_data['quantity'] if item_data else 0
