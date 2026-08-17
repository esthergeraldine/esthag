from django.db.models import Count, Exists, OuterRef, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from ..models import Article, ArticleSubscriber
from ..models.comment import Comment, CommentLike, ReportedComment


COMMENTS_PER_PAGE = 20
COMMENTS_PREVIEW_COUNT = 3


def _session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _get_or_create_subscriber(email, name=''):
    subscriber, created = ArticleSubscriber.objects.get_or_create(
        email=email.lower()
    )
    if name:
        subscriber.name = name[:100]
    if subscriber.status == 'unsubscribed':
        subscriber.status = 'pending'
        subscriber.generate_confirmation_token()
    elif not subscriber.confirmation_token:
        subscriber.generate_confirmation_token()
    subscriber.save()
    return subscriber


def _send_confirmation_email(subscriber, article_slug=None, request=None):
    from django.urls import reverse
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives

    token = subscriber.confirmation_token
    confirm_url = reverse('confirm_subscription', kwargs={'token': token})
    if article_slug:
        confirm_url = f"{confirm_url}?next=/blog/{article_slug}/discussion/"

    if request:
        confirmation_url = request.build_absolute_uri(confirm_url)
    else:
        confirmation_url = f"{settings.SITE_DOMAIN}{confirm_url}"

    context = {
        'name': subscriber.name or 'Abonné',
        'confirmation_url': confirmation_url,
    }

    subject = "Confirmez votre inscription à la newsletter"

    html_content = render_to_string('emails/newsletter_confirmation.html', context)
    text_content = render_to_string('emails/newsletter_confirmation.txt', context)

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[subscriber.email],
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=False)
        return True
    except Exception as e:
        return False


def _escape_content(content):
    import html
    return html.escape(content)


class DiscussionView(TemplateView):
    template_name = "blog_discussion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        article = get_object_or_404(Article.objects.filter(is_published=True), slug=slug)

        session_key = _session_key(self.request)

        sort = self.request.GET.get('sort', 'newest')
        search = self.request.GET.get('q', '').strip()

        comments_qs = Comment.objects.filter(
            article=article,
            status='published',
            parent=None
        ).select_related('article', 'article__author', 'subscriber')

        if search:
            comments_qs = comments_qs.filter(content__icontains=search)

        if sort == 'oldest':
            comments_qs = comments_qs.order_by('created_date')
        elif sort == 'popular':
            comments_qs = comments_qs.order_by('-likes_count')
        else:
            comments_qs = comments_qs.order_by('-created_date')

        total_count = comments_qs.count()

        liked_subquery = CommentLike.objects.filter(
            comment=OuterRef('pk'),
            session_key=session_key
        )
        comments_qs = comments_qs.annotate(
            likes_total=Count('likes', distinct=True),
            is_liked_by_me=Exists(liked_subquery),
            annotated_replies_count=Count('replies', filter=Q(replies__status='published'))
        )

        comments = comments_qs[:COMMENTS_PER_PAGE]

        context['article'] = article
        context['comments'] = comments
        context['total_count'] = total_count
        context['has_more'] = total_count > COMMENTS_PER_PAGE
        context['current_sort'] = sort
        context['search_query'] = search
        context['session_key'] = session_key
        context['previous_article'] = article.get_previous_article()
        context['next_article'] = article.get_next_article()

        context['total_replies'] = Comment.objects.filter(
            article=article,
            status='published',
            parent__isnull=False
        ).count()

        context['unique_commenters'] = Comment.objects.filter(
            article=article,
            status='published',
            subscriber__isnull=False
        ).values('subscriber__email').distinct().count()

        confirmed_email = self.request.session.get('confirmed_email')
        if confirmed_email:
            confirmed_subscriber = ArticleSubscriber.objects.filter(
                email=confirmed_email,
                status='confirmed'
            ).first()
            context['confirmed_subscriber'] = confirmed_subscriber
            context['user_email'] = confirmed_email
        else:
            context['confirmed_subscriber'] = None
            context['user_email'] = None

        return context


