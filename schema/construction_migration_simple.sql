-- Simple construction migration for direct execution
-- Run this in your PostgreSQL database

-- 1. Add job fields to expenses (if they don't exist)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='expenses' AND column_name='job_name') THEN
        ALTER TABLE expenses 
        ADD COLUMN job_name VARCHAR(200),
        ADD COLUMN job_id VARCHAR(100);
        
        CREATE INDEX idx_expenses_job_name ON expenses(job_name) WHERE job_name IS NOT NULL;
        CREATE INDEX idx_expenses_job_id ON expenses(job_id) WHERE job_id IS NOT NULL;
        CREATE INDEX idx_expenses_user_job ON expenses(user_id, job_name) WHERE job_name IS NOT NULL;
    END IF;
END $$;

-- 2. Create jobs table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS jobs (
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
);

CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_job_id ON jobs(job_id);

-- 3. Create job_notes table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS job_notes (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    note_type VARCHAR(50),
    note TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_job_notes_job_id ON job_notes(job_id);

-- 4. Add trigger for jobs updated_at (if it doesn't exist)
CREATE OR REPLACE TRIGGER update_jobs_updated_at
BEFORE UPDATE ON jobs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 5. Insert construction categories (only if they don't exist)
INSERT INTO expense_categories (name, description, icon, is_active)
SELECT * FROM (VALUES
    -- Materials
    ('Materials - Lumber', 'Wood, plywood, framing materials', 'fa-tree', true),
    ('Materials - Electrical', 'Wiring, outlets, panels, fixtures', 'fa-bolt', true),
    ('Materials - Plumbing', 'Pipes, fittings, fixtures, valves', 'fa-faucet', true),
    ('Materials - Hardware', 'Fasteners, tools, small parts', 'fa-wrench', true),
    ('Materials - Concrete', 'Concrete, rebar, forms', 'fa-cube', true),
    ('Materials - Drywall', 'Sheetrock, mud, tape, texture', 'fa-square', true),
    ('Materials - Roofing', 'Shingles, underlayment, flashing', 'fa-home', true),
    ('Materials - Flooring', 'Tile, carpet, hardwood, vinyl', 'fa-border-all', true),
    ('Materials - Paint', 'Paint, primer, supplies', 'fa-paint-roller', true),
    ('Materials - Other', 'Miscellaneous construction materials', 'fa-box', true),
    
    -- Labor
    ('Labor - Crew', 'Your employees and helpers', 'fa-users', true),
    ('Labor - Subcontractors', 'Hired specialty trades', 'fa-hard-hat', true),
    ('Labor - Own Hours', 'Your own billable time', 'fa-user-clock', true),
    
    -- Equipment
    ('Equipment - Rental', 'Rented tools and machinery', 'fa-truck', true),
    ('Equipment - Fuel', 'Gas and diesel for equipment', 'fa-gas-pump', true),
    ('Equipment - Maintenance', 'Equipment repairs and service', 'fa-tools', true),
    ('Equipment - Purchase', 'Bought tools and equipment', 'fa-shopping-cart', true),
    
    -- Other job costs
    ('Permits & Fees', 'Building permits, inspection fees', 'fa-file-alt', true),
    ('Insurance - Job', 'Job-specific insurance costs', 'fa-shield-alt', true),
    ('Waste & Disposal', 'Dumpster rental, dump fees', 'fa-trash', true),
    ('Utilities - Job Site', 'Temporary power, water', 'fa-plug', true),
    ('Safety Equipment', 'PPE, safety supplies', 'fa-hard-hat', true),
    ('Office - Job Related', 'Plans, copies, job documentation', 'fa-folder', true)
) AS v(name, description, icon, is_active)
WHERE NOT EXISTS (
    SELECT 1 FROM expense_categories ec WHERE ec.name = v.name
);

-- 6. Create job profitability view
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
GROUP BY j.id, j.user_id, j.job_name, j.customer_name, j.quoted_amount, j.status;

-- Show summary
SELECT 'Migration complete!' as status;
SELECT COUNT(*) as construction_categories FROM expense_categories 
WHERE name LIKE 'Materials - %' OR name LIKE 'Labor - %' OR name LIKE 'Equipment - %';