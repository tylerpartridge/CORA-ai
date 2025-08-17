#!/usr/bin/env python3
"""
Apply construction pivot database migration
This script adds job tracking fields and construction-specific categories
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://cora_user:cora_password@localhost:5432/cora_db')

def run_migration():
    """Run the construction pivot migration"""
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print("Connected to database successfully")
        
        # Check if job_name column already exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='expenses' AND column_name='job_name'
        """)
        
        if not cur.fetchone():
            print("Adding job tracking fields to expenses table...")
            
            # Add job fields to expenses
            cur.execute("""
                ALTER TABLE expenses 
                ADD COLUMN job_name VARCHAR(200),
                ADD COLUMN job_id VARCHAR(100)
            """)
            
            # Create indexes
            cur.execute("CREATE INDEX idx_expenses_job_name ON expenses(job_name) WHERE job_name IS NOT NULL")
            cur.execute("CREATE INDEX idx_expenses_job_id ON expenses(job_id) WHERE job_id IS NOT NULL")
            cur.execute("CREATE INDEX idx_expenses_user_job ON expenses(user_id, job_name) WHERE job_name IS NOT NULL")
            
            print("✓ Job tracking fields added")
        else:
            print("Job tracking fields already exist, skipping...")
        
        # Check if jobs table exists
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name='jobs' AND table_schema='public'
        """)
        
        if not cur.fetchone():
            print("Creating jobs table...")
            
            # Create jobs table
            cur.execute("""
                CREATE TABLE jobs (
                    id SERIAL PRIMARY KEY,
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    job_id VARCHAR(100) UNIQUE NOT NULL,
                    job_name VARCHAR(200) NOT NULL,
                    customer_name VARCHAR(200),
                    job_address TEXT,
                    start_date DATE,
                    end_date DATE,
                    quoted_amount NUMERIC(12,2),
                    status VARCHAR(50) DEFAULT 'active',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            # Create indexes
            cur.execute("CREATE INDEX idx_jobs_user_id ON jobs(user_id)")
            cur.execute("CREATE INDEX idx_jobs_status ON jobs(status)")
            cur.execute("CREATE INDEX idx_jobs_job_id ON jobs(job_id)")
            
            # Create job_notes table
            cur.execute("""
                CREATE TABLE job_notes (
                    id SERIAL PRIMARY KEY,
                    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    note_type VARCHAR(50),
                    note TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            cur.execute("CREATE INDEX idx_job_notes_job_id ON job_notes(job_id)")
            
            # Add trigger for updated_at
            cur.execute("""
                CREATE TRIGGER update_jobs_updated_at
                BEFORE UPDATE ON jobs
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
            """)
            
            print("✓ Jobs tables created")
        else:
            print("Jobs table already exists, skipping...")
        
        # Add construction categories
        print("Adding construction-specific expense categories...")
        
        # Check if categories already exist
        cur.execute("""
            SELECT COUNT(*) as count 
            FROM expense_categories 
            WHERE name LIKE 'Materials - %' OR name LIKE 'Labor - %'
        """)
        
        result = cur.fetchone()
        if result['count'] == 0:
            # Insert construction categories
            construction_categories = [
                # Materials
                ('Materials - Lumber', 'Wood, plywood, framing materials', 'fa-tree'),
                ('Materials - Electrical', 'Wiring, outlets, panels, fixtures', 'fa-bolt'),
                ('Materials - Plumbing', 'Pipes, fittings, fixtures, valves', 'fa-faucet'),
                ('Materials - Hardware', 'Fasteners, tools, small parts', 'fa-wrench'),
                ('Materials - Concrete', 'Concrete, rebar, forms', 'fa-cube'),
                ('Materials - Drywall', 'Sheetrock, mud, tape, texture', 'fa-square'),
                ('Materials - Roofing', 'Shingles, underlayment, flashing', 'fa-home'),
                ('Materials - Flooring', 'Tile, carpet, hardwood, vinyl', 'fa-border-all'),
                ('Materials - Paint', 'Paint, primer, supplies', 'fa-paint-roller'),
                ('Materials - Other', 'Miscellaneous construction materials', 'fa-box'),
                
                # Labor
                ('Labor - Crew', 'Your employees and helpers', 'fa-users'),
                ('Labor - Subcontractors', 'Hired specialty trades', 'fa-hard-hat'),
                ('Labor - Own Hours', 'Your own billable time', 'fa-user-clock'),
                
                # Equipment
                ('Equipment - Rental', 'Rented tools and machinery', 'fa-truck'),
                ('Equipment - Fuel', 'Gas and diesel for equipment', 'fa-gas-pump'),
                ('Equipment - Maintenance', 'Equipment repairs and service', 'fa-tools'),
                ('Equipment - Purchase', 'Bought tools and equipment', 'fa-shopping-cart'),
                
                # Other job costs
                ('Permits & Fees', 'Building permits, inspection fees', 'fa-file-alt'),
                ('Insurance - Job', 'Job-specific insurance costs', 'fa-shield-alt'),
                ('Waste & Disposal', 'Dumpster rental, dump fees', 'fa-trash'),
                ('Utilities - Job Site', 'Temporary power, water', 'fa-plug'),
                ('Safety Equipment', 'PPE, safety supplies', 'fa-hard-hat'),
                ('Office - Job Related', 'Plans, copies, job documentation', 'fa-folder')
            ]
            
            for name, description, icon in construction_categories:
                cur.execute("""
                    INSERT INTO expense_categories (name, description, icon, is_active)
                    VALUES (%s, %s, %s, true)
                """, (name, description, icon))
            
            print(f"✓ Added {len(construction_categories)} construction categories")
        else:
            print(f"Construction categories already exist ({result['count']} found), skipping...")
        
        # Create job profitability view
        print("Creating job profitability view...")
        
        cur.execute("""
            CREATE OR REPLACE VIEW job_profitability AS
            SELECT 
                j.id as job_id,
                j.user_id,
                j.job_name,
                j.customer_name,
                j.quoted_amount,
                j.status,
                COALESCE(SUM(e.amount_cents) / 100.0, 0) as total_costs,
                j.quoted_amount - COALESCE(SUM(e.amount_cents) / 100.0, 0) as profit,
                CASE 
                    WHEN j.quoted_amount > 0 
                    THEN ((j.quoted_amount - COALESCE(SUM(e.amount_cents) / 100.0, 0)) / j.quoted_amount * 100)
                    ELSE 0 
                END as profit_margin_percent
            FROM jobs j
            LEFT JOIN expenses e ON j.user_id = e.user_id AND j.job_name = e.job_name
            GROUP BY j.id, j.user_id, j.job_name, j.customer_name, j.quoted_amount, j.status
        """)
        
        print("✓ Job profitability view created")
        
        # Commit changes
        conn.commit()
        print("\n✅ Construction pivot migration completed successfully!")
        
        # Show summary
        cur.execute("SELECT COUNT(*) as count FROM expense_categories WHERE name LIKE 'Materials - %' OR name LIKE 'Labor - %' OR name LIKE 'Equipment - %'")
        category_count = cur.fetchone()['count']
        
        print(f"\nSummary:")
        print(f"- Job tracking fields added to expenses")
        print(f"- Jobs and job_notes tables created")
        print(f"- {category_count} construction categories available")
        print(f"- Job profitability view ready for use")
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🏗️ CORA Construction Pivot Migration")
    print("=" * 50)
    run_migration()