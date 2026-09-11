---
title: دليل استخدام النظام الوزاري — كيف تستخدمه فعلياً؟
type: guide
language: arabic
created: 2026-09-11
updated: 2026-09-11
version: "1.0"
tags: [cabinet-office, guide, usage, tutorial]
status: published
---

# دليل الاستخدام العملي — كيف تستخدم النظام من داخل Hermes؟

> [!ABSTRACT]
> هذا الدليل يشرح كيفية استخدام النظام الوزاري متعدد الوكلاء من داخل محادثة Hermes Agent.

---

## الطريقة 1: من داخل محادثة Hermes (الطريقة الأسهل)

أنت الآن تتحدث مع `@deep-dive` (بوت البحث في يوتيوب).

لاستخدام النظام الوزاري، اكتب ببساطة:

### 1. البحث عبر @omni-researcher

```bash
"ابحث لي عن [موضوعك]"
```

هذا يُفعّل `@omni-researcher` ويبحث في:
- الويب
- تويتر/إكس
- ريديت
- أخبار

### 2. البحث في يوتيوب عبر @deep-dive

```bash
"ابحث لي في يوتيوب عن [موضوعك]"
```

هذا يُفعّل `@deep-dive` ويبحث في فيديوهات يوتيوب ويقرأ النصوص.

### 3. الكتابة عبر @draft-writer

```bash
"اكتب لي مقال عن [موضوعك]"
```

هذا يُفعّل `@draft-writer` ويكتب مقال كامل.

### 4. التحقق من الجودة عبر @editor-qa

```bash
"تحقق من هذا النص: [النص]"
```

### 5. النشر عبر @publisher

```bash
"انشر هذا المقال في [المكان]"
```

---

## الطريقة 2: استخدام الوكلاء مباشرة (الطريقة المباشرة)

كل وكيل هو "بروفايل" داخل Hermes. لتفعيله:

### 1. كتابة مهمة لوكيل محدد

```bash
# اكتب في محادثة Hermes:
"@omni-researcher: ابحث عن تأثير AI على التعليم"

# أو:
"@strategist: ابنِ خطة لكتابة مقال عن البرمجة"

# أو:
"@editor-qa: تحقق من صحة هذه المعلومات..."
```

### 2. تسلسل العمل (Pipeline)

```bash
# الخطوة 1: البحث
"@omni-researcher: ابحث عن آخر أخبار العملات الرقمية"

# الخطوة 2: الاستراتيجية
"@strategist: حول نتائج البحث لخطة استثمارية"

# الخطوة 3: الكتابة
"@draft-writer: اكتب تقرير مبني على الخطة"

# الخطوة 4: التحقق
"@editor-qa: تحقق من كل ادعاء في التقرير"

# الخطوة 5: النشر
"@publisher: انشر التقرير في vault"
```

---

## الطريقة 3: واجهة التشغيل الموحدة (12 أمر)

```bash
# مهمة بسيطة (المنظّم فقط)
python3 ~/.hermes/system/cabinet-office.py run "ما هي أفضل ممارسات SEO؟"

# بحث سريع (الباحث + الناشر)
python3 ~/.hermes/system/cabinet-office.py run "ابحث عن تأثير AI على التعليم" --tier tier_1

# استراتيجية كاملة (5 وكلاء)
python3 ~/.hermes/system/cabinet-office.py run "اكتب مقالة عن مستقبل البرمجة" --tier tier_2

# تحليل شامل (8 وكلاء)
python3 ~/.hermes/system/cabinet-office.py run "حلل سوق العملات الرقمية 2026" --tier tier_3

# فحص حالة النظام
python3 ~/.hermes/system/cabinet-office.py status

# فحص الجودة
python3 ~/.hermes/system/cabinet-office.py quality

# فحص الميزانية
python3 ~/.hermes/system/cabinet-office.py budget

# استخلاص الدروس
python3 ~/.hermes/system/cabinet-office.py learn --mission m001
```

---

## الطريقة 4: السكريبتات الفردية (17 سكريبت)

```bash
# قاطع الدائرة
python3 ~/.hermes/system/scripts/circuit-breaker.py --status

# المراقبة
python3 ~/.hermes/system/scripts/watchdog.py

# التوجيه الديناميكي
python3 ~/.hermes/system/scripts/dynamic-router.py --task "اكتب مقالة عن AI"

# بوابة الجودة
python3 ~/.hermes/system/scripts/quality-gate.py --check output.md

# التعلم الذاتي
python3 ~/.hermes/system/scripts/self-learning.py --extract mission-report.json

# معايير الموثوقية
python3 ~/.hermes/system/scripts/reliability-standards.py
```

---

## شرح المستويات الأربعة (Tier System)

