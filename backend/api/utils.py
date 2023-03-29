from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from recipes.models import RecipeIngredient
from weasyprint import HTML

User = get_user_model()


def get_shopping_list(user: User) -> dict:
    return RecipeIngredient.objects.filter(
        recipe__shopping_recipe__user=user).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).annotate(
            amount=Sum('amount')
        ).values_list(
            'ingredient__name',
            'amount',
            'ingredient__measurement_unit'
        )


def render_pdf_response(html: str) -> HttpResponse:
    html_template = HTML(string=html)
    pdf_file = html_template.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=shopping_list.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    return response
