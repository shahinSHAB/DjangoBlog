from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils.translation import activate
from django.core.mail import send_mail

from .models import Blog, Category
from .forms import BLogForm, CategoryForm, ProfileForm, SharePostForm
from . import mixins


# =========== Blog Articles ===========
class ArticleListView(generic.ListView):
    template_name = "blog/article_list.html"
    context_object_name = 'articles'
    paginate_by = 5
    
    def get_queryset(self):
        """returns blog objects with publish status

        Returns:
            Queryset: list of published articles
        """
        search_param = self.request.GET.get('q')
        default_query = Blog.objects.published().select_related('author').prefetch_related('category', 'hits')
        if search_param:
            return get_list_or_404(default_query.filter(
                Q(title__icontains=search_param) | Q(content__icontains=search_param)))
        else:
            return get_list_or_404(default_query)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.active().filter(parent=None)
        return context
    

# =========== Blog Article Detail ===========
class ArticleDetailView(generic.DetailView):
    template_name = "blog/article_detail.html"
    context_object_name = 'article'
       
    def get_queryset(self):
        """returns blog objects with publish status

        Returns:
            Queryset: list of published articles
        """
        return Blog.objects.published().select_related('author').prefetch_related('category', 'hits')
    
    def get_object(self):
        """returns one blog object with hits, every time 
        new client with new ip watch article,one
        number add to the view and one new ip add to hits. 

        Returns:
            object: one article of blog articles
        """
        obj_slug=self.kwargs.get('slug')
        obj = get_object_or_404(self.get_queryset(),slug=obj_slug)
        client_ip = self.request.user.ip_address
        if client_ip not in obj.hits.all():
            obj.hits.add(client_ip)
            obj.view+=1
            obj.save()
        else:
            pass
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.active().filter(parent=None)
        return context


# ============= All Articles ================
class AllArticlesView(LoginRequiredMixin, mixins.SuperUserOrAuthorAccessMixin , generic.ListView):
    template_name = "admin_panel/index.html"
    context_object_name = 'articles'
    
    def get_queryset(self):
        """returns all blog objects with any status if user is superuser.
        
        if user is author returns only blog objects that their authors are this user.
        """
        user = self.request.user
        if user.is_superuser:
            return Blog.objects.all().select_related('author').prefetch_related('category')
        elif user.is_author:
            return Blog.objects.filter(author=user).select_related('author').prefetch_related('category')


# ========== Create Article ============
class ArticleCreateView(LoginRequiredMixin, mixins.SuperUserOrAuthorAccessMixin, mixins.FormValidMixin, SuccessMessageMixin, generic.CreateView):
    model = Blog
    template_name = "admin_panel/article_create.html"
    form_class = BLogForm
    success_url = reverse_lazy('blog:panel')
    success_message = 'Article was created successfully'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


# ==========  Update Article ============
class ArticleUpdateView(LoginRequiredMixin, mixins.SuperUserOrOwnerDraftAccessMixin, SuccessMessageMixin, generic.UpdateView):
    model = Blog
    template_name = "admin_panel/article_update.html"
    context_object_name = 'article'
    form_class = BLogForm
    success_url = reverse_lazy('blog:panel')
    success_message = 'Article was updated successfully'
    
    def get_object(self):
        obj_slug = self.kwargs.get('slug')
        return get_object_or_404(self.model, slug=obj_slug)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


# ============ Delete Article =============
class ArticleDeleteView(LoginRequiredMixin, mixins.SuperUserOrOwnerDraftAccessMixin, SuccessMessageMixin, generic.DeleteView):
    model = Blog
    context_object_name = 'article'
    template_name = "admin_panel/article_delete.html"
    success_url = reverse_lazy('blog:panel')
    success_message = 'Article was deleted successfully'
    
    def get_object(self):
        obj_slug = self.kwargs.get('slug')
        return get_object_or_404(self.model, slug=obj_slug)


# ========== Create Category ============
class CategoryCreateView(LoginRequiredMixin, mixins.SuperUserOrAuthorAccessMixin, SuccessMessageMixin, generic.CreateView):
    model = Category
    template_name = "admin_panel/category_create.html"
    form_class = CategoryForm
    success_url = reverse_lazy('blog:panel')
    success_message = 'Category was created successfully'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user':self.request.user})
        return kwargs


# ========== Update Category ============
class CategoryUpdateView(LoginRequiredMixin, mixins.SuperUserOrAuthorAccessMixin, SuccessMessageMixin, generic.UpdateView):
    model = Category
    template_name = "admin_panel/category_update.html"
    form_class = CategoryForm
    success_url = reverse_lazy('blog:panel')
    success_message = 'Category was updated successfully'
    
    def get_object(self):
        obj_slug = self.kwargs.get('slug')
        return get_object_or_404(self.model, slug=obj_slug)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


# ========== Delete Category ============
class CategoryDeleteView(LoginRequiredMixin, mixins.SuperUserAccessMixin, SuccessMessageMixin, generic.DeleteView):
    model = Category
    template_name = "admin_panel/category_delete.html"
    success_url = reverse_lazy('blog:panel')
    success_message = 'Category was deleted successfully'

    def get_object(self):
        obj_slug = self.kwargs.get('slug')
        return get_object_or_404(self.model, slug=obj_slug)


