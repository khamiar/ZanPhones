# Zan Phones Project Overview

## Project Summary

Zan Phones is an in-development Django REST API for a multi-branch phone and accessories retail business. The repository currently contains only the backend; no application frontend source is present.

The system is designed to support:

- Product categories and product images
- TZS and USD pricing
- Branch locations
- Branch-specific inventory
- Customer records
- Customer-facing order creation
- Branch-scoped order management
- WhatsApp order links
- Staff roles and branch assignments
- USD-to-TZS currency configuration

The CORS settings allow the local frontend origins `http://localhost:5173` and `http://127.0.0.1:5173`, but the frontend application is not included in this repository.

## Technology

- Python
- Django 6.1
- Django REST Framework 3.18
- drf-spectacular and Swagger UI
- django-cors-headers
- Pillow
- PostgreSQL with `psycopg`
- Local virtual environment under `venv/`
- SQLite database file at `backend/db.sqlite3`

The project dependencies are recorded in `requirements.txt`.

## Repository Structure

- `backend/config/` - Django project settings and root URLs
- `backend/accounts/` - custom user model, user/branch association, and permission classes
- `backend/products/` - categories, products, and product images
- `backend/branches/` - branches and per-branch stock
- `backend/orders/` - customers, orders, order items, creation logic, and WhatsApp generation
- `backend/core/` - currency configuration
- `backend/media/products/` - uploaded product media
- `zan_phones_backup.sql` - PostgreSQL database backup
- `PROJECT_OVERVIEW.md` - this project overview

There are no dedicated frontend directories in the repository.

## Domain Model

### User and account roles

`accounts.User` extends Django's `AbstractUser`.

User fields include:

- The standard Django authentication fields
- `role`
- Optional `branch`

Roles:

- `SUPER_ADMIN`
- `ADMIN`
- `BRANCH_MANAGER`
- `STAFF`

Each user may be assigned to one branch through a nullable `PROTECT` foreign key. Super administrators and administrators are treated as system-wide users; branch managers and staff are expected to be branch-scoped.

The role migration is `accounts/migrations/0002_user_branch.py`.

### Products

`Category`

- Unique name
- Description
- Unique slug
- Creation timestamp

`Product`

- Belongs to one category
- Name
- Unique SKU
- Description
- TZS price
- USD price
- Active flag
- Creation and update timestamps

`ProductImage`

- Belongs to a product
- Uploaded image
- Optional primary-image flag
- Creation timestamp

Deleting a category or product is protected from cascading through existing related records.

### Branches and inventory

`Branch`

- Name
- City
- Address
- WhatsApp number
- Active flag
- Creation timestamp

`BranchStock`

- Branch
- Product
- Quantity
- Update timestamp

A database uniqueness constraint prevents duplicate stock rows for the same branch and product pair.

### Orders

`Customer`

- Full name
- Phone number
- Creation timestamp

`Order`

- UUID `order_number`
- Customer
- Branch
- Optional assigned `managed_by` user
- Currency (`TZS` or `USD`)
- Total amount
- Status
- Creation timestamp

Statuses:

- `PENDING`
- `CONFIRMED`
- `PROCESSING`
- `COMPLETED`
- `CANCELLED`

`OrderItem`

- Parent order
- Product
- Snapshot of product name
- Quantity
- Unit price
- Subtotal

Order items store price and name snapshots, so later catalog changes do not alter historical order lines.

### Currency

`CurrencyConfig` contains:

- Base currency
- USD-to-TZS exchange rate
- Last update timestamp

The default base currency is `TZS` and the default exchange rate is `2600`.

## REST API

The API is rooted at `/api/v1/`.

