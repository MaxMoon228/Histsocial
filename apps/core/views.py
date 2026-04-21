from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from apps.axis.models import TimelineNode
from apps.catalog.models import Material
from apps.common.models import ExternalClickLog, SearchQueryLog, Tag
from apps.events.models import HistoricalEvent
from apps.tests_catalog.models import TestItem
from .models import HomePageAuthorBlock


def home(request):
    featured_materials = Material.objects.filter(is_published=True, is_archived=False).select_related("source")[:3]
    era_tags = Tag.objects.filter(tag_type="era")[:10]
    author_block = HomePageAuthorBlock.objects.filter(is_active=True).first()
    if not author_block:
        author_block = HomePageAuthorBlock.objects.create(
            is_active=True,
            section_label="Автор проекта",
            title_text="Автор сайта — Билалова Дина Султановна.",
            subtitle_text="Учитель истории и обществознания высшей квалификационной категории, преподаватель СОШИ Лицей имени Н. И. Лобачевского КФУ.",
            description_text="Проект объединяет академическую точность, современные учебные маршруты и удобную навигацию по ключевым темам.",
        )
    context = {
        "featured_materials": featured_materials,
        "era_tags": era_tags,
        "author_block": author_block,
        "popular_queries": [
            "Пётр I",
            "Французская революция",
            "1812 год",
            "Экономика",
            "Право",
            "Политика",
            "Социальные отношения",
        ],
    }
    return render(request, "core/home.html", context)


def about(request):
    stats = {
        "materials": Material.objects.filter(is_published=True, is_archived=False).count(),
        "tests": TestItem.objects.filter(is_published=True).count(),
        "events": HistoricalEvent.objects.filter(is_published=True).count(),
        "axis_nodes": TimelineNode.objects.filter(is_published=True).count(),
    }
    useful_resources = [
        {
            "title": "History.ru",
            "url": "https://history.ru/",
            "domain": "history.ru",
            "description": "Исторические статьи, материалы и аналитика по ключевым эпохам.",
            "image_url": "https://historyrussia.org/images/16042026_RAO/SHAR0867_1.jpg",
        },
        {
            "title": "Российское историческое общество",
            "url": "https://historyrussia.org/",
            "domain": "historyrussia.org",
            "description": "Официальный портал с событиями, проектами и историческими публикациями.",
            "image_url": "https://historyrussia.org/images/jsn_is_thumbs/images/Slideshow_CK_Test/2026/Red_Square_2026_1.jpg",
        },
        {
            "title": "Конкурс «История в школе: традиции и новации»",
            "url": "https://fond.historyrussia.org/vserossijskij-konkurs-istoriya-v-shkole-traditsii-i-novatsii.html",
            "domain": "fond.historyrussia.org",
            "description": "Всероссийский конкурс образовательных практик для преподавателей истории.",
            "image_url": "https://historyrussia.org/images/jsn_is_thumbs/images/Slideshow_CK_Test/2026/Youth_schools_1.jpg",
        },
        {
            "title": "Культура.РФ",
            "url": "https://www.culture.ru/",
            "domain": "culture.ru",
            "description": "Культурные гиды, лекции, архивы и цифровые выставки по России.",
            "image_url": "https://historyrussia.org/images/jsn_is_thumbs/images/Slideshow_CK_Test/2026/Zasechnie_line_3.jpg",
        },
        {
            "title": "Арзамас",
            "url": "https://arzamas.academy/mag",
            "domain": "arzamas.academy",
            "description": "Научно-популярные курсы и статьи по гуманитарным дисциплинам.",
            "image_url": "https://historyrussia.org/images/13042026_225_Dal/SHAR0090_2.jpg",
        },
        {
            "title": "I Love Economics",
            "url": "https://www.iloveeconomics.ru/",
            "domain": "iloveeconomics.ru",
            "description": "Олимпиадные задачи, книги, видео и материалы по экономике для школьников.",
            "image_url": "https://iloveeconomics.ru/add/img/ILE_stamp_large.png",
        },
        {
            "title": "Онлайн-уроки по финансовой грамотности",
            "url": "https://dni-fg.ru/",
            "domain": "dni-fg.ru",
            "description": "Интерактивные онлайн-уроки по финансовой грамотности для школьников и педагогов.",
            "image_url": "https://static.tildacdn.com/tild3033-3765-4436-a561-373639343066/Deskto42p-Compressif.jpg",
        },
        {
            "title": "Финансовая культура",
            "url": "https://fincult.info/",
            "domain": "fincult.info",
            "description": "Просветительский ресурс Банка России о личных финансах, безопасности и полезных сервисах.",
            "image_url": "https://fincult.info/f/dist/images/share/share.jpg",
        },
    ]
    return render(request, "core/about.html", {"stats": stats, "useful_resources": useful_resources})


