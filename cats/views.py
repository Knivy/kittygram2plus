from rest_framework import viewsets
#from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Achievement, Cat, User
from .permissions import OwnerOrReadOnly, ReadOnly
from .throttling import WorkingHoursRateThrottle
from .pagination import CatsPagination
from .serializers import AchievementSerializer, CatSerializer, UserSerializer


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    permission_classes = (OwnerOrReadOnly,)
    # throttle_classes = (AnonRateThrottle,)  # Подключили класс AnonRateThrottle 
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    throttle_scope = 'low_request'  # раз в минуту
    # pagination_class = PageNumberPagination  # уже установлено в settings
    # pagination_class = LimitOffsetPagination
    # pagination_class = CatsPagination 
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # Временно отключим пагинацию на уровне вьюсета, 
    # так будет удобнее настраивать фильтрацию
    pagination_class = None
    # Фильтровать будем по полям color и birth_year модели Cat
    filterset_fields = ('color', 'birth_year') 
    search_fields = ('^name', 'achievements__name', 'owner__username')
    ordering_fields = ('name', 'birth_year') 
    ordering = ('birth_year',) 

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user) 

    def get_permissions(self):
        # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернём обновлённый перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов без изменений
        return super().get_permissions()   

    # def get_queryset(self): # много эндпоинтов
    #     queryset = Cat.objects.all()
    #     color = self.kwargs['color']
    #     # Через ORM отфильтровать объекты модели Cat
    #     # по значению параметра color, полученного в запросе
    #     queryset = queryset.filter(color=color)
    #     return queryset   

    # def get_queryset(self):  # много однотипного кода
    #     queryset = Cat.objects.all()
    #     # Добыть параметр color из GET-запроса
    #     color = self.request.query_params.get('color')
    #     if color is not None:
    #         #  через ORM отфильтровать объекты модели Cat
    #         #  по значению параметра color, полученного в запросе
    #         queryset = queryset.filter(color=color)
    #     return queryset 

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer