from django.urls import reverse
from PIL import Image
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
# from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone


User = get_user_model()

# def get_models_count(*model_names):
#     return [models.Count(model_name) for model_name in model_names]
#
#
# def get_product_url(obj, viewname):
#
#     ct_model = obj.__class__._meta.model_name
#
#     return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})
#
#


class MinResolutionErrorException(Exception):
    pass

class MaxResolutionErrorException(Exception):
    pass

# class LatestProductsManager:
#
#     @staticmethod
#     def get_products_for_mainpage(*args, **kwargs):
#         with_respect_to = kwargs.get('with_respect_to')
#         products = []
#         ct_models = ContentType.objects.filter(model__in=args)
#         for ct_model in ct_models:
#             model_products = ct_model.model_class()._base_manager.all().order_by('id')[:5]
#             products.extend(model_products)
#         if with_respect_to:
#             ct_model = ContentType.objects.filter(model=with_respect_to)
#             if ct_model.exists():
#                 if with_respect_to in args:
#                     return sorted(
#                         products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
#                     )
#         return products


# class LatestProducts:
#
#     objects = LatestProductsManager
#
#
# class CategoryManager(models.Manager):
#
#     CATEGORY_NAME_COUNT_NAME = {
#         'Ноутбуки': 'notebook__count',
#         'Смартфоны': 'smartphone__count'
#     }
#
#     def get_queryset(self):
#         return super().get_queryset()
#
#     def get_categories_for_left_sidebar(self):
#         models = get_models_count('notebook', 'smartphone')
#         qs = list(self.get_queryset().annotate(*models))
#         data = [
#             dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
#             for c in qs
#         ]
#         return data



class Category(models.Model):

    name = models.CharField(max_length=200, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)
    # objects = CategoryManager()

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

class Product(models.Model):

    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (800, 800)
    MAX_IMAGE_SIZE = 3145728

    # class Meta:
    #     abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Цена')

    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        min_width, min_height = Product.MIN_RESOLUTION
        max_width, max_height = Product.MAX_RESOLUTION
        if image.size > Product.MAX_IMAGE_SIZE:
            raise ValidationError('Размер изображения не должен превышать 3МБ!')
        if img.height < min_height or img.width < min_width:
            raise MinResolutionErrorException('Разрешение изображения меньше минимального!')
        if img.height > max_height or img.width > max_width:
            raise MaxResolutionErrorException('Разрешение изображения больше максимального!')
        super().save(*args, **kwargs)


    def get_model_name(self):
        return self.__class__.__name__.lower()


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

# class Notebook(Product):
#
#     diagonal = models.CharField(max_length=200, verbose_name='Диагональ')
#     display_type = models.CharField(max_length=200, verbose_name='Тип дисплея')
#     processor_freq = models.CharField(max_length=200, verbose_name='Частота процессора')
#     ram = models.CharField(max_length=200, verbose_name='Оперативная память')
#     video = models.CharField(max_length=200, verbose_name='Видеокарта')
#     time_without_charge = models.CharField(max_length=200, verbose_name='Время работы без зарядки')
#
#     def __str__(self):
#         return f"{self.category.name} : {self.title}"
#
#
#     def get_absolute_url(self):
#         return get_product_url(self, 'product_detail')



# class Smartphone(Product):
#     diagonal = models.CharField(max_length=200, verbose_name='Диагональ')
#     display_type = models.CharField(max_length=200, verbose_name='Тип дисплея')
#     accum_volume = models.CharField(max_length=200, verbose_name='Объем батареии')
#     ram = models.CharField(max_length=200, verbose_name='Оперативная память')
#     sd = models.BooleanField(default=True, verbose_name='Наличие SD карты')
#     main_cam_mp = models.CharField(max_length=200, verbose_name='Задняя камера')
#     frontal_cam_mp = models.CharField(max_length=200, verbose_name='Передняя камера')
#
#     def __str__(self):
#         return f"{self.category.name} : {self.title}"
#
#     def get_absolute_url(self):
#         return get_product_url(self, 'product_detail')



class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Общая цена')

    def save(self, *args, **kwargs):
        self.final_price = self.quantity * self.product.price
        super().save(*args, **kwargs)



    def __str__(self):
        return f"Продукт {self.product.title} "

class Cart(models.Model):
    owner = models.ForeignKey('Customer', null=True, verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=6, default=0, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)


    def __str__(self):
        return str(self.id)

class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    adress = models.CharField(max_length=200, verbose_name='Адрес', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_customer')

    def __str__(self):
        return f"Покупатель {self.user.first_name} {self.user.last_name}"


class Order(models.Model):

    STATUS_NEW = ''
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLITED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'


    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLITED, 'Заказ выполнен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='related_orders', on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name='Корзина', null=True, blank=True)
    first_name = models.CharField(max_length=200, verbose_name='Имя')
    last_name = models.CharField(max_length=200, verbose_name='Фамилия')
    phone = models.CharField(max_length=200, verbose_name='Телефон')
    adress = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Cтатус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Тип заказа',
        choices=BUYING_TYPE_CHOICES,
        default=BUYING_TYPE_SELF
    )
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_data = models.DateTimeField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)

