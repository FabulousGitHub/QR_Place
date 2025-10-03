from PIL import Image, ImageDraw
import qrcode
import os

def find_empty_corner(image_path, qr_size=(100, 100), margin=20):
    # Загружаем изображение
    image = Image.open(image_path)
    width, height = image.size
    qr_width, qr_height = qr_size
    
    print(f"📐 Размер изображения: {width}x{height}")
    print(f"📏 Размер QR-кода: {qr_width}x{qr_height}")
    
    # Определяем 4 угла с отступами
    corners = [
        (margin, margin),  # верхний левый
        (width - qr_width - margin, margin),  # верхний правый
        (margin, height - qr_height - margin),  # нижний левый
        (width - qr_width - margin, height - qr_height - margin)  # нижний правый
    ]
    
    corner_names = [
        "Верхний левый",
        "Верхний правый", 
        "Нижний левый",
        "Нижний правый"
    ]

    empty_corners = [(None,None),(None,None),(None,None),(None,None)]
    # Проверяем каждый угол на "пустоту"
    for i, (x, y) in enumerate(corners):
        print(f"\n🔍 Проверяем {corner_names[i]} угол: ({x}, {y})")
        
        # Проверяем, что координаты валидны
        if x < 0 or y < 0 or x + qr_width > width or y + qr_height > height:
            print(f"❌ Угол выходит за границы изображения")
            continue
        
        # Проверяем область на однородность (простая проверка)
        if is_area_empty(image, x, y, qr_width, qr_height):
            print(f"✅ {corner_names[i]} угол подходит!")
            empty_corners[i]=corners[i]
        else:
            print(f"❌ {corner_names[i]} угол занят")
    
    # Если ни один угол не подошел
    if empty_corners[0]=="None":
        print("⚠️  Все углы заняты, используем верхний левый угол")
        return corners[0]
    # Выбор сценария пользователем
    else: print("⚠ Выберите свободный угол:\n")
    for i, (x, y) in enumerate(empty_corners):
        if x or y != None:
            print(f'{i}.:{corner_names[i]}\n')
    print("\nЛюбой, нажмите enter")
    scen = input()
    for i, (x, y) in enumerate(empty_corners):
        if scen==str(i):
            return x,y
    

def is_area_empty(image, x, y, width, height, color_variance=50):
    
    # Вырезаем область для проверки
    area = image.crop((x, y, x + width, y + height))
    
    # Конвертируем в RGB если нужно
    if area.mode != 'RGB':
        area = area.convert('RGB')
    
    pixels = list(area.getdata())
    
    if not pixels:
        return True
    
    avg_color = (
        sum(p[0] for p in pixels) // len(pixels),
        sum(p[1] for p in pixels) // len(pixels),
        sum(p[2] for p in pixels) // len(pixels)
    )
    
    color_variations = []
    for pixel in pixels[::10]:  # Проверяем каждый 10-й пиксель для скорости
        variation = sum(abs(pixel[i] - avg_color[i]) for i in range(3))
        color_variations.append(variation)
    
    avg_variation = sum(color_variations) / len(color_variations)
    
    print(f"   Средняя вариация цвета: {avg_variation:.1f}")
    
    # Если средняя вариация меньше порога - считаем область пустой
    return avg_variation < color_variance

def generate_qr_code(data, size=(100, 100)):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_image = qr_image.resize(size, Image.Resampling.LANCZOS)
    
    return qr_image

def place_qr_in_corner(image_path, qr_data, output_path="result.jpg"):
    print("🎨 Начинаем обработку изображения...")
    
    try:
        base_image = Image.open(image_path)
        print(f"✅ Изображение загружено: {image_path}")
    except Exception as e:
        print(f"❌ Ошибка загрузки изображения: {e}")
        return None
    
    qr_position = find_empty_corner(image_path)
    
    # Генерируем QR-код
    qr_image = generate_qr_code(qr_data)
    print("✅ QR-код сгенерирован")
    
    # Создаем копию изображения для размещения QR-кода
    result_image = base_image.copy()
    
    # Добавляем белый фон под QR-код для лучшей читаемости
    white_bg = Image.new('RGB', qr_image.size, 'white')
    mask = Image.new('L', qr_image.size, 255)
    
    # Размещаем QR-код
    result_image.paste(white_bg, qr_position)
    result_image.paste(qr_image, qr_position, mask)
    
    result_image.save(output_path)
    print(f"💾 Результат сохранен: {output_path}")
    print(f"📍 QR-код размещен в позиции: {qr_position}")
    
    return result_image

def create_test_image():
    print("🖼️ Создаем тестовое изображение...")
    
    img = Image.new('RGB', (800, 600), color='lightblue')
    draw = ImageDraw.Draw(img)
    draw.rectangle([650, 10, 790, 150], fill='red', outline='darkred')
    
    draw.ellipse([10, 450, 150, 590], fill='green', outline='darkgreen')

    draw.ellipse([300, 200, 500, 400], fill='orange', outline='darkorange')
    
    # Сохраняем тестовое изображение
    img.save('test_image.jpg')
    print("✅ Тестовое изображение создано: test_image.jpg")
    
    return 'test_image.jpg'

def main():
    test_image_path = 'test_image.jpg'
    qr_data = "https://example.com/invite/unique-code-12345"
    result = place_qr_in_corner('image.jpg', qr_data, "qr_result.jpg")
    
    if result is not None:
        print("\n🎉 Готово! QR-код успешно размещен!")
        
        result_size = result.size
        print(f"📐 Размер итогового изображения: {result_size[0]}x{result_size[1]}")
    else:
        print("\n❌ Произошла ошибка при обработке")

if __name__ == "__main__":
    main()