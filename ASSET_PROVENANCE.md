# Varlık Kaynak Kaydı

Bu kayıt, yayımlanan sürümdeki görsel ve yazılım varlıklarının kökenini açıklar.

## Özgün proje varlıkları

- `dist/models/*.glb`: `tools/generate_original_assets.py` ile temel geometrilerden
  bu proje için prosedürel olarak üretilmiştir. Üçüncü taraf model, doku veya
  fotoğraf içermez.
- `dist/assets/*.svg`: aynı üretici betik tarafından bu proje için çizilmiştir.
  Üçüncü taraf ikon veya çizim paketi içermez.
- Türkçe metin ve arayüz kodu bu proje için hazırlanmıştır.
- `dist/assets/logo.png`: iotfyedu tarafından sağlanan marka varlığıdır.

## Üçüncü taraf yazılım

- `<model-viewer>` 4.3.1 — Google tarafından Apache License 2.0 altında
  yayımlanır. Dağıtım dosyası `dist/assets/model-viewer.min.js` içinde yerel
  olarak barındırılır. Lisans: https://github.com/google/model-viewer/blob/master/LICENSE

## Yeniden üretim

```sh
python3 tools/generate_original_assets.py
```

Betik yalnızca Python standart kütüphanesini kullanır.
