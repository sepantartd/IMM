<div align="center">

```ascii
  _____ __  __ __M 
 |_   _|  \/  |  \/  |   Instagram Modular Manager
   | | | |\/| | |\/| |   Safety-First Automation Engine for Android & Linux
  _| |_| |  | | |  | |   
 |_____|_|  |_|_|  |_|   v1.0.0 Stable
```

# 🚀 IMM — Instagram Modular Manager

**موتور اتوماسیون ماژولار، ایمن و پیشرفته برای اینستاگرام با تمرکز بر حفظ امنیت اکانت، صف تأیید دستی و اجرای بهینه روی Termux و Linux**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Termux%20%7C%20Linux-green.svg?style=for-the-badge&logo=android&logoColor=white)](#)
[![License](https://img.shields.io/badge/license-MIT-purple.svg?style=for-the-badge)](#)
[![Build Status](https://img.shields.io/badge/tests-10%2F10%20passing-brightgreen.svg?style=for-the-badge&logo=github-actions&logoColor=white)](#)
[![Safety Guard](https://img.shields.io/badge/DRY__RUN-Supported-orange.svg?style=for-the-badge&logo=shield&logoColor=white)](#)

</div>

<br/>

## 📌 درباره پروژه

پروژه **IMM (Instagram Modular Manager)** یک ابزار حرفه‌ای، معماری‌محور و مستقل به زبان پایتون است که جهت مدیریت هوشمند و ساختاریافته تعاملات اینستاگرام (کشف ریلز، فیلترینگ چندلایه‌ای، تولید کامنت متنی، صف تأیید انسانی و کنترل دقیق نرخ ارسال) طراحی شده است. 

این پروژه با بهینه‌سازی‌های سنگین در لایه حافظه و پردازش، بدون کوچک‌ترین افت سرعت روی **ترموکس (Termux) اندروید** و انواع **سرورهای لینوکس (VPS)** قابل اجرا است.

---

## ✨ ویژگی‌های برجسته

* 🛡️ **حالت ایمن (DRY_RUN):** شبیه‌سازی کامل تمامی مراحل بدون ارسال واقعی کامنت یا ریسک مسدودی اکانت.
* 🚦 **صف تأیید تعاملی (Manual Approval Queue):** امکان بررسی، ویرایش یا رد کامنت‌های تولیدشده پیش از ارسال نهایی.
* ⚡ **کنترل نرخ هوشمند (Rate Limiter & Jitter):** اعمال تاخیرهای تصادفی انسان‌گونه و سقف مجاز ساعتی/روزانه.
* 🚫 **مدیریت لیست‌های سیاه/سفید (Blacklist/Whitelist):** مسدودسازی خودکار کلمات کلیدی، نام‌های کاربری و اسپمرها.
* 🔄 **زمان‌بندی پس‌زمینه (Daemon Mode):** اجرای دوره‌ای خودکار همراه با مدیریت سیگنال‌های توقف ایمن (`SIGINT`/`SIGTERM`).
* 🩺 **عیب‌یابی خودکار (Diagnostics & Health Check):** پایش سلامت دیتابیس، اتصال شبکه، فضای دیسک و تنظیمات سیستم.
* 🧹 **پشتیبان‌گیری و نگهداری (Backup & Vacuum):** ساخت بکاپ‌های تاریخ‌دار و فشرده‌سازی خودکار دیتابیس SQLite.
* 📊 **گزارش‌گیری پیشرفته (Analytics):** محاسبه دقیق نرخ موفقیت ارسال‌ها و خروجی گزارش‌های تحلیلی به فرمت JSON.

---

## 📂 ساختار پروژه

```text
IMM/
├── app/
│   ├── cli/             # دستورات و رابط خط فرمان (Click + Rich)
│   ├── database/        # مدیریت اتصالات و کوئری‌های SQLite
│   ├── instagram/       # کلاینت شبکه و ارتباط با API اینستاگرام
│   ├── models/          # مدل‌های داده اصلی (Reel, Comment)
│   ├── services/        # لایه منطق کسب‌وکار (کشف، فیلتر، ارسال، زمان‌بندی و...)
│   └── utils/           # ابزارهای کمکی (لاگر، تاخیرها، استثناها)
├── data/                # محل ذخیره دیتابیس و فایل‌های پشتیبان
├── tests/               # مجموعه تست‌های واحد و شبیه‌سازی شبکه
├── main.py              # نقطه ورود اصلی برنامه
├── requirements.txt     # نیازمندی‌ها و وابستگی‌های پایتون
└── README.md            # مستندات پروژه
```

---

## 📦 پیش‌نیازها و راهنمای نصب

### ۱. نصب در ترموکس (Termux - Android)

```bash
# بروزرسانی و نصب پیش‌نیازهای سیستم‌عامل
pkg update && pkg upgrade -y
pkg install python git clang make -y

# دریافت پروژه و ورود به پوشه
git clone [https://github.com/sepantartd/IMM.git](https://github.com/sepantartd/IMM.git)
cd IMM

# ساخت محیط مجازی و نصب وابستگی‌ها
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### ۲. نصب در لینوکس / VPS (Ubuntu/Debian)

```bash
# نصب پایتون و ابزارهای پایه
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y

# دریافت پروژه
git clone [https://github.com/sepantartd/IMM.git](https://github.com/sepantartd/IMM.git)
cd IMM

# ساخت محیط مجازی و نصب وابستگی‌ها
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ⚙️ پیکربندی (.env)

یک کپی از فایل نمونه `.env.example` با نام `.env` ایجاد کرده و متغیرهای خود را تنظیم کنید:

```bash
cp .env.example .env
```

نمونه محتوای فایل `.env`:

```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
INSTAGRAM_SESSION_ID=your_session_id

DRY_RUN=True
LOG_LEVEL=INFO
DATABASE_PATH=data/imm.db

MAX_COMMENTS_PER_HOUR=10
MAX_COMMENTS_PER_DAY=50
```

> ⚠️ **نکته مهم:** در حالت `DRY_RUN=True` هیچ کامنتی به صورت واقعی ارسال نمی‌شود. پس از اطمینان از صحت عملکرد، می‌توانید آن را برابر `False` قرار دهید.

---

## 💻 راهنمای کامل دستورات CLI

| دستور | توضیحات و کاربرد |
| :--- | :--- |
| `python main.py init` | راه‌اندازی و ساخت جداول پایگاه داده SQLite |
| `python main.py status` | مشاهده وضعیت کانفیگ، متغیرهای محیطی و اتصال دیتابیس |
| `python main.py discover -t target_user` | کشف ریلزهای هدف، اعمال فیلترها و افزودن به صف کامنت |
| `python main.py pending` | مشاهده جدول کامنت‌های منتظر تأیید |
| `python main.py approve --all` | تأیید یک‌جای تمام کامنت‌های صف |
| `python main.py approve --id 1` | تأیید یک کامنت مشخص با شناسه |
| `python main.py submit -l 5` | ارسال کامنت‌های تأییدشده با رعایت نرخ مجاز ارسال |
| `python main.py lists --add spam_user --type blacklist` | افزودن یک نام کاربری به لیست سیاه |
| `python main.py lists --show blacklist` | نمایش تمام ورودی‌های لیست سیاه |
| `python main.py daemon -t target_user -i 30` | اجرای پس‌زمینه (Daemon) و چرخه کشف/ارسال هر ۳۰ دقیقه |
| `python main.py health` | اجرای عیب‌یابی خودکار شبکه، دیتابیس و فضای دیسک |
| `python main.py report --export report.json` | مشاهده گزارش عملکرد و خروجی‌گرفتن به صورت JSON |
| `python main.py backup` | بهینه‌سازی دیتابیس (`VACUUM`) و تهیه بکاپ تاریخ‌دار |

---

## 🧪 اجرای تست‌ها

جهت اعتبارسنجی کلیه سرویس‌ها و شبیه‌سازی لایه شبکه بدون نیاز به اینترنت واقعی:

```bash
python -m unittest discover tests
```

---

## 📜 لایسنس

این پروژه تحت لایسنس **MIT** منتشر شده است. استفاده، تغییر و توسعه آن برای عموم آزاد است.

<div align="center">
  <sub>طراحی و پیاده‌سازی شده با ❤️ برای توسعه‌دهندگان پایتون و کاربران حرفه‌ای Termux</sub>
</div>