# ========== Category's Articles ============
class CategoryArticlesView(generic.ListView):
    template_name = 'blog/category_articles.html'
    context_object_name = 'articles'
    paginate_by = 5
    
    def get_queryset(self):
        return get_list_or_404(self.get_object().blog_set.published())
    
    def get_object(self):
        obj_slug = self.kwargs.get('slug')
        return get_object_or_404(Category.objects.active(), slug=obj_slug)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_object()
        return context
    

# ============ Articles Period ==============
class ArticlesPeriodView(generic.ListView):
    template_name = 'blog/articles_period.html'
    context_object_name = 'articles'
    paginate_by = 5
    
    def get_queryset(self):
        q_set = Blog.objects.published()
        q_param = self.kwargs.get('slug')
        last_month = timezone.now() - timedelta(days=30)
        last_week = timezone.now() - timedelta(days=7)
        last_day = timezone.now() - timedelta(days=1)
        if q_param == 'last-month':
            return get_list_or_404(q_set, publish__gt=last_month)
        elif q_param == 'last-week':
            return get_list_or_404(q_set, publish__gt=last_week)
        elif q_param == 'last-day':
            return q_set.filter(publish__gt=last_day)
        elif q_param == 'last-five-articles':
            return q_set[:5]
        else:
            raise Http404

        
# ============ Most Viewed Articles ==============
class MostViewedArticlesView(generic.ListView):
    template_name = 'blog/most_viewed_articles.html'
    context_object_name = 'articles'
    paginate_by = 5
    
    def get_queryset(self):
        q_set = Blog.objects.published().order_by('-view')
        q_param = self.kwargs.get('slug')
        last_month = timezone.now() - timedelta(days=30)
        last_week = timezone.now() - timedelta(days=7)
        last_day = timezone.now() - timedelta(days=1)
        if q_param == 'last-month':
            return get_list_or_404(q_set, publish__gt=last_month)
        elif q_param == 'last-week':
            return get_list_or_404(q_set, publish__gt=last_week)
        elif q_param == 'last-day':
            return q_set.filter(publish__gt=last_day)
        elif q_param == 'last-five-articles':
            return q_set[:5]
        else:
            raise Http404
        
        
# ============ Profile Detail View ==============
class ProfileDetailView(LoginRequiredMixin, SuccessMessageMixin, generic.DetailView):
    template_name = 'blog/profile/profile.html'
    context_object_name = 'user'
    
    def get_object(self):
        obj_username = self.request.user.username
        return get_object_or_404(get_user_model().objects.active_users(), username=obj_username)
    
    
# ============ Profile Update View ==============
class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin,  generic.UpdateView):
    template_name = 'blog/profile/profile_update.html'
    form_class = ProfileForm
    success_message = 'Profile was updated successfully'
    
    def get_success_url(self):
        return reverse_lazy('blog:profile_detail')
        
    def get_object(self):
        obj_username = self.request.user.username
        return get_object_or_404(get_user_model().objects.active_users(), username=obj_username)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user':self.request.user})
        return kwargs
        

# ============ Author Information View ==============
class AuthorInformationView(generic.DetailView):
    template_name = 'blog/author.html'
    context_object_name = 'author'
    queryset = get_user_model().objects.author_users()
    
    def get_object(self):
        obj_username = self.kwargs.get('username')
        return get_object_or_404(self.queryset, username=obj_username)
    
    def get_context_data(self, **kwargs):
        """returns author's published articles
        """
        context = super().get_context_data(**kwargs)
        context['articles'] = self.get_object().blog_set.published()
        return context
    
    
# ============ Article PreView View ==============
class ArticlePreView(LoginRequiredMixin, mixins.SuperUserOrOwnerAccessMixin, generic.DetailView):
    model = Blog
    template_name = 'admin_panel/preview.html'
    context_object_name = 'article'


# ============================= Share Post View ===========================
class SharePostView(LoginRequiredMixin, SuccessMessageMixin, generic.FormView, generic.DetailView):
    form_class = SharePostForm
    success_message = 'post successfully shared'
    template_name = 'blog/share_post.html'

    def get_queryset(self):
        return Blog.objects.published()

    def get_object(self):
        obj = self.get_queryset().get(slug=self.kwargs.get('slug'))
        return obj

    def get_success_url(self):
        slug = self.get_object().slug
        return reverse_lazy('blog:detail', kwargs={'slug':slug})

    def form_valid(self, form):
        cd = form.cleaned_data
        user_message = cd['message']
        to_email = cd['email']
        obj = self.get_object()
        obj_url = self.request.build_absolute_uri(reverse_lazy('blog:detail',
                                                    kwargs={'slug':obj.slug})
                                                )
        user_name = self.request.user.username
        subject = f'Blog {obj.title}'
        message = f'user {user_name} send this mail for you: \n \
                    link of post is : {obj_url} \n {user_message}'
        from_ = 'someaccount@gmail.com'
        send_mail(subject, message, from_, [to_email])
        return super().form_valid(form)


# ============ Change Language ==============
class ChangeLanguageView(generic.RedirectView):

    def get(self, request, *args, **kwargs):
        language_code = request.GET.get('lang')
        activate(language_code)
        return self.get_redirect_url(*args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return redirect(self.request.GET.get('next'))
