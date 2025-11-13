from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Ad, Categorie
from .serializers import AdSerializer, CategorySerializer


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all().order_by('-created_at')
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Associe automatiquement l'annonce à l'utilisateur connecté
        serializer.save(owner=self.request.user)

    # 🔹 Incrémentation automatique à chaque consultation
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views = (instance.views or 0) + 1
        instance.save(update_fields=["views"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # 🔹 (Optionnel) endpoint spécifique pour incrémenter depuis le front
    @action(detail=True, methods=["post"])
    def increment_view(self, request, pk=None):
        ad = self.get_object()
        ad.views = (ad.views or 0) + 1
        ad.save(update_fields=["views"])
        return Response({"views": ad.views})


class AdListCreateView(generics.ListCreateAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Ad.objects.all().order_by('-created_at')

        # --- 🔍 Récupération des paramètres de recherche ---
        mine = self.request.query_params.get('mine')
        q = self.request.query_params.get('q')
        ville = self.request.query_params.get('ville')
        prix_max = self.request.query_params.get('prix_max')
        categorie = self.request.query_params.get('categorie')

        # --- 👤 Filtrer uniquement les annonces du user connecté ---
        if mine and self.request.user.is_authenticated:
            queryset = queryset.filter(owner=self.request.user)

        # --- 🔎 Recherche par mot-clé ---
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q)
            )

        # --- 🏙️ Filtrer par ville ---
        if ville:
            queryset = queryset.filter(Q(location__icontains=ville) | Q(owner__city__icontains=ville))

        # --- 💰 Filtrer par prix maximum ---
        if prix_max:
            try:
                queryset = queryset.filter(price__lte=float(prix_max))
            except ValueError:
                pass  # ignore si l'utilisateur entre une valeur invalide

        # --- 🗂️ Filtrer par catégorie ---
        if categorie:
            queryset = queryset.filter(category__name__icontains=categorie)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AdDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)