def discussion_stats(request, slug):
    from django.http import JsonResponse
    from django.db.models import Count, Q

    article = get_object_or_404(Article, slug=slug)

    total_comments = Comment.objects.filter(
        article=article,
        status='published',
        parent=None
    ).count()

    total_replies = Comment.objects.filter(
        article=article,
        status='published',
        parent__isnull=False
    ).count()

    unique_commenters = Comment.objects.filter(
        article=article,
        status='published',
        subscriber__isnull=False
    ).values('subscriber__email').distinct().count()

    return JsonResponse({
        'total_comments': total_comments,
        'total_replies': total_replies,
        'unique_commenters': unique_commenters,
    })


@require_POST
def add_comment(request):
    slug = request.POST.get('article_slug', '').strip()
    article = get_object_or_404(Article, slug=slug)

    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    content = request.POST.get('content', '').strip()
    honeypot = request.POST.get('website', '').strip()

    if honeypot:
        return JsonResponse({'success': False, 'error': 'Erreur.'}, status=400)

    if not name or not email or not content:
        return JsonResponse({'success': False, 'error': 'Tous les champs sont requis.'}, status=400)

    if len(content) > 5000:
        return JsonResponse({'success': False, 'error': 'Commentaire trop long.'}, status=400)

    url_count = content.count('http://') + content.count('https://')
    if url_count > 3:
        return JsonResponse({'success': False, 'error': 'Trop de liens.'}, status=400)

    subscriber = _get_or_create_subscriber(email, name)

    if not subscriber.is_confirmed():
        subscriber.generate_confirmation_token()
        _send_confirmation_email(subscriber, slug, request)
        return JsonResponse({
            'success': False,
            'needs_confirmation': True,
            'error': 'Veuillez confirmer votre email pour publier un commentaire. Un lien de confirmation a été envoyé.'
        }, status=403)

    comment = Comment.objects.create(
        article=article,
        subscriber=subscriber,
        name=name[:100],
        email=email.lower(),
        content=_escape_content(content),
        status='published'
    )

    liked_subquery = CommentLike.objects.filter(
        comment=OuterRef('pk'),
        session_key=_session_key(request)
    )
    comment = Comment.objects.filter(pk=comment.pk).annotate(
        likes_total=Count('likes', distinct=True),
        is_liked_by_me=Exists(liked_subquery),
        annotated_replies_count=Count('replies', filter=Q(replies__status='published'))
    ).first()

    return JsonResponse({
        'success': True,
        'comment': _serialize_comment(comment)
    })


@require_POST
def add_reply(request, comment_id):
    parent_comment = get_object_or_404(
        Comment.objects.filter(status='published'),
        id=comment_id
    )

    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    content = request.POST.get('content', '').strip()
    honeypot = request.POST.get('website', '').strip()

    if honeypot:
        return JsonResponse({'success': False, 'error': 'Erreur.'}, status=400)

    if not name or not email or not content:
        return JsonResponse({'success': False, 'error': 'Tous les champs sont requis.'}, status=400)

    if len(content) > 5000:
        return JsonResponse({'success': False, 'error': 'Commentaire trop long.'}, status=400)

    subscriber = _get_or_create_subscriber(email, name)

    if not subscriber.is_confirmed():
        subscriber.generate_confirmation_token()
        _send_confirmation_email(subscriber, parent_comment.article.slug, request)
        return JsonResponse({
            'success': False,
            'needs_confirmation': True,
            'error': 'Veuillez confirmer votre email pour publier une réponse. Un lien de confirmation a été envoyé.'
        }, status=403)

    reply = Comment.objects.create(
        article=parent_comment.article,
        parent=parent_comment,
        subscriber=subscriber,
        name=name[:100],
        email=email.lower(),
        content=_escape_content(content),
        status='published'
    )

    new_replies_count = Comment.objects.filter(
        parent=parent_comment,
        status='published'
    ).count()
    parent_comment.replies_count = new_replies_count
    parent_comment.save(update_fields=['replies_count'])

    liked_subquery = CommentLike.objects.filter(
        comment=OuterRef('pk'),
        session_key=_session_key(request)
    )
    reply = Comment.objects.filter(pk=reply.pk).annotate(
        likes_total=Count('likes', distinct=True),
        is_liked_by_me=Exists(liked_subquery),
        annotated_replies_count=Count('replies', filter=Q(replies__status='published'))
    ).first()

    return JsonResponse({
        'success': True,
        'reply': _serialize_comment(reply),
        'parent_id': parent_comment.id
    })