def materials(request):
    return render(request, "core/textbooks.html")


def textbooks(request):
    return redirect("materials")


def search_results(request):
    query = request.GET.get("q", "").strip()
    materials = Material.objects.none()
    tests = TestItem.objects.none()
    events = HistoricalEvent.objects.none()
    nodes = TimelineNode.objects.none()
    if query:
        if request.session.session_key is None:
            request.session.save()
        SearchQueryLog.objects.create(
            query=query,
            session_key=request.session.session_key or "",
            page_context=request.path,
        )
        materials = Material.objects.filter(is_published=True, is_archived=False).filter(Q(title__icontains=query) | Q(short_description__icontains=query))
        tests = TestItem.objects.filter(is_published=True).filter(Q(title__icontains=query) | Q(short_description__icontains=query))
        events = HistoricalEvent.objects.filter(is_published=True).filter(Q(title__icontains=query) | Q(summary__icontains=query))
        nodes = TimelineNode.objects.filter(is_published=True).filter(Q(title__icontains=query) | Q(description__icontains=query))
    return render(
        request,
        "core/search_results.html",
        {
            "query": query,
            "materials": materials[:12],
            "tests": tests[:12],
            "events": events[:12],
            "nodes": nodes[:12],
        },
    )


@require_GET
def search_suggest(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return HttpResponse("")
    context = {
        "query": query,
        "materials": Material.objects.filter(is_published=True, is_archived=False, title__icontains=query)[:4],
        "tests": TestItem.objects.filter(is_published=True, title__icontains=query)[:4],
        "events": HistoricalEvent.objects.filter(is_published=True, title__icontains=query)[:4],
        "nodes": TimelineNode.objects.filter(is_published=True, title__icontains=query)[:4],
    }
    return render(request, "includes/components/search_suggest.html", context)


def health(request):
    return HttpResponse("ok", content_type="text/plain")


def external_go(request, content_type, pk):
    model_map = {
        "material": Material,
        "test": TestItem,
        "event": HistoricalEvent,
    }
    model = model_map.get(content_type)
    if not model:
        raise Http404
    item = get_object_or_404(model, pk=pk)
    target_url = getattr(item, "target_url", "") or ""
    if not target_url:
        return render(request, "core/link_error.html", {"item": item}, status=404)

    if request.session.session_key is None:
        request.session.save()
    ExternalClickLog.objects.create(
        session_key=request.session.session_key or "",
        content_type=ContentType.objects.get_for_model(model),
        object_id=item.pk,
        target_url=target_url,
        referrer_path=request.META.get("HTTP_REFERER", ""),
    )
    return redirect(target_url)


def staff_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("staff_dashboard")
    error = ""
    next_url = request.GET.get("next") or request.POST.get("next") or "/staff/"
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect(next_url)
        error = "Неверный логин или пароль, либо нет доступа staff."
    return render(request, "core/staff/login.html", {"error": error, "next": next_url})


@login_required
def staff_logout(request):
    logout(request)
    return redirect("staff_login")


@login_required
@user_passes_test(lambda u: u.is_staff)
def staff_dashboard(request):
    materials_all = Material.objects.all()
    recent_materials = materials_all.select_related("source", "updated_by").order_by("-updated_at")[:8]
    context = {
        "total_cards": materials_all.count(),
        "published_cards": materials_all.filter(is_published=True, is_archived=False).count(),
        "draft_cards": materials_all.filter(is_published=False, is_archived=False).count(),
        "archived_cards": materials_all.filter(is_archived=True).count(),
        "without_tags_cards": materials_all.filter(tags__isnull=True).distinct().count(),
        "without_cover_cards": materials_all.filter(Q(cover_image="") | Q(cover_image__isnull=True)).count(),
        "without_url_cards": materials_all.filter(external_url="").filter(Q(primary_file="") | Q(primary_file__isnull=True)).count(),
        "recent_materials": recent_materials,
    }
    return render(request, "core/staff/dashboard.html", context)
