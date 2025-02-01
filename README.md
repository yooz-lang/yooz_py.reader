# Yooz reader


### معرفی

**yooz reader** یک ابزار قدرتمند برای پردازش ورودی‌های متنی، تجزیه قوانین و تولید پاسخ‌های تعاملی است. این ابزار برای پردازش الگوهای مکالمه، جایگزینی کلمات، مدیریت قوانین و موارد دیگر طراحی شده است.

---

### ویژگی‌ها
- پشتیبانی از دسته‌بندی‌های متنی (مانند ضمایر و افعال)
- تعریف و استفاده از قوانین برای مدیریت رفتار پاسخ‌ها
- امکان جایگزینی کلمات با استفاده از الگوها
- پشتیبانی از کلمات توقف (Stop Words)
- قابلیت مدیریت پاسخ‌های چند سطحی و شرطی
- امکان ذخیره متغیرها و استفاده از آن‌ها در پاسخ‌ها
- کاملاً قابل شخصی‌سازی و توسعه‌پذیر
- پشتیبانی از زبان‌های مختلف برای پردازش متون

---

### نحوه استفاده

#### 1. نصب
```bash
pip install yooz-reader
```

#### 2. نمونه کد
```python
from yooz-reader import YoozParser


parser = YoozParser()


input_text = '''
(
+سلام
-سلام
)

'''
parser.parse(input_text)

response = parser.get_response(input("Enter your Message:"))
print(response) 
```

#### 3. ساختار ورودی
- **الگوهای مکالمه:** `( + سوال کاربر - پاسخ های بات )`
- **تعاریف:** `#تعریف : مقدار.`
- **جایگزینی:** `{ کلمه1، کلمه2 } -> { جایگزین1، جایگزین2 }`
- **قوانین:** `{ [0.5] شرط > پاسخ }`
- **کلمات توقف:** `- { کلمه1، کلمه2 }`
- **متغیرها:** `=نام: مقدار`

---


### Introduction

**yooz reader** is a powerful tool for parsing textual inputs, managing rules, and generating interactive responses. It is designed for conversational patterns, word replacements, rule handling, and more.

---

### Features
- Support for text categories (e.g., pronouns and verbs)
- Define and apply rules to control response behavior
- Word replacement using patterns
- Stop words management
- Multi-level and conditional response handling
- Variable storage and usage in responses
- Fully customizable and extensible
- Multi-language support for text processing

---

### Usage

#### 1. Installation
```bash
pip install yooz-reader
```

#### 2. Example Code
```python
from yooz-reader import YoozParser

parser = YoozParser()

input_text = '''
(
+Hi
-Hi
)

'''
parser.parse(input_text)

response = parser.get_response(input("Enter your Message:"))
print(response) 
```

#### 3. Input Structure
- **Conversation patterns:** `( + User question - Bot responses )`
- **Definitions:** `#definition : value.`
- **Replacements:** `{ word1, word2 } -> { replacement1, replacement2 }`
- **Rules:** `{ [0.5] condition > response }`
- **Stop words:** `- { word1, word2 }`
- **Variables:** `=name: value`
