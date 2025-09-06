from django.contrib import admin
from recipe.models import Recipe, RecipeComment

admin.site.register(RecipeComment)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'time_minutes', 'price', 'description', 'ingredients')

    class Meta:
        model = Recipe
        fields = (
            'title',
            'time_minutes',
            'price',
            'description',
            'ingredients',
        )


# admin.site.register(Recipe)
