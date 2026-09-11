<div dir="rtl">

# النظام الوزاري متعدد الوكلاء — ورقة بحثية شاملة

## الملخص

يُقدَّم في هذه الورقة نظام وزاري متعدد الوكلاء (Cabinet-Office Multi-Agent System) مبني على إطار عمل Hermes Agent. يتكون النظام من 11 وكيلاً ذكياً، لكل منهم دور محدد و مخصصة، يعملون معاً ضمن بنية من ثلاث طبقات (دستورية، نظامية، وكيلية) لإنتاج معلومات عالية الجودة مع ضمان التطور الذاتي المستمر. يتميز النظام ببروتوكول تواصل موحد، وديناميكية تحميل العقود حسب حجم نافذة السياق، وحلقة تطور ذاتي آمنة، وبوابة بشرية واحدة للقرارات الحاسمة.

**الكلمات المفتاحية:** نظام متعدد الوكلاء، ذكاء اصطناعي، إدارة المعرفة، التطور الذاتي، بوابة بشرية

---

## 1. المقدمة

### 1.1 المشكلة

تعاني أنظمة الذكاء الاصطناعي الفردية من قيود جوهرية:
- **غياب التخصص:** نموذج واحد لا يمكنه أن يكون خبيراً في البحث والاستراتيجية والكتابة والتحرير والنشر والتحليل في آن واحد.
- **غياب الضبط:** لا يوجد آلية مستقلة للتحقق من جودة المخرجات.
- **غياب الذاكرة:** كل جلسة تبدأ من صفر.
- **غياب التطور:** النظام لا يتعلم من أخطائه.

### 1.2 الحل

نظام وزاري متعدد الوكلاء حيث كل "وزير" مسؤول عن مجال محدد، و"منظّم" (Architect) يدير التواصل بينهم، و"بوابة بشرية" تضمن بقاء الإنسان في الحلقة.

---

## 2. البنية المعمارية (ثلاث طبقات)

### الطبقة الدستورية (مجمدة)
المبادئ الخمسة التي لا تُعدَّل:
1. **طابق قبل أن تعمل** — افهم الموضوع والعمق المطلوب قبل البحث.
2. **الحقيقة المُسمّاة** — كل معلومة تتبع مصدرها بتوقيت زمني.
3. **تأكد من غير القابل للإرجاع** — لا إجراءات مدمرة.
4. **اقرأ قبل أن تكتب** — استرجع النصوص قبل التلخيص.
5. **أبلغ بصراحة** — قدم النتائج بوضوح.

### الطبقة النظامية (قابلة للتعديل عبر بروتوكول التطور)
6 عقود نظامية:
- `registry.json` — سجل الوكلاء
- `protocol.md` — بروتوكول التواصل
- `routing.yaml` — قواعد التوجيه
- `quality-charter.md` — ميثاق الجودة
- `ledger-schema.json` — مخطط دفتر المهام
- `evolution.md` — حلقة التطور

### الطبقة الوكيلية (ملفات SOUL)
11 ملف SOUL، لكل وكيل دوره وأدواته وقيوده.

---

## 3. الوكلاء الأحد عشر

### 3.1 المنظّم (Architect)
- **:** 
- **الدور:** المُنسِّق الوحيد الذي يدير التواصل بين الوكلاء
- **الأدوات:** بحث ويب، استخراج، قراءة/كتابة ملفات، طرفية، رسائل، مهام فرعية، بحث جلسات، جدولة
- **الصلاحيات:** فتح دفتر المهام الجديد، التوجيه بين المستويات، التصعيد للبشر

### 3.2 الباحث الشامل (Omni-Researcher)
- **:** 
- **الدور:** البحث في المصادر الرسمية والأخبار وتويتر وريديت
- **الأدوات:** بحث ويب، استخراج، قراءة ملفات، طرفية، رسائل
- **ينتج:** ملف بحثي (research_dossier)

### 3.3 الغوّاص (Deep-Dive)
- **:** 
- **الدور:** البحث في يوتيوب وتحليل التجارب الشخصية
- **الأدوات:** بحث ويب، استخراج، قراءة ملفات، طرفية، رسائل
- **ينتج:** تلخيص تجارب الفيديو

### 3.4 الاستراتيجي (Strategist)
- **:** 
- **الدور:** تحويل البحث إلى خطة وهيكل
- **الأدوات:** بحث ويب، استخراج، قراءة/كتابة ملفات، رسائل
- **ينتج:** موجز استراتيجي + هيكل بنيوي

