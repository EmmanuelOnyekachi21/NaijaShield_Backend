# 🚀 Quick Start: Running Your Tests

## Step 1: Fix Database Permissions

Run the setup script:

```bash
cd /home/d3mxn/Documents/NaijaShield_Backend
./setup_test_db.sh
```

Or manually:

```bash
sudo -u postgres psql
```

Then in psql:

```sql
-- Replace 'your_db_user' and 'your_password' with your actual credentials
CREATE USER your_db_user WITH PASSWORD 'your_password' SUPERUSER;
CREATE DATABASE your_db_name OWNER your_db_user;
\c your_db_name
CREATE EXTENSION postgis;
\q
```

## Step 2: Activate Virtual Environment

```bash
source /home/d3mxn/Documents/notebooks/.venv312/bin/activate
```

## Step 3: Run Tests

```bash
cd /home/d3mxn/Documents/NaijaShield_Backend

# Run all 30 tests
python manage.py test apps.user

# Run with detailed output
python manage.py test apps.user --verbosity=2

# Run specific test class
python manage.py test apps.user.tests.ProfileCompletionTests

# Run with coverage
pip install coverage
coverage run --source='apps.user' manage.py test apps.user
coverage report
```

## Expected Output

```
Found 30 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..............................
----------------------------------------------------------------------
Ran 30 tests in 2.345s

OK
```

## 📚 What to Read Next

1. **TESTING_SUMMARY.md** - Overview of all 30 tests
2. **TESTING_GUIDE.md** - Complete tutorial on Django testing
3. **apps/user/tests.py** - The actual test code (heavily commented)

## 🎯 Your Mission

1. ✅ Get all 30 tests passing
2. ✅ Read through each test to understand what it does
3. ✅ Try modifying a test to make it fail (to see what happens)
4. ✅ Write 1 new test on your own
5. ✅ Run coverage to see what's tested

## 💡 Pro Tips

- Use `--keepdb` to speed up repeated test runs
- Use `--parallel` to run tests faster
- Use `-k test_name` to run tests matching a pattern
- Add `import pdb; pdb.set_trace()` to debug tests

## 🆘 Troubleshooting

**Problem**: `permission denied to create extension "postgis"`
**Solution**: Grant SUPERUSER to your database user (see Step 1)

**Problem**: `ModuleNotFoundError`
**Solution**: Activate virtual environment (see Step 2)

**Problem**: Tests fail with "connection refused"
**Solution**: Make sure PostgreSQL is running: `sudo service postgresql start`

---

**You've got this!** 🎉 Once the database is set up, all 30 tests will pass and you'll have a solid foundation for testing in Django.