@require_POST
def toggle_comment_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    session_key = _session_key(request)

    like = CommentLike.objects.filter(comment=comment, session_key=session_key).first()
    if like:
        like.delete()
        comment.likes_count = max(0, comment.likes_count - 1)
        comment.save(update_fields=['likes_count'])
        liked = False
    else:
        CommentLike.objects.create(comment=comment, session_key=session_key)
        comment.likes_count += 1
        comment.save(update_fields=['likes_count'])
        liked = True

    return JsonResponse({
        'liked': liked,
        'likes_count': comment.likes_count
    })


@require_POST
def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    reason = request.POST.get('reason', 'other').strip()
    session_key = _session_key(request)

    valid_reasons = ['spam', 'inappropriate', 'harassment', 'other']
    if reason not in valid_reasons:
        reason = 'other'

    already_reported = ReportedComment.objects.filter(
        comment=comment,
        session_key=session_key
    ).exists()

    if already_reported:
        return JsonResponse({'success': False, 'error': 'Déjà signalé.'}, status=400)

    ReportedComment.objects.create(
        comment=comment,
        reason=reason,
        session_key=session_key
    )

    return JsonResponse({'success': True})


def load_comments(request, slug):
    article = get_object_or_404(Article, slug=slug)
    session_key = _session_key(request)

    page = int(request.GET.get('page', 1))
    sort = request.GET.get('sort', 'newest')
    search = request.GET.get('q', '').strip()
    offset = (page - 1) * COMMENTS_PER_PAGE

    comments_qs = Comment.objects.filter(
        article=article,
        status='published',
        parent=None
    ).select_related('article', 'article__author', 'subscriber')

    if search:
        comments_qs = comments_qs.filter(content__icontains=search)

    if sort == 'oldest':
        comments_qs = comments_qs.order_by('created_date')
    elif sort == 'popular':
        comments_qs = comments_qs.order_by('-likes_count')
    else:
        comments_qs = comments_qs.order_by('-created_date')

    liked_subquery = CommentLike.objects.filter(
        comment=OuterRef('pk'),
        session_key=session_key
    )
    comments_qs = comments_qs.annotate(
        likes_total=Count('likes', distinct=True),
        is_liked_by_me=Exists(liked_subquery),
        annotated_replies_count=Count('replies', filter=Q(replies__status='published'))
    )

    comments = list(comments_qs[offset:offset + COMMENTS_PER_PAGE])
    has_more = len(comments) == COMMENTS_PER_PAGE

    comments_data = [_serialize_comment(c) for c in comments]

    return JsonResponse({
        'comments': comments_data,
        'has_more': has_more,
        'next_page': page + 1 if has_more else None
    })


def load_replies(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, parent=None)
    session_key = _session_key(request)

    replies = Comment.objects.filter(
        parent=comment,
        status='published'
    ).select_related('article', 'article__author', 'subscriber')

    liked_subquery = CommentLike.objects.filter(
        comment=OuterRef('pk'),
        session_key=session_key
    )
    replies = replies.annotate(
        likes_total=Count('likes', distinct=True),
        is_liked_by_me=Exists(liked_subquery),
        annotated_replies_count=Count('replies', filter=Q(replies__status='published'))
    ).order_by('created_date')

    replies_data = [_serialize_comment(r) for r in replies]

    return JsonResponse({
        'replies': replies_data,
        'parent_id': comment_id
    })


