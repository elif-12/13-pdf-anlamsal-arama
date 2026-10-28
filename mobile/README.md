# PDF Semantic Search — Android (Flutter)

Bu klasordeki Flutter uygulamasi, ana projenin backend'ini (`main.py`) ve
mevcut web arayuzunu (`ui.html`) bir WebView icinde acan ince bir Android
istemcisidir. Yani PDF yukleme, anlamsal arama, sayfaya atlama ve vurgulama
ozellikleri telefon tarafinda da aynen calisir — ayri bir uygulama mantigi
yazilmadi, zaten calisan web arayuzu mobilde gosteriliyor.

> Not: Bu proje yazilirken bu ortamda Flutter SDK kurulu degildi, dolayisiyla
> asagidaki `android/` native iskeleti burada `flutter create` ile
> **uretilmedi** — kasten. El ile yazilmis bir Gradle/Android Manifest
> iskeleti, Flutter/Gradle surum uyumsuzluklarina karsi kirilgan olurdu. Bu
> yuzden `lib/` ve `pubspec.yaml` hazir; `android/` klasorunu senin kuracagin
> Flutter SDK, kendi suruculerine uygun sekilde uretecek.

## Kurulum

### 1. Flutter SDK'yi kur
https://docs.flutter.dev/get-started/install adresinden kur, ardindan:
```bash
flutter doctor
```
Android toolchain'in (Android SDK, bir emulator veya bagli telefon) hazir
oldugunu dogrula.

### 2. Native Android iskeletini uret
Bu klasorde (`mobile/`):
```bash
flutter create --platforms=android .
```
Bu komut mevcut `pubspec.yaml` ve `lib/`'e dokunmadan sadece eksik olan
`android/` klasorunu olusturur (Flutter bilinen dosyalari `--overwrite`
verilmedigi surece ezmez). Komut bittikten sonra `git status` ile sadece
`android/` altinda yeni dosyalar goruyor olman gerekir — `lib/main.dart`
degismemis olmali. Degismisse `git checkout -- lib/ pubspec.yaml` ile geri al.

### 3. AndroidManifest.xml'i duzenle
`android/app/src/main/AndroidManifest.xml` acip iki degisiklik yap:

**a)** `<manifest>` etiketinin icine (uygulama disariyla (backend'le) HTTP
uzerinden konusacagi icin internet izni gerekir):
```xml
<uses-permission android:name="android.permission.INTERNET" />

<queries>
    <intent>
        <action android:name="android.intent.action.GET_CONTENT" />
        <data android:mimeType="*/*" />
    </intent>
</queries>
```

**b)** `<application ...>` etiketine `android:usesCleartextTraffic="true"`
ekle (backend'imiz HTTPS degil, duz HTTP; Android 9+ varsayilan olarak bunu
engeller):
```xml
<application
    android:label="pdf_semantic_search_mobile"
    android:usesCleartextTraffic="true"
    ...>
```

Bu iki degisiklik olmadan uygulama backend'e hic baglanamaz / dosya
yukleme dosya secici acamaz.

### 4. Backend'i disaridan erisilebilir yap
Ana proje klasorunde (`pdf-semantic-search/`, `mobile/` degil):
```bash
venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```
`--host 0.0.0.0` sart: varsayilan `127.0.0.1` sadece bilgisayarin kendisinden
erisime acar, emulator veya telefon bunu goremez.

### 5. Bagimliliklari kur ve calistir
```bash
cd mobile
flutter pub get
flutter run
```
Bir Android emulator acik olmali (Android Studio > Device Manager) veya USB
ile bagli, "Geliştirici modu" acik bir telefon.

## Backend adresi
Varsayilan adres `http://10.0.2.2:8000` — bu, **Android emulator'un**
kendisini calistiran bilgisayarin `localhost`'una ulasmak icin kullandigi
ozel adrestir, gercek telefonda calismaz.

Gercek bir telefonda test ediyorsan:
1. Bilgisayarinin yerel ag IP'sini ogren (`ipconfig` → IPv4 Address, orn.
   `192.168.1.23`).
2. Telefon ile bilgisayar **ayni WiFi** agında olmali.
3. Uygulamada sag ustteki disli (ayarlar) ikonuna dokun, adresi
   `http://192.168.1.23:8000` seklinde degistir ve kaydet.

## Neden WebView ve tam native arayuz degil?
Web arayuzu (`ui.html`) zaten PDF goruntuleme (pdf.js), sayfaya atlama ve
eslesen metni vurgulama dahil tam ozellikli ve test edilmis durumda. Bunu
native Flutter widget'lariyla (PDF render, metin katmani vurgulama) yeniden
yazmak hem cok daha fazla kod hem de bu ortamda derleyip test edemedigim
icin yuksek hata riski demek. WebView sarmalayici, ayni deneyimi dusuk
riskle ve az kodla telefona tasir. Ileride gercek native bir arayuz istenirse
bu ayri bir is olarak ele alinabilir.
