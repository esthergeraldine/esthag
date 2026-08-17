document.addEventListener('DOMContentLoaded', function() {
  const commentsSection = document.getElementById('comments');
  const commentsList = document.getElementById('comments-list');
  const commentsCount = document.getElementById('comments-count');
  const commentsLoading = document.getElementById('comments-loading');
  const commentsEmpty = document.getElementById('comments-empty');
  const viewAllComments = document.getElementById('view-all-comments');
  const commentForm = document.getElementById('comment-form');
  const commentFormError = document.getElementById('comment-form-error');
  const submitBtn = document.getElementById('submit-comment-btn');

  function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
  }

  function csrfToken() {
    return getCookie('csrftoken');
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'fixed top-4 right-4 z-50 space-y-2';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `px-6 py-4 rounded-xl shadow-lg text-sm font-medium ${
      type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' :
      type === 'error' ? 'bg-red-100 text-red-800 border border-red-200' :
      'bg-bg-surface text-text-main border border-border-subtle'
    }`;
    toast.textContent = message;
    toast.style.animation = 'fadeUp 0.3s ease-out';
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  function createCommentElement(comment) {
    const div = document.createElement('div');
    div.className = 'bg-bg-soft rounded-2xl p-5 comment-item';
    div.dataset.commentId = comment.id;

    const avatarInitial = comment.name.charAt(0).toUpperCase();
    const isLikedClass = comment.is_liked_by_me ? 'liked' : '';
    const authorBadge = comment.is_article_author ? '<span class="text-xs bg-accent text-bg-surface px-2 py-0.5 rounded-full ml-2">[Auteur]</span>' : '';

    div.innerHTML = `
      <div class="flex gap-4">
        <div class="w-10 h-10 rounded-full bg-accent-mid flex items-center justify-center flex-shrink-0">
          <span class="text-sm font-medium text-bg-surface">${avatarInitial}</span>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-baseline gap-2 mb-2 flex-wrap">
            <span class="font-semibold text-sm text-text-main">${escapeHtml(comment.name)}</span>
            ${authorBadge}
            <span class="text-xs text-text-muted">${comment.created_date}</span>
          </div>
          <p class="text-sm text-text-main leading-relaxed mb-3">${escapeHtml(comment.content)}</p>
          <div class="flex items-center gap-4">
            <button type="button" class="js-comment-like ${isLikedClass} inline-flex items-center gap-1 text-xs text-text-muted hover:text-accent transition" data-url="/blog/comment/${comment.id}/like/">
              <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="${comment.is_liked_by_me ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
              </svg>
              <span class="js-like-count">${comment.likes_count}</span>
            </button>
            <button type="button" class="js-reply-btn text-xs text-text-muted hover:text-accent transition">Répondre</button>
            <div class="relative">
              <button type="button" class="js-more-btn text-xs text-text-muted hover:text-accent transition p-1">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/></svg>
              </button>
              <div class="js-more-menu hidden absolute right-0 top-full mt-1 bg-bg-surface border border-border-subtle rounded-xl shadow-lg py-2 min-w-[140px] z-10">
                <button type="button" class="js-report-btn w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-bg-soft transition">Signaler</button>
              </div>
            </div>
          </div>
          <div class="js-reply-form hidden mt-4"></div>
          <div class="js-replies-container mt-3"></div>
        </div>
      </div>
    `;

    setupCommentEvents(div);

    if (comment.replies_count > 0) {
      const repliesContainer = div.querySelector('.js-replies-container');
      if (comment.replies_count === 1) {
        loadReplies(comment.id, repliesContainer);
      } else {
        const showRepliesBtn = document.createElement('button');
        showRepliesBtn.type = 'button';
        showRepliesBtn.className = 'js-toggle-replies text-xs text-accent hover:text-accent-dark transition mt-2';
        showRepliesBtn.textContent = `Voir ${comment.replies_count} réponses`;
        showRepliesBtn.dataset.expanded = 'false';
        showRepliesBtn.dataset.commentId = comment.id;
        showRepliesBtn.dataset.repliesCount = comment.replies_count;
        repliesContainer.appendChild(showRepliesBtn);
      }
    }

    return div;
  }

  function createReplyElement(reply) {
    const div = document.createElement('div');
    div.className = 'reply-item ml-6 mt-3 bg-bg-surface/50 rounded-xl p-4';

    const avatarInitial = reply.name.charAt(0).toUpperCase();
    const isLikedClass = reply.is_liked_by_me ? 'liked' : '';
    const authorBadge = reply.is_article_author ? '<span class="text-xs bg-accent text-bg-surface px-2 py-0.5 rounded-full ml-2">[Auteur]</span>' : '';

    div.innerHTML = `
      <div class="flex gap-3">
        <div class="w-8 h-8 rounded-full bg-accent-mid flex items-center justify-center flex-shrink-0">
          <span class="text-xs font-medium text-bg-surface">${avatarInitial}</span>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-baseline gap-2 mb-1 flex-wrap">
            <span class="font-semibold text-sm text-text-main">${escapeHtml(reply.name)}</span>
            ${authorBadge}
            <span class="text-xs text-text-muted">${reply.created_date}</span>
          </div>
          <p class="text-sm text-text-main leading-relaxed">${escapeHtml(reply.content)}</p>
          <div class="flex items-center gap-3 mt-2">
            <button type="button" class="js-comment-like ${isLikedClass} inline-flex items-center gap-1 text-xs text-text-muted hover:text-accent transition" data-url="/blog/comment/${reply.id}/like/">
              <svg class="w-3.5 h-3.5" xmlns="http://www.w3.org/2000/svg" fill="${reply.is_liked_by_me ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
              </svg>
              <span class="js-like-count">${reply.likes_count}</span>
            </button>
          </div>
        </div>
      </div>
    `;

    setupCommentEvents(div);
    return div;
  }

  async function loadReplies(commentId, container) {
    try {
      const response = await fetch(`/blog/comment/${commentId}/replies/`);
      const data = await response.json();

      container.innerHTML = '';
      if (data.replies && data.replies.length > 0) {
        data.replies.forEach(reply => {
          container.appendChild(createReplyElement(reply));
        });
      }
    } catch (error) {
      console.error('Error loading replies:', error);
    }
  }

  function setupCommentEvents(element) {
    const likeBtn = element.querySelector('.js-comment-like');
    if (likeBtn) {
      likeBtn.addEventListener('click', async function() {
        const url = this.dataset.url;
        try {
          const response = await fetch(url, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken() }
          });
          const data = await response.json();

          this.classList.toggle('liked');
          const svg = this.querySelector('svg');
          svg.setAttribute('fill', data.liked ? 'currentColor' : 'none');
          const countSpan = this.querySelector('.js-like-count');
          if (countSpan) countSpan.textContent = data.likes_count;
        } catch (error) {
          console.error('Error toggling like:', error);
        }
      });
    }

    const replyBtn = element.querySelector('.js-reply-btn');
    if (replyBtn) {
      replyBtn.addEventListener('click', function() {
        const replyForm = element.querySelector('.js-reply-form');
        if (replyForm.classList.contains('hidden')) {
          replyForm.classList.remove('hidden');
          replyForm.innerHTML = `
            <form class="reply-form space-y-3">
              <input type="hidden" name="parent_id" value="${element.dataset.commentId}">
              <div class="grid sm:grid-cols-2 gap-3">
                <input type="text" name="name" placeholder="Votre nom" maxlength="100"
                       class="w-full px-3 py-2 rounded-lg bg-bg-surface border border-border-subtle text-text-main text-sm placeholder-text-muted focus:outline-none focus:border-accent transition" required />
                <input type="email" name="email" placeholder="Votre email"
                       class="w-full px-3 py-2 rounded-lg bg-bg-surface border border-border-subtle text-text-main text-sm placeholder-text-muted focus:outline-none focus:border-accent transition" required />
              </div>
              <textarea name="content" rows="3" placeholder="Votre réponse..." maxlength="5000"
                        class="w-full px-3 py-2 rounded-lg bg-bg-surface border border-border-subtle text-text-main text-sm placeholder-text-muted focus:outline-none focus:border-accent transition resize-none" required></textarea>
              <input type="text" name="website" placeholder="" style="position: absolute; left: -9999px; tab-index: -1;">
              <div class="flex items-center gap-2">
                <button type="submit" class="px-4 py-2 bg-accent text-bg-surface rounded-full text-xs font-medium hover:bg-accent-dark transition">Répondre</button>
                <button type="button" class="js-cancel-reply px-4 py-2 text-text-muted hover:text-text-main transition text-xs">Annuler</button>
              </div>
            </form>
          `;

          const cancelBtn = replyForm.querySelector('.js-cancel-reply');
          cancelBtn.addEventListener('click', () => {
            replyForm.classList.add('hidden');
          });

          const formEl = replyForm.querySelector('.reply-form');
          formEl.addEventListener('submit', async function(e) {
            e.preventDefault();
            await submitReply(this, replyForm, element);
          });
        } else {
          replyForm.classList.add('hidden');
        }
      });
    }

    const moreBtn = element.querySelector('.js-more-btn');
    if (moreBtn) {
      moreBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        const menu = this.nextElementSibling;
        document.querySelectorAll('.js-more-menu').forEach(m => {
          if (m !== menu) m.classList.add('hidden');
        });
        menu.classList.toggle('hidden');
      });
    }

    const reportBtn = element.querySelector('.js-report-btn');
    if (reportBtn) {
      reportBtn.addEventListener('click', async function() {
        const commentId = element.dataset.commentId;
        const reason = await showReportModal();
        if (reason) {
          await reportComment(commentId, reason);
        }
        element.querySelector('.js-more-menu').classList.add('hidden');
      });
    }

    const showRepliesBtn = element.querySelector('.js-toggle-replies');
    if (showRepliesBtn) {
      showRepliesBtn.addEventListener('click', function() {
        const repliesContainer = element.querySelector('.js-replies-container');
        const isExpanded = this.dataset.expanded === 'true';
        const repliesCount = parseInt(this.dataset.repliesCount) || 0;

        if (isExpanded) {
          repliesContainer.innerHTML = '';
          this.textContent = `Voir ${repliesCount} réponses`;
          this.dataset.expanded = 'false';
        } else {
          loadReplies(element.dataset.commentId, repliesContainer);
          this.textContent = 'Réduire les réponses';
          this.dataset.expanded = 'true';
        }
      });
    }
  }

  async function submitReply(formEl, replyFormContainer, parentElement) {
    const formData = new FormData(formEl);
    const submitBtnReply = formEl.querySelector('button[type="submit"]');
    submitBtnReply.disabled = true;

    try {
      const response = await fetch('/blog/comment/' + formData.get('parent_id') + '/reply/', {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': csrfToken() }
      });

      const data = await response.json();

      if (data.success) {
        formEl.reset();
        replyFormContainer.classList.add('hidden');

        const repliesContainer = parentElement.querySelector('.js-replies-container');
        const replyElement = createReplyElement(data.reply);
        repliesContainer.appendChild(replyElement);

        const replyCount = parentElement.querySelector('.js-reply-btn');
        if (replyCount) {
          const currentText = replyCount.textContent;
          const match = currentText.match(/(\d+)\s*réponse/);
          if (match) {
            replyCount.textContent = `${parseInt(match[1]) + 1} réponses`;
          }
        }
      } else if (data.needs_confirmation) {
        showToast('Veuillez confirmer votre email pour publier.', 'info');
      } else {
        showToast(data.error || 'Erreur lors de la publication', 'error');
      }
    } catch (error) {
      console.error('Error submitting reply:', error);
      showToast('Erreur lors de la publication', 'error');
    } finally {
      submitBtnReply.disabled = false;
    }
  }

  async function showReportModal() {
    return new Promise((resolve) => {
      const reasons = [
        { value: 'spam', label: 'Spam' },
        { value: 'inappropriate', label: 'Contenu inapproprié' },
        { value: 'harassment', label: 'Harcèlement' },
        { value: 'other', label: 'Autre' }
      ];

      const overlay = document.createElement('div');
      overlay.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50';

      overlay.innerHTML = `
        <div class="bg-bg-surface rounded-2xl p-6 max-w-sm w-full mx-4 shadow-xl">
          <h3 class="font-semibold text-text-main mb-4">Signaler ce commentaire</h3>
          <div class="space-y-2 mb-4">
            ${reasons.map(r => `
              <label class="flex items-center gap-3 p-3 rounded-xl hover:bg-bg-soft cursor-pointer transition">
                <input type="radio" name="reason" value="${r.value}" class="text-accent">
                <span class="text-sm text-text-main">${r.label}</span>
              </label>
            `).join('')}
          </div>
          <div class="flex gap-3">
            <button class="js-confirm-report flex-1 px-4 py-2 bg-red-500 text-white rounded-full text-sm font-medium hover:bg-red-600 transition disabled:opacity-50" disabled>Signaler</button>
            <button class="js-cancel flex-1 px-4 py-2 text-text-muted hover:text-text-main transition text-sm">Annuler</button>
          </div>
        </div>
      `;

      document.body.appendChild(overlay);

      let selectedReason = null;
      const radios = overlay.querySelectorAll('input[name="reason"]');
      radios.forEach(radio => {
        radio.addEventListener('change', function() {
          selectedReason = this.value;
          overlay.querySelector('.js-confirm-report').disabled = false;
        });
      });

      overlay.querySelector('.js-confirm-report').addEventListener('click', () => {
        document.body.removeChild(overlay);
        resolve(selectedReason);
      });

      overlay.querySelector('.js-cancel').addEventListener('click', () => {
        document.body.removeChild(overlay);
        resolve(null);
      });

      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          document.body.removeChild(overlay);
          resolve(null);
        }
      });
    });
  }

  async function reportComment(commentId, reason) {
    try {
      const formData = new FormData();
      formData.append('reason', reason);

      const response = await fetch('/blog/comment/' + commentId + '/report/', {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': csrfToken() }
      });

      const data = await response.json();

      if (data.success) {
        showToast('Commentaire signalé. Merci.');
      } else {
        showToast(data.error || 'Erreur lors du signalement', 'error');
      }
    } catch (error) {
      console.error('Error reporting comment:', error);
      showToast('Erreur lors du signalement', 'error');
    }
  }

  async function fetchCommentsPreview() {
    if (!commentsSection || !commentsList) return;

    const articleSlug = commentsSection.dataset.articleSlug;
    if (!articleSlug) return;

    commentsLoading.classList.remove('hidden');
    commentsEmpty.classList.add('hidden');

    try {
      const response = await fetch(`/blog/${articleSlug}/comments/preview/`);
      const data = await response.json();

      commentsList.innerHTML = '';

      if (data.comments && data.comments.length > 0) {
        data.comments.forEach(comment => {
          commentsList.appendChild(createCommentElement(comment));
        });
        commentsEmpty.classList.add('hidden');
        if (data.show_view_all && viewAllComments) {
          viewAllComments.classList.remove('hidden');
        }
      } else {
        commentsEmpty.classList.remove('hidden');
        if (viewAllComments) viewAllComments.classList.add('hidden');
      }

      if (commentsCount) {
        commentsCount.textContent = data.total_count;
      }
    } catch (error) {
      console.error('Error loading comments:', error);
    } finally {
      commentsLoading.classList.add('hidden');
    }
  }

  if (commentForm) {
    commentForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      commentFormError.classList.add('hidden');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Publication...';

      const formData = new FormData(this);

      try {
        const response = await fetch('/blog/comment/add/', {
          method: 'POST',
          body: formData,
          headers: { 'X-CSRFToken': csrfToken() }
        });

        const data = await response.json();

        if (data.success) {
          commentForm.reset();
          const newComment = createCommentElement(data.comment);
          commentsList.prepend(newComment);

          if (commentsCount) {
            commentsCount.textContent = parseInt(commentsCount.textContent) + 1;
          }

          commentsEmpty.classList.add('hidden');
          if (viewAllComments) viewAllComments.classList.remove('hidden');
        } else if (data.needs_confirmation) {
          const email = formData.get('email');
          if (typeof window.showSubscribeModal === 'function') {
            window.showSubscribeModal(email);
          } else {
            commentFormError.textContent = data.error || 'Veuillez confirmer votre email pour publier.';
            commentFormError.classList.remove('hidden');
          }
        } else {
          commentFormError.textContent = data.error || 'Erreur lors de la publication';
          commentFormError.classList.remove('hidden');
        }
      } catch (error) {
        console.error('Error submitting comment:', error);
        commentFormError.textContent = 'Erreur lors de la publication';
        commentFormError.classList.remove('hidden');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Publier le commentaire';
      }
    });
  }

  document.addEventListener('click', function(e) {
    if (!e.target.closest('.js-more-btn') && !e.target.closest('.js-more-menu')) {
      document.querySelectorAll('.js-more-menu').forEach(menu => {
        menu.classList.add('hidden');
      });
    }
  });

  if (commentsSection && commentsList) {
    fetchCommentsPreview();
  }
});