| Resource | Endpoint | Supported operations | Current access behavior |
|---|---|---|---|
| Products | `/api/v1/products/` | List, create | Public list/create by role permission |
| Products | `/api/v1/products/{id}/` | Retrieve, update, delete | Public retrieve; mutations restricted |
| Branches | `/api/v1/branches/` | List, retrieve | Read-only and public |
| Stock | `/api/v1/stock/` | List, retrieve | Read-only and public |
| Orders | `/api/v1/orders/` | List | Authenticated branch-scoped order access |
| Orders | `/api/v1/orders/create/` | Create | Public by DRF default permission |
| Orders | `/api/v1/orders/{id}/` | Retrieve | Authenticated branch-scoped order access |
| Currencies | `/api/v1/currencies/` | List, retrieve | Read-only and public |
| OpenAPI | `/api/schema/` | Retrieve | Public |
| Swagger UI | `/api/docs/` | Browse | Public |
| Django Admin | `/admin/` | Browser UI | Django staff authentication |
| Media | `/media/<path>` | Retrieve | Development media serving |

Product list filtering:

- `?category=<category_id>`
- `?search=<product_name>`

Only active products are returned by the product viewset.

Order list filtering:

- `?status=PENDING`
- `?status=CONFIRMED`
- `?status=PROCESSING`
- `?status=COMPLETED`
- `?status=CANCELLED`
- Pagination through `page` and `page_size`

Order list pagination uses ten rows per page, a configurable `page_size`, and a maximum page size of fifty.

## Implemented Features

### Catalog

- Category, product, and product-image models
- Public active-product listing
- Public product detail retrieval
- Product filtering by category
- Product name search
- Admin/manager-only product mutations
- Nested product-image serialization
- Category-name serialization

### Branches

- Active-branch listing
- Branch detail retrieval
- Branch stock listing
- Branch and product relationships
- Unique branch/product stock rows

### Orders

Customer-facing creation is implemented through `POST /api/v1/orders/create/`.

The request accepts:

- A customer object containing `name` and `phone`
- `branch_id`
- `currency`
- A non-empty list of `product_id` and `quantity` items

The create flow:

1. Validates customer text and required values
2. Validates that the branch exists and is active
3. Rejects duplicate products in one request
4. Locks branch stock records inside a database transaction
5. Checks product availability and active status
6. Checks each quantity against branch stock
7. Calculates totals using TZS or USD product prices
8. Creates or reuses a customer by phone number
9. Updates the existing customer's name
10. Creates the order and order items
11. Deducts stock quantities
12. Returns order details, including a generated WhatsApp link

The response includes:

- Numeric order ID
- UUID order number
- Branch name
- Branch WhatsApp number
- Generated WhatsApp click-to-chat link
- Customer name and phone
- Order items
- Currency
- Total
- Status
- Creation timestamp

The WhatsApp utility formats the order number, customer, products, quantities, unit prices, subtotals, and total into a click-to-chat message.

### Branch-scoped order access

The order list and detail views restrict branch employees to orders for their assigned branch.

- Superusers may access every branch
- `SUPER_ADMIN` users may access every branch
- `ADMIN` users may access every branch
- `BRANCH_MANAGER` users may access their own branch
- `STAFF` users may access their own branch

The order list supports status filtering and pagination.

## Permission Model

The custom account permissions are:

- `IsAdminOrManager`
- `IsStaffMember`
- `IsBranchOrderMember`
- `IsBranchOrderManager`

Current permission behavior:

- `IsAdminOrManager` allows superusers, `SUPER_ADMIN`, `ADMIN`, and `BRANCH_MANAGER`
- `IsStaffMember` adds `STAFF`
- `IsBranchOrderMember` allows system-wide super/admin access and requires a branch assignment for branch employees
- `IsBranchOrderManager` allows superusers, administrators, and branch managers; branch-manager object access is branch-scoped

Product mutations use `IsAdminOrManager`. Order list/detail views use `IsBranchOrderMember`.

## Django Administration

Django Admin registrations exist for:

- Custom users
- Categories
- Products
- Product images
- Branches
- Branch stock
- Customers
- Orders
- Order items
- Currency configuration

The custom user admin displays `role`, but the new `branch` field is not currently included in its custom fieldsets.

## Configuration

Current configuration includes:

