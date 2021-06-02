from django import template
from django.utils.safestring import mark_safe

register = template.Library()

TABLE_HEAD = """
                <table class="table">
                <tbody>
             """

TABLE_TAIL = """
                </tbody>
                </table>
             """

TABLE_CONTENT = """
                   <tr>
                    <td>{name}</td>
                    <td>{value}</td>
                   </tr>
                """

PRODUCT_SPEC = {
    'notebook': {
        'Диагональ': 'diagonal',
        'Дисплей': 'display_type',
        'Частота процессора': 'processor_freq',
        'Оперативная память': 'ram',
        'Видеокарта': 'video',
        'Время работы аккумулятора': 'time_without_charge'
    },
    'smartphone': {
        'Диагональ': 'diagonal',
        'Дисплей': 'display_type',
        'Объем батареии': 'accum_volume',
        'sd': 'sd',
        'Задняя камера': 'main_cam_mp',
        'Передняя камера': 'frontal_cam_mp'
    }
}

def get_product_spec(product, model_name):
    table_content = ''
    for name, value in PRODUCT_SPEC[model_name].items():
        table_content += TABLE_CONTENT.format(name=name, value=getattr(product, value))
    return table_content

@register.filter
def product_spec(product):
    model_name = product.__class__._meta.model_name
    return mark_safe(TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL)