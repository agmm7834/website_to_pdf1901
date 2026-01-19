# Web to PDF Converter

Veb-sahifalarni PDF formatiga o'giradigan va debug ma'lumotlarini saqlaydigan Python skript.

## O'rnatish

```bash
pip install playwright
playwright install chromium
```

## Ishlatish

```bash
python main.py "URL" -o natija.pdf
```

**Misol:**
```bash
python main.py "https://example.com" -o sahifa.pdf
```

## Natija

Skript quyidagi fayllarni yaratadi:

- **PDF fayl** - asosiy natija
- **_debug.png** - sahifaning to'liq screenshot
- **_debug.html** - sahifa HTML kodi
- **_debug.log** - barcha debug loglar

## Xususiyatlar

- Screen CSS bilan PDF yaratish (print media emas)
- Lazy-load rasmlar uchun avtomatik scroll
- Barcha console/error loglarini saqlash
- To'liq sahifa screenshot
- Network timeout handling
