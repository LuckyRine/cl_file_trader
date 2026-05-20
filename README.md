#  FileShare Pro

A full-stack file sharing platform built to demonstrate production-grade Django development skills. Users can upload files, share them via short links, protect them with passwords, set expiry dates, and search through public files.

> **Built as a portfolio project** to showcase backend architecture, REST API design, async task processing, and modern frontend integration.

---


## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Framework** | Django 5.x + Django REST Framework | Battle-tested, clean MVT architecture |
| **Database** | PostgreSQL | Relational integrity, full-text support |
| **Auth** | Custom `AbstractBaseUser` + SimpleJWT | Full control over auth flow, UUID PKs, email login |
| **Task Queue** | Celery + Redis | Async file processing, scheduled cleanup |
| **Cache / Broker** | Redis | Dual role — Celery broker + Django cache backend |
| **Search** | Elasticsearch 8.x + `django-elasticsearch-dsl` | Fuzzy full-text search with field boosting |
| **Frontend** | Bootstrap 5 + HTMX | SPA-like behaviour without a JS build pipeline |
| **Ad System** | Custom banner model + Celery tracking | Impression/click tracking, CTR analytics |
| **DevOps** | Docker + docker-compose | One-command local setup |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Django App                           │
│                                                             │
│  accounts │ files │ subscriptions │ search │ ads │ core    │
│                                                             │
│  DRF API ──────────────────────────────► JSON responses    │
│  Template Views ───────────────────────► HTML pages        │
└──────────┬──────────────────┬───────────────────────────────┘
           │                  │
           ▼                  ▼
        Redis              PostgreSQL
     (broker + cache)     (main DB)
           │
           ▼
        Celery Worker
     ┌────────────────┐
     │ process_file   │  MIME check → ES index → email
     │ cleanup_files  │  runs daily at 3am via Celery Beat
     │ record_ad_*    │  async impression/click tracking
     └────────────────┘
           │
           ▼
     Elasticsearch
     (fuzzy file search)
```

---

## Project Structure

```
cl_file_trader/
├── apps/
│   ├── accounts/          # Custom auth — email login, UUID PKs, JWT
│   ├── files/             # Upload, download, short links, expiry
│   ├── subscriptions/     # Plans (Free/Pro/Business), Stripe billing
│   ├── search/            # Elasticsearch integration
│   ├── ads/               # Banner system, impression/click tracking
│   └── core/              # Home page, shared utils, custom logging
├── config/
│   └── settings/
│       ├── base.py        # Shared settings
│       ├── development.py # Local overrides
│       └── production.py  # Production overrides (S3, SES, security headers)
├── templates/
│   ├── base.html          # Navbar, dark/light theme toggle, toast system
│   ├── home.html          # Landing page with live stats and quick upload
│   ├── upload.html        # Drag & drop upload with XHR progress bar
│   ├── download.html      # File download page with password unlock
│   ├── accounts/          # register.html, login.html, profile.html
│   ├── files/             # my_files.html — user dashboard
│   ├── subscriptions/     # pricing.html, checkout.html
│   ├── search/            # search.html
│   └── ads/               # banner.html — HTMX-loaded ad partial
├── logs/                  # Rotating log files (app.log, errors.log, celery.log)
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```


## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register/` | Register new user |
| `POST` | `/api/auth/token/` | Get JWT token pair |
| `POST` | `/api/auth/token/refresh/` | Refresh access token |
| `GET/PATCH` | `/api/auth/profile/` | Get or update profile |
| `POST` | `/api/files/upload/` | Upload a file |
| `GET` | `/api/files/<slug>/` | Get download URL |
| `DELETE` | `/api/files/<slug>/delete/` | Delete a file |
| `GET` | `/api/files/my/` | List user's files |
| `GET` | `/api/search/?q=report` | Search public files |
| `GET` | `/api/ads/serve/<placement>/` | Serve ad banner (HTMX) |
| `GET` | `/api/ads/click/<id>/` | Track ad click + redirect |
| `GET` | `/api/subs/plans/` | List subscription plans |
| `POST` | `/api/subs/webhook/` | Stripe webhook handler |