### 3.5 الكاتب (Draft-Writer)
- **:** 
- **الدور:** كتابة المسودة الأولى
- **الأدوات:** قراءة/كتابة ملفات، طرفية، رسائل
- **ينتج:** مسودة (draft)

### 3.6 المدقق (Editor-QA)
- **:** 
- **الدور:** التحقق من الادعاءات والمراجعات
- **الأدوات:** بحث ويب، استخراج، قراءة/كتابة ملفات، طرفية، رسائل
- **ينتج:** تقرير تحقق + طلب مراجعة

### 3.7 الناشر (Publisher)
- **:** 
- **الدور:** النشر في المنصات الخارجية
- **الأدوات:** قراءة/كتابة ملفات، طرفية، رسائل
- **ينتج:** قطعة منشورة + سجل نشر

### 3.8 المحلّل (Analytics)
- **:** 
- **الدور:** قياس الأداء وتقديم التغذية الراجعة
- **الأدوات:** قراءة/كتابة ملفات، طرفية، رسائل، بحث جلسات
- **ينتج:** تقرير أداء + تحديثات فرضيات

### 3.9 صانع البوتات (Bot-Maker)
- **:** 
- **الدور:** إنشاء وكلاء جدد وتعديل ملفات SOUL
- **الأدوات:** قراءة/كتابة ملفات، طرفية، رسائل، إدارة المهارات
- **ينتج:** SOUL جديد + سجل وكيل جديد

### 3.10 أومارشي (Omarchy)
- **:** 
- **الدور:** إدارة النظام وتخصيص سطح المكتب
- **الأدوات:** طرفية، قراءة/كتابة ملفات، رسائل، متصفح
- **ينتج:** إصلاح نظام + تحديث شادر

### 3.11 الراصد (Scout)
- **:** 
- **الدور:** مراقبة المصادر الخارجية باستمرار
- **الأدوات:** بحث ويب فقط
- **ينبه:** عند ظهور معلومات جديدة مطابقة للاهتمامات

---

## 4. خط الأنابيب (4 مستويات)

### المستوى 0 (Tier 0)
- لا وكلاء — قرار فوري من المنظّم
- للمهام البسيطة التي لا تحتاج بحثاً

### المستوى 1 (Tier 1)
- الباحث الشامل ← الناشر
- للمهام السريعة: ابحث وانشر

### المستوى 2 (Tier 2)
- الباحث ← الاستراتيجي ← الكاتب ← المدقق ← الناشر
- للمهام المتوسطة التي تحتاج استراتيجية وتدقيق

### المستوى 3 (Tier 3)
- المنظّم ← الباحث ← الغوّاص ← الاستراتيجي ← الكاتب ← المدقق ← الناشر ← المحلّل
- للمهام المعقدة مع تحليل الفيديو والتغذية الراجعة

---

## 5. بروتوكول التواصل

### 5.1 الظرف (Envelope)
كل رسالة بين الوكلاء تبدأ بظرف موحد:
```
[MISSION:<معرف المهمة>]
[FROM:<المرسل>]
[TO:<المستقبل>]
[STAGE:<مرحلة خط الأنابيب>]
[URGENCY:<منخفض|عادي|عالي|مانع>]
---PAYLOAD---
<الحمولة المهيكلة>
---END---
```

### 5.2 أنواع الحمولات (8 أنواع)
1. `handoff` — تسليم مرحلة
2. `blocker` — حاجة لقرار
3. `revision_request` — طلب مراجعة
4. `clarification_request` — طلب توضيح
5. `video_request` — طلب فيديو
6. `hypothesis_update` — تحديث فرضية
7. `escalation` — تصعيد
8. `registry_notice` — إشعار سجل
9. `proposal` — مقترح للبوابة البشرية
10. `dedup` — إزالة التكرار

### 5.3 ميزانية الرسائل
- 12 رسالة حد أقصى لكل مهمة
- بعد 12، كل التواصل يمر عبر المنظّم
- 8 دورات حد أقصى للغرف الجماعية

---

## 6. الكشف الديناميكي عن نافذة السياق

### 6.1 المشكلة
حجم العقود النظامية (~15,000 توكن) قد يتجاوز النافذة السياقية للنموذج المستخدم.

### 6.2 الحل
كشف تلقائي لحجم النافذة من اسم النموذج، ثم تحميل العقود بالأولوية:

| حجم النافذة | العقود المحمّلة | المستويات المدعومة |
|---|---|---|
| 8K | 1 (registry.json) | Tier 0 |
| 32K | 3 (registry + protocol + routing) | Tier 0-1 |
| 128K | 6 (+ quality-charter + ledger + evolution) | Tier 0-2 |
| 200K | 8 (+ README + status) | جميع المستويات |
| 1M+ | جميع العقود | جميع المستويات |

### 6.3 التخفيض التلقائي
إذا طُلب مستوى عالٍ والنافذة صغيرة، يُخفَّض المستوى تلقائياً مع إشعار.

---

## 7. ميثاق الجودة

### 7.1 سلم الأدلة
- **[V]** مُتحقق منه (فيديو + توقيت)
- **[M]** مُدعَّم بمصدر
- **[U]** غير مُتحقق منه
- **[H]** فرضية
- **[X]** غير قابل للتحقق

### 7.2 المواد الأساسية
- المادة الأولى: كل ادعاء يحتاج مصدراً
- المادة الثالثة: التحقق المستقل (لا يعتمد على المصدر وحده)
- المادة الخامسة: لا معلومات غير قابلة للتحقق في المنتج النهائي
- المادة العاشرة: الإصلاح الذاتي (محاولة واحدة قبل التصعيد)
- المادة الحادية عشرة: القبو المشترك (قراءة للجميع، كتابة للمنظّم والناشر)
- المادة الثانية عشرة: تقليم الأدوات (لا وكيل يستخدم أداة خارج قائمته)

---

## 8. حلقة التطور الذاتي

### 8.1 المراحل
1. **التشغيل** — تنفيذ خط الأنابيب
2. **الجمع** — دفتر المهام + التحليلات
3. **التحليل** — اكتشاف الأنماط
4. **التعديل** — تعديل العقود/SOULs

### 8.2 فئات التعديل
- **الفئة 1 (منخفضة):** تُطبَّق تلقائياً بعد 7 أيام
- **الفئة 2 (متوسطة):** تحتاج توقيع المنظّم
- **الفئة 3 (عالية):** تحتاج موافقة المستخدم

### 8.3 الفئة الفعّالة (E-class)
تغييرات منخفضة التكلدة وعالية القيمة:
- E1: إصلاح ذاتي (مكالمة LLM واحدة)
- E2: تخزين تلقائي (عند انخفاض النتيجة عن الحد)
- E3: إيقاف الغرفة الجماعية (0 مكالمات LLM)
- E4: حظر أداة غير مصرّح بها (0 مكالمات LLM)

---

## 9. التقييم

### 9.1 وقت التحميل
تحميل العقود التسعة: **0.8ms** (مرة واحدة عند بدء التشغيل)

### 9.2 التكلفة بالتوكنز
| المستوى | الوكلاء | توكنز العمل | الإجمالي مع النظام | نسبة الزيادة |
|---|---|---|---|---|
| Tier 0 | 1 | 500 | 17,211 | +305% |
| Tier 1 | 2 | 6,000 | 31,066 | +130% |
| Tier 2 | 5 | 37,500 | 87,633 | +56% |
| Tier 3 | 8 | 112,000 | 187,200 | +32% |

### 9.3 التحسينات المُنفَّذة
- **تقليم الأدوات:** كل وكيل يملك فقط ما يحتاجه
- **التحميل الكسول:** العقود تُحمَّل حسب حجم النافذة
- **إزالة التكرار:** بصمة URL + ادعاء
- **الإصلاح الذاتي:** محاولة واحدة قبل التصعيد
- **التخفيض التلقائي:** عند عدم كفاية النافذة

---

## 10. الخلابة

النظام الوزاري متعدد الوكلاء يحوّل مجموعة من الوكلاء المستقلين إلى نظام متكامل يُنتج معلومات عالية الجودة، مع ضمان التطور الذاتي المستمر والبشر في الحلول. البنية من ثلاث طبقات تضمن الاستقرار مع المرونة، وبروتوكول التواصل يضمن التنسيق، والكشف الديناميكي عن النافذة يضمن التوافق مع الأجهزة المختلفة.

---

## المراجع

1. Hermes Agent Documentation — nousresearch.com
2. Multi-Agent Systems: A Survey — arXiv:2309.00918
3. Constitutional AI — Anthropic, 2022
4. AutoGen: Enabling Next-Gen LLM Applications — Microsoft Research, 2023

</div>

---

# Cabinet-Office Multi-Agent System — Comprehensive Research Paper

## Abstract

