from django.shortcuts import render, redirect
from .forms import UserDetailsForm

def user_details_view(request):
    if request.method == 'POST':
        form = UserDetailsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # Редирект на страницу успеха
    else:
        form = UserDetailsForm()

    return render(request, 'details/user_details_form.html', {'form': form})

# detail/views.py

def success_page(request):
    return render(request, 'success.html')
