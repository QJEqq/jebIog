from django.shortcuts import render, redirect
from .forms import RepairForm
from django.contrib import messages
from auth.notification import send_telegram
def RepairView(request):
    if request.method == 'POST':
  
        form = RepairForm(request.POST, request.FILES, user=request.user )
        if form.is_valid():

            repair_request = form.save(commit=False)
            if request.user.is_authenticated:
                repair_request.user = request.user
            repair_request.save()
            send_telegram(repair_request)
            messages.success(request, 'Ваш заказ был успешно передан в обработку! Ожидайте.')
            return redirect('users:profile')

    else:
        form = RepairForm(user=request.user)
    return render(request, 'repair/repair_form.html', {'form' : form})
