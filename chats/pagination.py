from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    page_size = 20 # Nombre d'éléments par page
    page_size_query_param = 'page_size' # Permet de changer la taille via ?page_size=X
    max_page_size = 100 # Taille maximale autorisée