- DRF automatic OpenAPI schema
- `AllowAny` as the default DRF permission
- Media URL and media root
- Django session/authentication middleware
- CORS for local frontend development
- PostgreSQL database configuration
- Custom `accounts.User` model
- Swagger and schema routes
- Development-only media URL handling

The project currently has:

- `DEBUG = True`
- Empty `ALLOWED_HOSTS`
- A hardcoded Django secret key
- Hardcoded PostgreSQL credentials

These settings are appropriate for local development but not production.

## Data and Migrations

Initial migrations exist for:

- Accounts
- Products
- Branches
- Orders
- Currency configuration

There is an additional `accounts` migration that adds the user-to-branch assignment.

Verified migration state: no unmigrated model changes are detected.

## Verification Status

The following Django commands were run successfully:

- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py test`

Results:

- Django system checks pass
- The migration state is complete
- Zero automated tests are currently discovered

All app test files contain only placeholders or comments.

## Current Working-Tree Summary

The current repository is active development code with working-tree changes, notably:

- User/branch association added
- Branch-aware permissions added
- Order list and detail APIs added
- Order creation expanded
- WhatsApp link generation added
- Product mutation behavior added
- Product and order Python bytecode/cache files appear in the working tree
- Product media and project overview files are currently untracked

The Python virtual environment and cache/media directories should not be treated as application source.

## Current Strengths

- Clear separation between Django applications
- Complete foundation for a multi-branch catalog
- Branch-stock uniqueness constraint
- Transactional order creation
- Database row locking for stock changes
- Historical order line snapshots
- Branch-scoped order permissions
- Public product and branch browsing
- OpenAPI and Swagger documentation
- Django Admin support

## Known Gaps and Risks

1. Automated tests are absent.
2. Authentication endpoints and JWT/session login APIs are not implemented in the visible project.
3. Order creation is public because no explicit authentication or staff permission is attached.
4. Order status updates and order management mutations are not implemented.
5. Customer phone numbers are not unique, although order creation reuses only the first/lookup result semantics and then updates its name.
6. The custom user admin does not expose the branch assignment field.
7. Branch stock and currency endpoints are read-only and public.
8. The account permissions assume that role strings and branch assignments are maintained consistently.
9. Branch stock may become inconsistent if inventory is modified outside the order transaction.
10. Secrets and database credentials are hardcoded.
11. Production hosts, HTTPS settings, and deployment environment configuration are absent.
12. There is no category mutation endpoint.
13. There is no product-image upload endpoint implemented separately; images are part of the product-image model and Django Admin.
14. The working tree contains cache, virtual-environment, database, media, and backup artifacts that should be excluded or managed explicitly in deployment.

## Recommended Next Steps

1. Add API tests for product filtering, permissions, order creation, insufficient stock, duplicate products, and branch isolation.
2. Add authentication endpoints and an authentication strategy.
3. Decide whether public orders should remain public or require staff authentication.
4. Add order status-management endpoints.
5. Add branch-manager and staff management API support.
6. Expose the user `branch` field in Django Admin.
7. Add uniqueness or normalization for customer phone numbers if one customer record per phone is required.
8. Restrict or filter stock and branch APIs according to business needs.
9. Move secrets and database settings to environment variables.
10. Configure production `ALLOWED_HOSTS`, `DEBUG`, HTTPS, static files, and media storage.
11. Add category and product-image administration/API workflows.
12. Add stock adjustment endpoints with audit or managed-by fields.
13. Remove or ignore generated virtual-environment, bytecode, database, and media artifacts from source control.

## Overall Architecture

Zan Phones follows a conventional Django application layout:

- `config` owns project-wide settings and routing
- `accounts` owns identity and business role/branch assignment
- `products` owns the catalog
- `branches` owns locations and local inventory
- `orders` owns customers and transactional sales
- `core` owns shared currency configuration

The backend is most mature in catalog models and branch-aware order code. The order creation and branch-security foundations are implemented, but authentication, status management, tests, and deployment hardening remain incomplete.
