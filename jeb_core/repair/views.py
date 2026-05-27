from django.shortcuts import render, redirect
from .forms import RepairForm
from django.contrib import messages

def RepairView(request):
    if request.method == 'POST':
        print('koko')
        form = RepairForm(request.POST, request.FILES, user=request.user )
        if form.is_valid():
            print('провалилось')
            repair_request = form.save(commit=False)
            if request.user.is_authenticated:
                repair_request.user = request.user
            repair_request.save()
            messages.success(request, 'Ваш заказ был успешно передан в обработку! Ожидайте.')
            return redirect('users:profile')

    else:
        print('kok')
        form = RepairForm(user=request.user)
    return render(request, 'repair/repair_form.html', {'form' : form})
