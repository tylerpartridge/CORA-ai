-- Add contractor waitlist table
-- This migration adds support for beta signup and referral tracking

CREATE TABLE IF NOT EXISTS contractor_waitlist (
    id SERIAL PRIMARY KEY,
    
    -- Basic info
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    phone VARCHAR(20),
    company_name VARCHAR(200),
    
    -- Source tracking
    source VARCHAR(100), -- 'facebook_group', 'referral', 'website'
    source_details TEXT, -- Which FB group, who referred, etc.
    signup_keyword VARCHAR(50), -- 'TRUCK', 'BETA', etc.
    
    -- Business info
    business_type VARCHAR(100), -- 'general_contractor', 'plumber', 'electrician'
    team_size VARCHAR(50), -- '1-5', '6-10', '11-25', '25+'
    biggest_pain_point TEXT, -- What problem they want solved
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, invited, active, declined
    invitation_sent_at TIMESTAMPTZ,
    invitation_accepted_at TIMESTAMPTZ,
    
    -- Referral tracking
    referred_by_id INTEGER REFERENCES contractor_waitlist(id),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Notes
    admin_notes TEXT
);

-- Create indexes for performance
CREATE INDEX idx_waitlist_email ON contractor_waitlist(email);
CREATE INDEX idx_waitlist_status ON contractor_waitlist(status);
CREATE INDEX idx_waitlist_source ON contractor_waitlist(source);
CREATE INDEX idx_waitlist_referred_by ON contractor_waitlist(referred_by_id);
CREATE INDEX idx_waitlist_created_at ON contractor_waitlist(created_at);

-- Create trigger for updated_at
CREATE TRIGGER update_waitlist_updated_at
    BEFORE UPDATE ON contractor_waitlist
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add some initial test data (optional - remove for production)
-- INSERT INTO contractor_waitlist (name, email, source, business_type, biggest_pain_point)
-- VALUES 
-- ('John Doe', 'john@example.com', 'website', 'general_contractor', 'Tracking job costs is a nightmare'),
-- ('Jane Smith', 'jane@example.com', 'facebook_group', 'electrician', 'Need to see profit per job instantly');