### Tier 0 — قرار فوري (~11 ثانية)
- **الوكلات:** المنظّم فقط
- **متى تستخدمه:** أسئلة بسيطة، قرارات سريعة
- **مثال:** "ما هي عاصمة اليابان؟"

### Tier 1 — بحث سريع (~44 ثانية)
- **الوكلات:** الباحث ← الناشر
- **متى تستخدمه:** تحتاج معلومات سريعة
- **مثال:** "ما آخر أخبار SpaceX؟"

### Tier 2 — استراتيجية وتدقيق (~2:40 دقيقة)
- **الوكلات:** الباحث ← الاستراتيجي ← الكاتب ← المدقق ← الناشر
- **متى تستخدمه:** كتابة مقال، تقرير، بحث
- **مثال:** "اكتب مقالة عن مستقبل البرمجة"

### Tier 3 — تحليل شامل (~5:20 دقيقة)
- **الوكلات:** كل الـ 8
- **متى تستخدمه:** بحث عميق، تقرير مفصل
- **مثال:** "حلل سوق العملات الرقمية 2026"

---

## دليل الوكلاء — من تسأل ومتى؟

| إذا كنت تريد... | اسأل... | التقني | المستوى |
|---|---|---|---|
| بحث شامل في الإنترنت | @omni-researcher | `research-agent-multi` | Tier 1+ |
| بحث في فيديوهات يوتيوب | @deep-dive | `research-agent-youtube` | Tier 2+ |
| تحويل لفكرة أو خطة | @strategist | `strategy-agent` | Tier 2+ |
| كتابة مقال أو تقرير | @draft-writer | `drafting-agent` | Tier 2+ |
| تحقق من جودة نص | @editor-qa | `qa-agent` | Tier 2+ |
| نشر أو توزيع محتوى | @publisher | `distribution-agent` | Tier 1+ |
| قياس أداء محتوى | @analytics | `analytics-agent` | Tier 3 |
| إنشاء بوت جديد | @bot-maker | `agent-factory` | خاص |
| إصلاح مشكلة في النظام | @omarchy | `system-operator` | خاص |
| مراقبة مصادر | @scout | `source-monitor` | Tier 3 |
| تنسيق المهام المعقدة | @architect | `orchestrator-agent` | الكل |

---

## مثال عملي كامل

### المهمة: "اكتب مقالة عن مستقبل البرمجة"

```bash
# الخطوة 1: تحقق من حالة النظام
python3 ~/.hermes/system/cabinet-office.py status

# الخطوة 2: شغّل المهمة
python3 ~/.hermes/system/cabinet-office.py run "اكتب مقالة عن مستقبل البرمجة 2026" --tier tier_2

# الخطوة 3: تحقق من الجودة
python3 ~/.hermes/system/cabinet-office.py quality

# الخطوة 4: استخلص الدروس
python3 ~/.hermes/system/cabinet-office.py learn --mission m001
```

### أو من داخل محادثة Hermes:

```bash
@omni-researcher: ابحث عن مستقبل البرمجة 2026
@strategist: ابنِ خطة مقال من نتائج البحث
@draft-writer: اكتب مقال مبني على الخطة
@editor-qa: تحقق من كل ادعاء
@publisher: انشر المقال في vault
```

---

## استكشاف الأعطال

| المشكلة | الحل |
|---|---|
| الوكلاء لا يعملون | `python3 ~/.hermes/system/cabinet-office.py heartbeat --check` |
| المخرجات ضعيفة | `python3 ~/.hermes/system/cabinet-office.py quality` |
| التوكنز تنتهي سريعاً | `python3 ~/.hermes/system/cabinet-office.py budget` |
| خطأ في سكريبت | `bash ~/.hermes/setup.sh --verify` |

---

## نصائح الاستخدام الأمثل

### افعل ✅
- استخدم Tier 0 للأسئلة البسيطة
- تحقق من الجودة بعد كل مهمة
- استخلص الدروس من المهام الفاشلة
- حدّث النظام بانتظام: `bash setup.sh --pull`

### لا تفعل ❌
- لا تستخدم Tier 3 للمهام البسيطة (إهدار للموارد)
- لا تتجاوز البوابة البشرية (human gate)
- لا تثق في المخرجات دون التحقق
- لا تنسَ أن المقاييس الحالية دائرية (Circular Validation)

---

> [!INFO] معلومات الدليل
> **الإصدار:** 1.0 | **التاريخ:** 2026-09-11
> **النظام:** Cabinet-Office v1.7.0
> **المكان:** ~/.hermes/system/
> **الأوامر:** 12 أمر رئيسي + 17 سكريبت
> **الوكلاء:** 11 وكيل متخصص