This paper presents a Cabinet-Office Multi-Agent System built on the Hermes Agent framework. The system consists of 11 intelligent agents, each with a specific role and dedicated , working together across three architectural layers (constitutional, systemic, agentic) to produce high-quality information with guaranteed continuous self-evolution. The system features a unified communication protocol, dynamic context-window-based contract loading, a safe self-evolution loop, and a single human gate for critical decisions.

**Keywords:** Multi-Agent System, Artificial Intelligence, Knowledge Management, Self-Evolution, Human-in-the-Loop

---

## 1. Introduction

### 1.1 Problem Statement

Single AI systems suffer from fundamental limitations:
- **Lack of specialization:** One model cannot simultaneously be an expert in research, strategy, writing, editing, publishing, and analysis.
- **Lack of verification:** No independent mechanism exists to validate output quality.
- **Lack of memory:** Every session starts from zero.
- **Lack of evolution:** The system does not learn from its mistakes.

### 1.2 Solution

A cabinet-style multi-agent system where each "minister" is responsible for a specific domain, an "architect" manages inter-agent communication, and a "human gate" ensures the human remains in the loop.

---

## 2. Architectural Design (Three Layers)

### 2.1 Constitutional Layer (Frozen)
Five immutable principles:
1. **Match Before Act** — Understand the topic and required depth before searching.
2. **Labeled Truth** — Every claim traces to its source with timestamp.
3. **Confirm the Irreversible** — No destructive actions.
4. **Read Before Write** — Fetch and read transcripts before summarizing.
5. **Report Plainly** — Present findings clearly.

### 2.2 Systemic Layer (Modifiable via Evolution Protocol)
6 system contracts:
- `registry.json` — Agent registry
- `protocol.md` — Communication protocol
- `routing.yaml` — Routing rules
- `quality-charter.md` — Quality charter
- `ledger-schema.json` — Task ledger schema
- `evolution.md` — Evolution loop

### 2.3 Agentic Layer (SOUL Files)
11 SOUL files, each defining an agent's role, tools, and constraints.

---

## 3. The Eleven Agents

### 3.1 Architect (Orchestrator)
- **:** 
- **Role:** Sole coordinator managing inter-agent communication
- **Tools:** Web search, extraction, file read/write, terminal, messaging, sub-tasks, session search, cron
- **Permissions:** Opens new ledgers, routes between tiers, escalates to human

### 3.2 Omni-Researcher
- **:** 
- **Role:** Searches official sources, news, Twitter, Reddit
- **Tools:** Web search, extraction, file read, terminal, messaging
- **Produces:** Research dossier

### 3.3 Deep-Dive
- **:** 
- **Role:** YouTube research and personal experience analysis
- **Tools:** Web search, extraction, file read, terminal, messaging
- **Produces:** Video experience synthesis

### 3.4 Strategist
- **:** 
- **Role:** Converts research into plan and structure
- **Tools:** Web search, extraction, file read/write, messaging
- **Produces:** Strategy brief + structural blueprint

### 3.5 Draft-Writer
- **:** 
- **Role:** Writes first draft
- **Tools:** File read/write, terminal, messaging
- **Produces:** Draft

### 3.6 Editor-QA
- **:** 
- **Role:** Verifies claims and reviews
- **Tools:** Web search, extraction, file read/write, terminal, messaging
- **Produces:** Verification report + revision request

### 3.7 Publisher
- **:** 
- **Role:** Publishes to external platforms
- **Tools:** File read/write, terminal, messaging
- **Produces:** Published artifact + deployment log

### 3.8 Analytics
- **:** 
- **Role:** Measures performance and provides feedback
- **Tools:** File read/write, terminal, messaging, session search
- **Produces:** Performance report + hypothesis updates

### 3.9 Bot-Maker
- **:** 
- **Role:** Creates new agents and modifies SOULs
- **Tools:** File read/write, terminal, messaging, skill management
- **Produces:** New SOUL + new registry entry

### 3.10 Omarchy
- **:** 
- **Role:** System management and desktop customization
- **Tools:** Terminal, file read/write, messaging, browser
- **Produces:** System fix + shader update

### 3.11 Scout
- **:** 
- **Role:** Continuous external source monitoring
- **Tools:** Web search only
- **Alerts:** When new information matches configured interests

---

## 4. Pipeline Design (4 Tiers)

### Tier 0
- No agents — immediate decision from Architect
- Simple tasks requiring no research

### Tier 1
- Omni-Researcher → Publisher
- Fast tasks: search and publish

### Tier 2
- Researcher → Strategist → Writer → Editor → Publisher
- Medium tasks needing strategy and verification

