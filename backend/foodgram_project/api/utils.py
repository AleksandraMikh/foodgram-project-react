import io

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, SimpleDocTemplate, TableStyle
from reportlab.lib import colors
from django.db import models
from django.http import FileResponse
from recipes.models import IngredientRecipe


def pdf_maker(request):
    buffer = io.BytesIO()

    pdfmetrics.registerFont(
        TTFont('TimesNewRoman',
               'static_backend/api/fonts/times new roman.ttf'))
    recipes = request.user.recipes_in_cart.all()
    queryset = IngredientRecipe.objects.filter(
        recipe__in=recipes).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(amount=models.Sum('amount'))
    content = [('ингредиент', 'количество', 'единица измерения'), ]
    for item in queryset:
        content.append(
            (item['ingredient__name'],
                item['amount'],
                item['ingredient__measurement_unit']))

    doc = SimpleDocTemplate(buffer)
    t = Table(content)

    list_style = TableStyle(
        [('LINEABOVE', (0, 0), (-1, 0), 2, colors.green),
            ('LINEABOVE', (0, 1), (-1, 1), 2, colors.green),
            ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONT', (0, 0), (-1, -1), 'TimesNewRoman')]
    )

    t.setStyle(list_style)
    doc.build([t])

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
