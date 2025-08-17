BEGIN TRANSACTION;
CREATE TABLE business_profiles (
	id INTEGER NOT NULL, 
	user_email TEXT NOT NULL, 
	business_name TEXT NOT NULL, 
	business_type TEXT NOT NULL, 
	industry TEXT NOT NULL, 
	monthly_revenue_range TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_email) REFERENCES users (email)
);
CREATE TABLE customers (
	id INTEGER NOT NULL, 
	user_email VARCHAR, 
	stripe_customer_id VARCHAR, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_email) REFERENCES users (email)
);
CREATE TABLE expense_categories (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	icon VARCHAR(50), 
	is_active BOOLEAN, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
);
INSERT INTO "expense_categories" VALUES(1,'Food & Dining','Restaurants, groceries, coffee',NULL,1,'2025-07-15 14:53:11');
INSERT INTO "expense_categories" VALUES(2,'Transportation','Gas, Uber, public transit',NULL,1,'2025-07-15 14:53:11');
INSERT INTO "expense_categories" VALUES(3,'Entertainment','Movies, concerts, hobbies',NULL,1,'2025-07-15 14:53:11');
INSERT INTO "expense_categories" VALUES(4,'Shopping','Clothing, electronics, home goods',NULL,1,'2025-07-15 14:53:11');
INSERT INTO "expense_categories" VALUES(5,'Utilities','Electricity, water, internet',NULL,1,'2025-07-15 14:53:11');
INSERT INTO "expense_categories" VALUES(6,'Office Supplies','Office equipment and supplies',NULL,1,'2025-07-15 17:51:38');
INSERT INTO "expense_categories" VALUES(7,'Meals & Entertainment','Food, drinks, and entertainment',NULL,1,'2025-07-15 17:51:38');
INSERT INTO "expense_categories" VALUES(8,'Software & Subscriptions','Software licenses and subscriptions',NULL,1,'2025-07-15 17:51:38');
INSERT INTO "expense_categories" VALUES(9,'Marketing & Advertising','Marketing and advertising expenses',NULL,1,'2025-07-15 17:51:38');
INSERT INTO "expense_categories" VALUES(10,'Shipping & Postage','Shipping and postage costs',NULL,1,'2025-07-15 17:51:38');
INSERT INTO "expense_categories" VALUES(11,'Professional Development','Training and education',NULL,1,'2025-07-15 17:51:38');
INSERT INTO "expense_categories" VALUES(12,'Travel','Business travel expenses',NULL,1,'2025-07-15 17:51:38');
INSERT INTO "expense_categories" VALUES(13,'Insurance','Insurance premiums',NULL,1,'2025-07-15 17:51:38');
INSERT INTO "expense_categories" VALUES(14,'Other','Miscellaneous expenses',NULL,1,'2025-07-15 17:51:38');
CREATE TABLE expenses (
	id INTEGER NOT NULL, 
	user_email VARCHAR(255) NOT NULL, 
	amount_cents INTEGER NOT NULL, 
	currency VARCHAR(3), 
	category_id INTEGER, 
	description TEXT NOT NULL, 
	vendor VARCHAR(200), 
	expense_date DATETIME NOT NULL, 
	payment_method VARCHAR(50), 
	receipt_url VARCHAR(500), 
	tags TEXT, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	confidence_score INTEGER, 
	auto_categorized INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_email) REFERENCES users (email), 
	FOREIGN KEY(category_id) REFERENCES expense_categories (id)
);
CREATE TABLE feedback (
	id INTEGER NOT NULL, 
	user_email VARCHAR NOT NULL, 
	category VARCHAR NOT NULL, 
	message VARCHAR NOT NULL, 
	rating INTEGER, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_email) REFERENCES users (email)
);
INSERT INTO "feedback" VALUES(1,'onboarding@test.com','onboarding','The onboarding process was very smooth and intuitive. I love the checklist feature!',5,'2025-07-15 17:43:11');
INSERT INTO "feedback" VALUES(2,'finaltest@example.com','testing','Final system test feedback - everything working great!',5,'2025-07-15 17:55:37');
CREATE TABLE password_reset_tokens (
	id INTEGER NOT NULL, 
	email VARCHAR NOT NULL, 
	token VARCHAR NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	expires_at DATETIME NOT NULL, 
	used VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(email) REFERENCES users (email), 
	UNIQUE (token)
);
INSERT INTO "password_reset_tokens" VALUES(1,'test2@example.com','xByI26_88FlrPcJXZOlV5luWfyiXzW_Aid1Nuk581YA','2025-07-15 17:05:05','2025-07-16 17:05:05.468289','true');
CREATE TABLE payments (
	id INTEGER NOT NULL, 
	user_email VARCHAR NOT NULL, 
	stripe_payment_intent_id VARCHAR, 
	amount FLOAT, 
	currency VARCHAR, 
	status VARCHAR, 
	description VARCHAR, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_email) REFERENCES users (email)
);
CREATE TABLE plaid_accounts (
	id INTEGER NOT NULL, 
	integration_id INTEGER NOT NULL, 
	plaid_account_id VARCHAR(255) NOT NULL, 
	account_name VARCHAR(255) NOT NULL, 
	account_type VARCHAR(100) NOT NULL, 
	account_subtype VARCHAR(100), 
	mask VARCHAR(10), 
	official_name VARCHAR(255), 
	verification_status VARCHAR(50), 
	current_balance FLOAT, 
	available_balance FLOAT, 
	iso_currency_code VARCHAR(10), 
	unofficial_currency_code VARCHAR(10), 
	last_sync_at DATETIME, 
	is_sync_enabled BOOLEAN, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(integration_id) REFERENCES plaid_integrations (id), 
	UNIQUE (plaid_account_id)
);
CREATE TABLE plaid_integrations (
	id INTEGER NOT NULL, 
	user_email VARCHAR NOT NULL, 
	access_token TEXT NOT NULL, 
	item_id VARCHAR(255) NOT NULL, 
	institution_id VARCHAR(255), 
	institution_name VARCHAR(255), 
	institution_logo VARCHAR(500), 
	institution_primary_color VARCHAR(7), 
	auto_sync BOOLEAN, 
	sync_frequency VARCHAR(50), 
	last_sync_at DATETIME, 
	last_sync_error TEXT, 
	total_transactions_synced INTEGER, 
	total_amount_synced FLOAT, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_email) REFERENCES users (email), 
	UNIQUE (item_id)
);
CREATE TABLE plaid_sync_history (
	id INTEGER NOT NULL, 
	integration_id INTEGER NOT NULL, 
	sync_type VARCHAR(50) NOT NULL, 
	account_id INTEGER, 
	plaid_transaction_id VARCHAR(255), 
	expense_id INTEGER, 
	sync_status VARCHAR(50) NOT NULL, 
	sync_duration INTEGER, 
	error_message TEXT, 
	amount FLOAT, 
	currency VARCHAR(10), 
	description TEXT, 
	category VARCHAR(100), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(integration_id) REFERENCES plaid_integrations (id), 
	FOREIGN KEY(account_id) REFERENCES plaid_accounts (id), 
	FOREIGN KEY(expense_id) REFERENCES expenses (id)
);
CREATE TABLE plaid_transactions (
	id INTEGER NOT NULL, 
	account_id INTEGER NOT NULL, 
	plaid_transaction_id VARCHAR(255) NOT NULL, 
	transaction_id VARCHAR(255), 
	amount FLOAT NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	date DATETIME NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	merchant_name VARCHAR(255), 
	payment_channel VARCHAR(50), 
	pending BOOLEAN, 
	address VARCHAR(500), 
	city VARCHAR(100), 
	state VARCHAR(100), 
	zip_code VARCHAR(20), 
	country VARCHAR(100), 
	lat FLOAT, 
	lon FLOAT, 
	category JSON, 
	category_id VARCHAR(255), 
	primary_category VARCHAR(255), 
	detailed_category VARCHAR(255), 
	check_number VARCHAR(50), 
	payment_meta JSON, 
	pending_transaction_id VARCHAR(255), 
	expense_id INTEGER, 
	is_synced_to_cora BOOLEAN, 
	auto_categorized BOOLEAN, 
	confidence_score FLOAT, 
	imported_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(account_id) REFERENCES plaid_accounts (id), 
	UNIQUE (plaid_transaction_id), 
	FOREIGN KEY(expense_id) REFERENCES expenses (id)
);
CREATE TABLE quickbooks_accounts (
	id INTEGER NOT NULL, 
	integration_id INTEGER NOT NULL, 
	quickbooks_id VARCHAR(50) NOT NULL, 
	account_name VARCHAR(200) NOT NULL, 
	account_type VARCHAR(50), 
	is_active BOOLEAN, 
	last_used_at DATETIME, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(integration_id) REFERENCES quickbooks_integrations (id)
);
CREATE TABLE quickbooks_integrations (
	id INTEGER NOT NULL, 
	user_email VARCHAR NOT NULL, 
	realm_id VARCHAR(50) NOT NULL, 
	company_name VARCHAR(200), 
	access_token TEXT NOT NULL, 
	refresh_token TEXT NOT NULL, 
	token_expires_at DATETIME NOT NULL, 
	is_active BOOLEAN, 
	auto_sync BOOLEAN, 
	sync_frequency VARCHAR(20), 
	category_mapping TEXT, 
	last_sync_at DATETIME, 
	total_expenses_synced INTEGER, 
	last_sync_error TEXT, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_email) REFERENCES users (email)
);
CREATE TABLE quickbooks_sync_history (
	id INTEGER NOT NULL, 
	integration_id INTEGER NOT NULL, 
	sync_type VARCHAR(20) NOT NULL, 
	expense_id INTEGER, 
	quickbooks_id VARCHAR(50), 
	quickbooks_status VARCHAR(20), 
	sync_duration INTEGER, 
	error_message TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(integration_id) REFERENCES quickbooks_integrations (id), 
	FOREIGN KEY(expense_id) REFERENCES expenses (id)
);
CREATE TABLE quickbooks_vendors (
	id INTEGER NOT NULL, 
	integration_id INTEGER NOT NULL, 
	quickbooks_id VARCHAR(50) NOT NULL, 
	vendor_name VARCHAR(200) NOT NULL, 
	display_name VARCHAR(200), 
	is_active BOOLEAN, 
	last_used_at DATETIME, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(integration_id) REFERENCES quickbooks_integrations (id)
);
CREATE TABLE stripe_integrations (
	id INTEGER NOT NULL, 
	user_email VARCHAR NOT NULL, 
	stripe_account_id VARCHAR(255) NOT NULL, 
	access_token TEXT NOT NULL, 
	refresh_token TEXT, 
	token_expires_at DATETIME, 
	business_name VARCHAR(255), 
	business_type VARCHAR(100), 
	country VARCHAR(10), 
	email VARCHAR(255), 
	auto_sync BOOLEAN, 
	sync_frequency VARCHAR(50), 
	last_sync_at DATETIME, 
	last_sync_error TEXT, 
	total_transactions_synced INTEGER, 
	total_amount_synced FLOAT, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_email) REFERENCES users (email), 
	UNIQUE (stripe_account_id)
);
CREATE TABLE stripe_sync_history (
	id INTEGER NOT NULL, 
	integration_id INTEGER NOT NULL, 
	sync_type VARCHAR(50) NOT NULL, 
	stripe_transaction_id VARCHAR(255), 
	expense_id INTEGER, 
	stripe_status VARCHAR(50) NOT NULL, 
	sync_duration INTEGER, 
	error_message TEXT, 
	amount FLOAT, 
	currency VARCHAR(10), 
	description TEXT, 
	category VARCHAR(100), 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(integration_id) REFERENCES stripe_integrations (id), 
	FOREIGN KEY(expense_id) REFERENCES expenses (id)
);
CREATE TABLE stripe_transactions (
	id INTEGER NOT NULL, 
	integration_id INTEGER NOT NULL, 
	stripe_transaction_id VARCHAR(255) NOT NULL, 
	stripe_charge_id VARCHAR(255), 
	stripe_payment_intent_id VARCHAR(255), 
	amount FLOAT NOT NULL, 
	currency VARCHAR(10) NOT NULL, 
	description TEXT, 
	receipt_url TEXT, 
	transaction_metadata TEXT, 
	created_at DATETIME NOT NULL, 
	expense_id INTEGER, 
	is_synced_to_cora BOOLEAN, 
	imported_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(integration_id) REFERENCES stripe_integrations (id), 
	UNIQUE (stripe_transaction_id), 
	FOREIGN KEY(expense_id) REFERENCES expenses (id)
);
CREATE TABLE subscriptions (
	id INTEGER NOT NULL, 
	user_email VARCHAR NOT NULL, 
	stripe_subscription_id VARCHAR, 
	plan_name VARCHAR, 
	status VARCHAR, 
	current_period_start DATETIME, 
	current_period_end DATETIME, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	canceled_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_email) REFERENCES users (email)
);
CREATE TABLE user_activity (
	id INTEGER NOT NULL, 
	user_email VARCHAR NOT NULL, 
	action VARCHAR NOT NULL, 
	details VARCHAR, 
	timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_email) REFERENCES users (email)
);
CREATE TABLE user_preferences (
	id INTEGER NOT NULL, 
	user_email VARCHAR NOT NULL, 
	"key" VARCHAR NOT NULL, 
	value VARCHAR, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_email) REFERENCES users (email)
);
CREATE TABLE users (
	email VARCHAR NOT NULL, 
	hashed_password VARCHAR NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	is_active VARCHAR, 
	PRIMARY KEY (email)
);
INSERT INTO "users" VALUES('test@example.com','$2b$12$jJHWvR18t8DPCmjKrQWgWuoJbSBOk3mIYNuhbcEuIrGZ1orPhPSJ6','2025-07-15 16:59:38','true');
INSERT INTO "users" VALUES('test2@example.com','$2b$12$sNZJjY154/d7zK0xwPk8iuyhm9ooFXDfdpgIbgIP4AffW9gPPbGwO','2025-07-15 17:01:26','true');
INSERT INTO "users" VALUES('onboarding@test.com','$2b$12$iXczKEaIx6bPJ3J3yJwzpuY4kL5RiJCn0C/wapKzCFEFz4EaT4z6i','2025-07-15 17:42:44','true');
INSERT INTO "users" VALUES('finaltest@example.com','$2b$12$WGC5nJ01VdEtXzYfTfKhVudiVY7XJ4yyqbuEAynU0JzrTzVxrvO4i','2025-07-15 17:55:28','true');
CREATE INDEX ix_users_email ON users (email);
CREATE INDEX ix_expense_categories_id ON expense_categories (id);
CREATE INDEX ix_expenses_id ON expenses (id);
CREATE INDEX ix_customers_id ON customers (id);
CREATE INDEX ix_subscriptions_id ON subscriptions (id);
CREATE INDEX ix_payments_id ON payments (id);
CREATE INDEX ix_business_profiles_id ON business_profiles (id);
CREATE INDEX ix_user_preferences_id ON user_preferences (id);
CREATE INDEX ix_password_reset_tokens_id ON password_reset_tokens (id);
CREATE INDEX ix_plaid_integrations_id ON plaid_integrations (id);
CREATE INDEX ix_stripe_integrations_id ON stripe_integrations (id);
CREATE INDEX ix_plaid_accounts_id ON plaid_accounts (id);
CREATE INDEX ix_stripe_sync_history_id ON stripe_sync_history (id);
CREATE INDEX ix_stripe_transactions_id ON stripe_transactions (id);
CREATE INDEX ix_plaid_transactions_id ON plaid_transactions (id);
CREATE INDEX ix_plaid_sync_history_id ON plaid_sync_history (id);
CREATE INDEX ix_feedback_id ON feedback (id);
CREATE INDEX ix_user_activity_user_email ON user_activity (user_email);
DELETE FROM "sqlite_sequence";
COMMIT;