### Tier 3
- Architect → Researcher → Deep-Dive → Strategist → Writer → Editor → Publisher → Analytics
- Complex tasks with video analysis and feedback

---

## 5. Communication Protocol

### 5.1 Envelope
Every inter-agent message begins with a unified envelope:
```
[MISSION:<mission_id>]
[FROM:<sender>]
[TO:<recipient>]
[STAGE:<pipeline_stage>]
[URGENCY:<low|normal|high|blocker>]
---PAYLOAD---
<structured_payload>
---END---
```

### 5.2 Payload Types (10 types)
1. `handoff` — Stage handoff
2. `blocker` — Needs decision
3. `revision_request` — Revision request
4. `clarification_request` — Clarification request
5. `video_request` — Video request
6. `hypothesis_update` — Hypothesis update
7. `escalation` — Escalation
8. `registry_notice` — Registry notice
9. `proposal` — Human gate proposal
10. `dedup` — Deduplication

### 5.3 Message Budget
- 12 messages maximum per mission
- After 12, all communication routes through Architect
- 8 turns maximum for group rooms

---

## 6. Dynamic Context Window Detection

### 6.1 Problem
System contracts (~15,000 tokens) may exceed the model's context window.

### 6.2 Solution
Automatic window size detection from model name, then priority-based contract loading:

| Window Size | Contracts Loaded | Supported Tiers |
|---|---|---|
| 8K | 1 (registry.json) | Tier 0 |
| 32K | 3 (registry + protocol + routing) | Tier 0-1 |
| 128K | 6 (+ quality-charter + ledger + evolution) | Tier 0-2 |
| 200K | 8 (+ README + status) | All tiers |
| 1M+ | All contracts | All tiers |

### 6.3 Auto-Downgrade
If a high tier is requested but the window is small, the tier is automatically downgraded with notification.

---

## 7. Quality Charter

### 7.1 Evidence Grading
- **[V]** Verified (video + timestamp)
- **[M]** Sourced
- **[U]** Unverified
- **[H]** Hypothesis
- **[X]** Unverifiable

### 7.2 Core Articles
- Article I: Every claim needs a source
- Article III: Independent verification
- Article V: No unverifiable claims in final output
- Article X: Self-healing (1 attempt before escalation)
- Article XI: Shared vault (read for all, write for Architect and Publisher)
- Article XII: Tool pruning (no agent uses tools outside its allowlist)

---

## 8. Evolution Loop

### 8.1 Stages
1. **Run** — Execute pipeline
2. **Collect** — Ledger + analytics
3. **Analyze** — Pattern detection
4. **Amend** — Modify contracts/SOULs

### 8.2 Amendment Classes
- **Class 1 (Low):** Auto-applied after 7 days
- **Class 2 (Medium):** Requires Architect sign-off
- **Class 3 (High):** Requires user approval

### 8.3 Effective Class (E-class)
Low-cost, high-value changes:
- E1: Self-repair (1 LLM call)
- E2: Auto-shelve (score below cutoff)
- E3: Group room pause (0 LLM calls)
- E4: Tool block (0 LLM calls)

---

## 9. Evaluation

### 9.1 Load Time
Loading all 9 contracts: **0.8ms** (once at startup)

### 9.2 Token Cost
| Tier | Agents | Work Tokens | Total with System | Overhead |
|---|---|---|---|---|
| Tier 0 | 1 | 500 | 17,211 | +305% |
| Tier 1 | 2 | 6,000 | 31,066 | +130% |
| Tier 2 | 5 | 37,500 | 87,633 | +56% |
| Tier 3 | 8 | 112,000 | 187,200 | +32% |

### 9.3 Implemented Optimizations
- **Tool pruning:** Each agent has only what it needs
- **Lazy loading:** Contracts loaded per window size
- **Deduplication:** URL + claim fingerprinting
- **Self-healing:** 1 attempt before escalation
- **Auto-downgrade:** When window is insufficient

---

## 10. Conclusion

The Cabinet-Office Multi-Agent System transforms a set of independent agents into an integrated system producing high-quality information, with guaranteed continuous self-evolution and the human in the loop. The three-layer architecture ensures stability with flexibility, the communication protocol ensures coordination, and dynamic context detection ensures compatibility across different devices.

---

## References

1. Hermes Agent Documentation — nousresearch.com
2. Multi-Agent Systems: A Survey — arXiv:2309.00918
3. Constitutional AI — Anthropic, 2022
4. AutoGen: Enabling Next-Gen LLM Applications — Microsoft Research, 2023