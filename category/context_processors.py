from .models import Category

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)
    #retorno un dictionary con el valor de links, osea los objetos de category
    #esta funcion la registro en settings para que todos los html puedan usarla
    #esto llamada todos los nombres de cada categoria, la uso para desplegable categoria en home.html