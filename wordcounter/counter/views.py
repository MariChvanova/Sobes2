
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
import re
from .models import WordCount


def home(request):
    return render(request, 'counter/home.html')


def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name

        # Сохраняем файл временно
        path = default_storage.save(f'tmp/{file_name}', ContentFile(uploaded_file.read()))

        try:
            with default_storage.open(path) as f:
                content = f.read().decode('utf-8')
                words = re.findall(r'\b[а-яА-Яa-zA-Z]+\b', content)

                # Удаляем старые записи для этого файла
                WordCount.objects.filter(file_name=file_name).delete()

                # Создаем новые записи
                word_counts = {}
                for word in words:
                    word_lower = word.lower()
                    word_counts[word_lower] = word_counts.get(word_lower, 0) + 1

                WordCount.objects.bulk_create([
                    WordCount(word=word, count=count, file_name=file_name)
                    for word, count in word_counts.items()
                ])

            return JsonResponse({'status': 'success', 'message': f'Файл {file_name} успешно обработан'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        finally:
            default_storage.delete(path)

    return JsonResponse({'status': 'error', 'message': 'Не получен файл'}, status=400)


def get_word_count(request):
    word = request.GET.get('word', '').strip().lower()
    if not word or not word.isalpha():
        return JsonResponse({'status': 'error', 'message': 'Некорректное слово'}, status=400)

    count = WordCount.objects.filter(word=word).aggregate(total=models.Sum('count'))['total'] or 0
    return JsonResponse({'status': 'success', 'count': count, 'word': word})


def clear_memory(request):
    if request.method == 'POST':
        WordCount.objects.all().delete()
        return JsonResponse({'status': 'success', 'message': 'Данные очищены'})
    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'}, status=400)
# Create your views here.
