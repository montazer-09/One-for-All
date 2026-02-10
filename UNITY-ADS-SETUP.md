# دليل إعداد Unity Ads لتطبيق OMNI-OS PRO

## نظرة عامة
تم إعداد تطبيق OMNI-OS PRO لاستخدام Unity Ads SDK 4.12.0 مع دعم كامل لثلاثة أنواع من الإعلانات:
- **Banner Ads**: إعلانات البنر في الأسفل
- **Interstitial Ads**: إعلانات البينية (ملء الشاشة)
- **Rewarded Ads**: إعلانات المكافآت

## التكوين الحالي

### معلومات Unity Ads
- **Game ID**: `6043973`
- **Test Mode**: `false` (وضع الإنتاج)
- **Placement IDs**:
  - Banner: `Banner_Android`
  - Interstitial: `Interstitial_Android`
  - Rewarded: `Rewarded_Android`

## خطوات التفعيل

### 1. تحديث Game ID (مهم جداً!)

قبل النشر، يجب عليك:

1. تسجيل الدخول إلى [Unity Dashboard](https://dashboard.unity3d.com/)
2. إنشاء مشروع جديد أو استخدام مشروع موجود
3. الحصول على Game ID الخاص بك
4. تحديث Game ID في الملفات التالية:

#### في ملف `index.html`:
```javascript
UnityAdsAndroid.initialize('YOUR_GAME_ID', false);
```

#### في ملف `.github/workflows/build-with-ads.yml`:
لا حاجة للتعديل - سيتم استخدام القيمة من index.html

### 2. تكوين Placement IDs

في Unity Dashboard:
1. اذهب إلى **Monetization** → **Placements**
2. أنشئ ثلاثة Placements:
   - `Banner_Android` (نوع: Banner)
   - `Interstitial_Android` (نوع: Interstitial)
   - `Rewarded_Android` (نوع: Rewarded)

إذا كنت تريد استخدام أسماء مختلفة، قم بتحديثها في `index.html`:
```javascript
UnityAdsAndroid.showBanner('YOUR_BANNER_ID');
UnityAdsAndroid.showInterstitial('YOUR_INTERSTITIAL_ID');
UnityAdsAndroid.showRewarded('YOUR_REWARDED_ID');
```

### 3. البناء باستخدام GitHub Actions

1. ارفع الكود إلى GitHub
2. انتقل إلى **Actions** في مستودعك
3. اختر workflow: **OMNI-OS PRO - Unity Ads Production Build**
4. انقر **Run workflow**

سيتم تنفيذ الخطوات التالية تلقائياً:
- إعداد Java 21
- تثبيت Capacitor
- إضافة Unity Ads SDK (v4.12.0)
- إنشاء Native Bridge للتواصل مع JavaScript
- بناء APK

### 4. تنزيل APK

بعد اكتمال البناء:
1. اذهب إلى **Actions** → اختر آخر run
2. انزل **Artifacts**: `OMNI-OS-Pro-UnityAds-Ready`
3. فك ضغط الملف واحصل على `app-debug.apk`

## كيفية عمل الإعلانات

### Banner (البنر)
- يظهر تلقائياً بعد 1 ثانية من التهيئة
- يمكن إخفاؤه/إظهاره من الإعدادات
- يعرض في أسفل الشاشة

### Interstitial (البينية)
- تعرض تلقائياً كل **3 دقائق**
- ملء الشاشة
- يمكن تخطيها بعد 5 ثوان

### Rewarded (المكافآت)
- تعرض تلقائياً كل **5 دقائق**
- تعرض أيضاً عند النقر على ميزات "Premium"
- يجب مشاهدتها كاملة للحصول على المكافأة

## تخصيص التوقيت

لتغيير توقيت عرض الإعلانات، عدّل في `index.html`:

```javascript
// Interstitial كل 3 دقائق (180000 ميلي ثانية)
Ads.interstitialTimer = setInterval(() => {
    Ads.showInterstitial();
}, 3 * 60 * 1000);

// Rewarded كل 5 دقائق (300000 ميلي ثانية)
Ads.rewardedTimer = setInterval(() => {
    Ads.showRewarded();
}, 5 * 60 * 1000);
```

## استكشاف الأخطاء

### الإعلانات لا تظهر

1. **تحقق من Game ID**:
   ```bash
   # ابحث في index.html عن:
   UnityAdsAndroid.initialize('6043973', false);
   ```
   تأكد أنه Game ID الصحيح من Unity Dashboard

2. **تحقق من Placement IDs**:
   - يجب أن تتطابق مع الأسماء في Unity Dashboard
   - حساسة لحالة الأحرف (Case Sensitive)

3. **تحقق من وضع الاختبار**:
   ```javascript
   // للاختبار، استخدم:
   UnityAdsAndroid.initialize('YOUR_GAME_ID', true);

   // للإنتاج، استخدم:
   UnityAdsAndroid.initialize('YOUR_GAME_ID', false);
   ```

4. **تحقق من Logcat**:
   ```bash
   adb logcat | grep UnityAds
   ```
   سترى رسائل مثل:
   - `[Unity Ads] Initialized successfully`
   - `[Banner] Shown`
   - `[Interstitial] Shown`

### تحقق من التهيئة في التطبيق

افتح Chrome DevTools أثناء تشغيل التطبيق:
```bash
chrome://inspect
```

سترى في Console:
- `[Unity Ads] Native bridge detected`
- `[Unity Ads] Initialized successfully`
- `تم تفعيل الإعلانات بنجاح!`

## الأذونات المطلوبة

تمت إضافة الأذونات التالية تلقائياً:
- `android.permission.INTERNET`
- `android.permission.ACCESS_NETWORK_STATE`

## ملاحظات مهمة

1. **Test Mode**:
   - استخدم `true` أثناء التطوير
   - استخدم `false` في الإنتاج

2. **Game ID الحقيقي**:
   - `6043973` هو مثال فقط
   - احصل على Game ID الخاص بك من Unity Dashboard

3. **Fill Rate**:
   - قد لا تظهر الإعلانات في البداية (Fill Rate منخفض)
   - انتظر 24-48 ساعة بعد تفعيل Unity Ads
   - استخدم Test Mode للاختبار الفوري

4. **الدول المدعومة**:
   - تحقق من Unity Dashboard لمعرفة الدول المدعومة
   - بعض الدول لديها Fill Rate أعلى من غيرها

## البنية التقنية

### Native Bridge Architecture

```
┌─────────────────────────────────────┐
│         HTML/JavaScript             │
│    (index.html - Ads Manager)       │
│                                     │
│  UnityAdsAndroid.initialize()       │
│  UnityAdsAndroid.showBanner()       │
│  UnityAdsAndroid.showInterstitial() │
│  UnityAdsAndroid.showRewarded()     │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│      UnityAdsPlugin.java            │
│    (Native Android Bridge)          │
│                                     │
│  @JavascriptInterface               │
│  - initialize()                     │
│  - showBanner()                     │
│  - showInterstitial()               │
│  - showRewarded()                   │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│       Unity Ads SDK 4.12.0          │
│    (com.unity3d.ads:unity-ads)      │
└─────────────────────────────────────┘
```

## الملفات المهمة

1. **index.html**:
   - يحتوي على Ads Manager (JavaScript)
   - Game ID و Placement IDs

2. **.github/workflows/build-with-ads.yml**:
   - GitHub Actions workflow للبناء التلقائي
   - إعداد Unity Ads SDK
   - إنشاء Native Bridge

3. **UnityAdsPlugin.java** (يتم إنشاؤه تلقائياً):
   - الجسر بين JavaScript و Unity Ads SDK
   - يتم إنشاؤه أثناء البناء في GitHub Actions

## الدعم والمساعدة

### Unity Ads Documentation
- [Unity Ads Getting Started](https://docs.unity.com/ads/)
- [Android Integration Guide](https://docs.unity.com/ads/UnityAdsAndroid.html)

### استكشاف المشاكل
- [Unity Ads Troubleshooting](https://docs.unity.com/ads/TroubleshootingGuide.html)
- [Fill Rate Optimization](https://docs.unity.com/ads/OptimizingFillRate.html)

---

## خطوات سريعة للبدء

1. احصل على Game ID من [Unity Dashboard](https://dashboard.unity3d.com/)
2. حدّث Game ID في `index.html`
3. أنشئ Placements في Unity Dashboard
4. ارفع الكود إلى GitHub
5. شغّل GitHub Actions workflow
6. نزّل APK واختبره
7. انشر التطبيق!

**ملاحظة**: لا تنسى تحويل `testMode` إلى `false` قبل النشر النهائي!
