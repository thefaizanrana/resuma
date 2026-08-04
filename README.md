# Alfalah.app — Pakistan's Premium Job Platform

An enterprise-grade, Pakistan-localized job recruitment SaaS MVP. Django SSR with a
compiled C++17 matching engine (pybind11) for high-performance skill matching.

## Tech Stack

- Python 3.11 / Django 5.2 (project: `job_portal`, app: `core`)
- PostgreSQL via `psycopg2-binary`
- Tailwind CSS via django-tailwind 4.5 (standalone, no Node.js required)
- C++17 matching engine via pybind11 (`cpp_engine` → `job_matcher` module)

## Project Structure

```
.
├── job_portal/                    # Project configuration
├── core/                          # Primary application
│   ├── management/commands/seed_demo.py
│   ├── migrations/
│   ├── templatetags/currency_tags.py   # pkr_compact filter
│   ├── admin.py                   # All models with search/list config
│   ├── engine.py                  # C++ engine wrapper
│   ├── forms.py                   # Registration + profile + job posting forms
│   ├── models.py                  # User, CompanyProfile, CandidateProfile, JobPosting, Application
│   ├── urls.py
│   └── views.py                   # Business logic + C++ integration
├── cpp_engine/                    # C++17 matching engine
│   ├── matcher.cpp                # job_matcher module, calculate_match() 0-100
│   └── setup.py
├── templates/                     # Premium Tailwind UI
│   ├── auth/register.html         # Two-column auth card
│   ├── candidate/feed.html        # Match-score-ranked job feed
│   ├── candidate/dashboard.html   # Resume status + application tracking
│   ├── employer/create_job.html   # Job posting form
│   ├── employer/kanban.html       # ATS Kanban by match score
│   ├── profiles/setup.html        # Dual-purpose profile setup (PDF dropzone)
│   ├── base.html / home.html (split-pane) / job_detail.html
│   └── registration/login.html
├── theme/                         # django-tailwind theme app
├── static/ media/ scripts/ _legacy/
├── manage.py requirements.txt .env.example
```

## Data Model (Pakistan-localized)

- `User` — `is_employer`, `is_candidate`, `phone_number` (`+92XXXXXXXXXX` validated)
- `CompanyProfile` — company_name (indexed), `ntn_number`, description, logo, `is_verified`
- `CandidateProfile` — `cnic_number` (unique, `XXXXX-XXXXXXX-X`), city (PK choices), `resume_pdf` (PDF only), `raw_skills_text`
- `JobPosting` — title (indexed), description, city, `salary_min_pkr`/`salary_max_pkr`, job_type (Remote/Onsite/Hybrid), `is_active` (indexed) — composite index on `(is_active, -created_at)`
- `Application` — candidate, job, `match_score` (from C++ engine), `applied_at` (indexed), `unique_together`, index on `-match_score`

## C++ Matching Engine

`cpp_engine/matcher.cpp` exposes `job_matcher.calculate_match(candidate_skills, job_description)`
— an O(N) tokenizer with an unordered-set intersection, returning a rounded 0-100
percentage of job requirements covered by the candidate's skills.

```bash
cd cpp_engine && python setup.py build_ext --inplace
```

## Setup

```bash
pip install -r requirements.txt
service postgresql start
su postgres -c "psql -c \"CREATE USER job_portal WITH PASSWORD 'job_portal';\""
su postgres -c "psql -c \"CREATE DATABASE job_portal OWNER job_portal;\""
cp .env.example .env
python manage.py migrate
python manage.py tailwind install && python manage.py tailwind build
cd cpp_engine && python setup.py build_ext --inplace && cd ..
python manage.py seed_demo
python manage.py runserver
```

Demo accounts: `admin`/`admin12345`, `employer`/`employer12345`, `candidate`/`candidate12345`.

## Routes

| URL | View | Description |
|-----|------|-------------|
| `/` | `core:home` | Indeed-style split-pane search: scrollable feed (40%) + sticky detail with Instant Apply (60%); `select_related`, no N+1 |
| `/register/` | `core:register` | Registration with user type; auto-login |
| `/setup/` | `core:profile_setup` | Company or candidate profile setup (PDF/image upload) |
| `/employer/create-job/` | `core:create_job` | Employer job posting |
| `/employer/ats/` | `core:ats` | ATS Kanban (prefetch_related, bucketed by score) |
| `/candidate/feed/` | `core:job_feed` | Feed ranked by C++ match score |
| `/candidate/dashboard/` | `core:candidate_dashboard` | Resume status + applications |
| `/job/<pk>/` `/job/<pk>/apply/` | `core:job_detail` / `core:apply` | Job detail + POST-only apply |
| `/accounts/` | built-in | Login/logout |

## Env Variables

`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `POSTGRES_DB`,
`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`.
