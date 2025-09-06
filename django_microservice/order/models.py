from django.db import models


class Order(models.Model):
    product_name = models.CharField('Название товара')
    quantity = models.IntegerField('Количество')
    customer_name = models.CharField('Имя заказчика')
    customer_email = models.EmailField('Еmail заказчика')
    status = models.CharField('Статус')
    created_at = models.CharField('Создан')

    def __str__(self):
        return f'Order: {self.product_name}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