def get_comments_preview(request, slug):
    article = get_object_or_404(Article, slug=slug)
    session_key = _session_key(request)

    comments_qs = Comment.objects.filter(
        article=article,
        status='published',
        parent=None
    ).select_related('article', 'article__author', 'subscriber')[:COMMENTS_PREVIEW_COUNT]

    liked_subquery = CommentLike.objects.filter(
        comment=OuterRef('pk'),
        session_key=session_key
    )
    comments_qs = comments_qs.annotate(
        likes_total=Count('likes', distinct=True),
        is_liked_by_me=Exists(liked_subquery),
        annotated_replies_count=Count('replies', filter=Q(replies__status='published'))
    )

    total_count = Comment.objects.filter(
        article=article,
        status='published',
        parent=None
    ).count()

    comments_data = [_serialize_comment(c) for c in comments_qs]

    return JsonResponse({
        'comments': comments_data,
        'total_count': total_count,
        'show_view_all': total_count > COMMENTS_PREVIEW_COUNT
    })


def _serialize_comment(comment):
    return {
        'id': comment.id,
        'name': comment.display_name,
        'content': comment.content,
        'likes_count': comment.likes_count,
        'likes_total': getattr(comment, 'likes_total', comment.likes_count),
        'is_liked_by_me': getattr(comment, 'is_liked_by_me', False),
        'replies_count': getattr(comment, 'annotated_replies_count', comment.replies_count),
        'created_date': comment.created_date.strftime('%d %b %Y'),
        'is_article_author': comment.is_article_author(),
        'parent_id': comment.parent_id,
    }


def confirm_subscription(request, token):
    from django.shortcuts import redirect
    from django.contrib import messages

    subscriber = get_object_or_404(ArticleSubscriber, confirmation_token=token)

    if subscriber.token_expires_at and subscriber.token_expires_at < timezone.now():
        messages.error(request, "Ce lien de confirmation a expiré. Veuillez vous réinscrire.")
        return redirect('article_list')

    subscriber.confirm()
    request.session['confirmed_email'] = subscriber.email
    messages.success(request, "Votre inscription est confirmée ! Vous pouvez maintenant publier des commentaires.")

    next_url = request.GET.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('article_list')


def unsubscribe(request, token):
    from django.shortcuts import redirect
    from django.contrib import messages

    subscriber = get_object_or_404(ArticleSubscriber, unsubscribe_token=token)
    subscriber.unsubscribe()
    if request.session.get('confirmed_email') == subscriber.email:
        del request.session['confirmed_email']
    messages.success(request, "Vous avez été désabonné de la newsletter.")

    next_url = request.GET.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('article_list')


@require_POST
def subscribe_newsletter(request):
    import re
    email = request.POST.get('email', '').strip()
    name = request.POST.get('name', '').strip()

    if not email:
        return JsonResponse({'success': False, 'error': 'Email requis.'}, status=400)
    if not name:
        return JsonResponse({'success': False, 'error': 'Nom requis.'}, status=400)

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return JsonResponse({'success': False, 'error': 'Adresse email invalide.'}, status=400)

    disposable_domains = [
        'tempmail.com', 'throwaway.email', 'guerrillamail.com', 'mailinator.com',
        '10minutemail.com', 'fakeinbox.com', 'trashmail.com', 'yopmail.com',
        'temp-mail.org', 'getnada.com', 'maildrop.cc', 'mohmal.com',
    ]
    email_domain = email.split('@')[1].lower() if '@' in email else ''
    if email_domain in disposable_domains:
        return JsonResponse({
            'success': False,
            'error': 'Les adresses email temporaires ne sont pas acceptées. Veuillez utiliser une adresse permanente.'
        }, status=400)

    subscriber = _get_or_create_subscriber(email, name)

    if subscriber.is_confirmed():
        return JsonResponse({'success': True, 'already_confirmed': True, 'message': 'Vous êtes déjà abonné et confirmé.'})

    email_sent = _send_confirmation_email(subscriber, request=request)
    if not email_sent:
        return JsonResponse({
            'success': False,
            'error': "Impossible d'envoyer l'email de confirmation. Vérifiez que votre adresse email est correcte."
        }, status=500)

    return JsonResponse({'success': True, 'message': 'Un email de confirmation a été envoyé.'})
